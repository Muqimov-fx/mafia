"""
URL configuration for mafia_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from game import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('create/', views.create_game, name='create_game'),
    path('join/', views.join_game, name='join_game'),
    path('room/<str:room_code>/', views.game_room, name='game_room'),
    path('start/<str:room_code>/', views.start_game, name='start_game'),
    path('api/state/<str:room_code>/', views.game_state, name='game_state'),
    path('next/<str:room_code>/', views.next_phase, name='next_phase'),
    path('action/<str:room_code>/', views.perform_action, name='perform_action'),
]