from django.urls import re_path
from .consumers import MafiaConsumer

websocket_urlpatterns = [
    re_path(r"ws/mafia/(?P<room_code>\w+)/$", MafiaConsumer.as_asgi()),
]