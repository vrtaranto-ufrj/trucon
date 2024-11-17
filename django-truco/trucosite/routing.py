# routing.py
from django.urls import re_path
from api.consumers import SalaConsumer, PartidaConsumer

websocket_urlpatterns = [
    re_path(r'ws/salas/(?P<sala_id>\w+)/$', SalaConsumer.as_asgi()),
    re_path(r'ws/partidas/(?P<partida_id>\w+)/jogadores/(?P<jogador_id>\w+)/$', PartidaConsumer.as_asgi()),
]