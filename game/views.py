from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Game, Player
import random
import json

def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

# --- SAHIFALAR ---

def index(request):
    return render(request, 'index.html')

def create_game(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        game = Game.objects.create()
        Player.objects.create(
            game=game, nickname=nickname,
            session_id=get_session_id(request), is_host=True
        )
        return redirect('game_room', room_code=game.room_code)
    return redirect('index')

def join_game(request):
    if request.method == 'POST':
        room_code = request.POST.get('room_code').upper()
        nickname = request.POST.get('nickname')
        game = get_object_or_404(Game, room_code=room_code)
        
        if game.is_started:
            return render(request, 'index.html', {'error': "O'yin allaqachon boshlangan!"})

        session_id = get_session_id(request)
        Player.objects.get_or_create(
            game=game, session_id=session_id,
            defaults={'nickname': nickname}
        )
        return redirect('game_room', room_code=room_code)
    return redirect('index')

def game_room(request, room_code):
    game = get_object_or_404(Game, room_code=room_code)
    session_id = get_session_id(request)
    try:
        current_player = Player.objects.get(game=game, session_id=session_id)
    except Player.DoesNotExist:
        return redirect('index')
    return render(request, 'room.html', {'game': game, 'player': current_player})

# --- O'YIN BOSHQARUVI (HOST) ---

def start_game(request, room_code):
    game = get_object_or_404(Game, room_code=room_code)
    session_id = get_session_id(request)
    host = Player.objects.get(game=game, session_id=session_id)
    
    if not host.is_host: return redirect('game_room', room_code=room_code)

    # 1. Reset (Qayta boshlash uchun tozalash)
    game.players.update(is_alive=True)
    game.mafia_target = None
    game.doctor_target = None
    game.morning_report = ""

    # 2. Rollarni taqsimlash
    players = list(game.players.all())
    count = len(players)
    roles = []
    if count > 0: roles.append('MAFIA')
    if count >= 3: roles.append('DOCTOR')
    while len(roles) < count: roles.append('CITIZEN')
    
    random.shuffle(roles)
    random.shuffle(players) # Odamlarni ham aralashtiramiz

    for p, r in zip(players, roles):
        p.role = r
        p.save()

    game.is_started = True
    game.phase = 'NIGHT'
    game.save()
    return redirect('game_room', room_code=room_code)

def next_phase(request, room_code):
    game = get_object_or_404(Game, room_code=room_code)
    session_id = get_session_id(request)
    if not Player.objects.filter(game=game, session_id=session_id, is_host=True).exists():
        return redirect('game_room', room_code=room_code)

    if game.phase == 'NIGHT':
        game.phase = 'MAFIA'
    elif game.phase == 'MAFIA':
        game.phase = 'DOCTOR'
    elif game.phase == 'DOCTOR':
        # --- TONGGI HISOB-KITOB ---
        game.phase = 'DAY'
        target_id = game.mafia_target
        save_id = game.doctor_target
        report = "Tun tinch o'tdi."

        if target_id:
            victim = Player.objects.get(id=target_id)
            if target_id == save_id:
                report = f"Mafia {victim.nickname}ga o'q uzdi, lekin Doktor uni qutqardi! ✅"
            else:
                victim.is_alive = False
                victim.save()
                report = f"Bu kecha {victim.nickname} shafqatsizlarcha o'ldirildi. 💀"
        else:
            report = "Mafia bu kecha hech kimni nishonga olmadi. Tinchlik! 🕊️"
        
        game.morning_report = report
        # Keyingi tun uchun tozalash
        game.mafia_target = None
        game.doctor_target = None

    elif game.phase == 'DAY':
        game.phase = 'NIGHT'
        game.morning_report = ""

    game.save()
    return redirect('game_room', room_code=room_code)

# --- API (JAVASCRIPT UCHUN) ---

@csrf_exempt
def perform_action(request, room_code):
    if request.method == 'POST':
        game = get_object_or_404(Game, room_code=room_code)
        session_id = get_session_id(request)
        
        # 1. Terminalga yozamiz (Xatolikni topish uchun)
        print(f"ACTION KELDI! Xona: {room_code}, Faza: {game.phase}")

        try:
            player = Player.objects.get(game=game, session_id=session_id)
            print(f"O'yinchi: {player.nickname}, Roli: {player.role}")
        except:
            print("O'yinchi topilmadi!")
            return JsonResponse({'status': 'error', 'msg': 'O\'yinchi topilmadi'})

        if not player.is_alive:
            return JsonResponse({'status': 'error', 'msg': 'O\'liklar gapirmaydi!'})

        # JSON ni o'qish
        try:
            data = json.loads(request.body)
            target_id = data.get('target_id')
            print(f"Nishon ID: {target_id}")
        except:
            print("JSON xato!")
            return JsonResponse({'status': 'error', 'msg': 'Ma\'lumot xato'})

        # Mantiqiy tekshiruv
        if game.phase == 'MAFIA' and player.role == 'MAFIA':
            game.mafia_target = target_id
            game.save()
            print(f"MAFIA OTDI: {target_id} saqlandi.") # <--- BU MUHIM
            return JsonResponse({'status': 'ok', 'msg': 'Nishonga olindi! 🔫'})
        
        if game.phase == 'DOCTOR' and player.role == 'DOCTOR':
            game.doctor_target = target_id
            game.save()
            print(f"DOKTOR DAVOLADI: {target_id} saqlandi.") # <--- BU MUHIM
            return JsonResponse({'status': 'ok', 'msg': 'Davolandi! 💉'})
            
        print("FAZA YOKI ROL MOS EMAS!") 
        return JsonResponse({'status': 'error', 'msg': f'Hozir {game.phase} vaqti, siz esa {player.role}siz!'})

    return JsonResponse({'status': 'error'})

def game_state(request, room_code):
    game = get_object_or_404(Game, room_code=room_code)
    players = list(game.players.all().values('id', 'nickname', 'is_host', 'is_alive'))
    
    session_id = get_session_id(request)
    try:
        me = Player.objects.get(game=game, session_id=session_id)
        my_role = me.get_role_display() if game.is_started else None
        role_code = me.role if game.is_started else None
        am_i_alive = me.is_alive
    except:
        my_role, role_code, am_i_alive = None, None, False

    return JsonResponse({
        'is_started': game.is_started,
        'players': players,
        'my_role': my_role,
        'role_code': role_code,
        'am_i_alive': am_i_alive,
        'phase': game.phase,
        'phase_display': game.get_phase_display(),
        'morning_report': game.morning_report
    })