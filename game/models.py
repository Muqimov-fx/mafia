from django.db import models
import random
import string

class Game(models.Model):
    room_code = models.CharField(max_length=6, unique=True)
    is_started = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    PHASE_CHOICES = [
        ('LOBBY', 'Kutish zali'),
        ('NIGHT', 'Tun 🌑'),
        ('MAFIA', 'Mafia Vaqti 🔫'),
        ('DOCTOR', 'Doktor Vaqti 💉'),
        ('DAY', 'Kun ☀️'),
    ]
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='LOBBY')
    
    # Harakatlar xotirasi
    mafia_target = models.IntegerField(null=True, blank=True)
    doctor_target = models.IntegerField(null=True, blank=True)
    morning_report = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.room_code

class Player(models.Model):
    ROLE_CHOICES = [
        ('MAFIA', 'Mafia 🔫'),
        ('DOCTOR', 'Doktor 💉'),
        ('CITIZEN', 'Tinch Aholi 🧔'),
    ]
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    nickname = models.CharField(max_length=50)
    session_id = models.CharField(max_length=100)
    is_host = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    is_alive = models.BooleanField(default=True) # Tiriklik statusi

    def __str__(self):
        return f"{self.nickname} ({self.game.room_code})"