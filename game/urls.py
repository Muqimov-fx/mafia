from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_game, name='create_game'),
    path('join/', views.join_game, name='join_game'),
    path('room/<str:room_code>/', views.game_room, name='game_room'),
    path('start/<str:room_code>/', views.start_game, name='start_game'),
    path('next/<str:room_code>/', views.next_phase, name='next_phase'),
    
    # --- MANA SHU QATOR SIZDA YETISHMAYAPTI ---
    path('action/<str:room_code>/', views.perform_action, name='perform_action'),
    # ------------------------------------------

    path('api/state/<str:room_code>/', views.game_state, name='game_state'),
]