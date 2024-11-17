# routing.py
from django.urls import re_path
from api.consumers import SalaConsumer

websocket_urlpatterns = [
    re_path(r'ws/salas/(?P<sala_id>\w+)/$', SalaConsumer.as_asgi()),
]