import json
from channels.generic.websocket import AsyncWebsocketConsumer
from controle.models import Jogador
from api.services import JogadorService, PartidaService
from asgiref.sync import sync_to_async

class SalaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sala_id: int = self.scope['url_route']['kwargs']['sala_id']
        self.nome_grupo_sala = f'sala_{self.sala_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.nome_grupo_sala,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.nome_grupo_sala,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.nome_grupo_sala,
            {
                'type': 'sala_message',
                'message': message.upper()
            }
        )

    async def sala_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

class PartidaConsumer(AsyncWebsocketConsumer):  # /ws/partida/<partida-id)>/jogador/<jogador-id>/
    def __init__(self, *args, **kwargs):
        self.jogadores_map: dict[str,Jogador] = {}
        super().__init__(*args, **kwargs)


    async def connect(self):
        self.partida_id: int = self.scope['url_route']['kwargs']['partida_id']
        self.jogador_id: int = self.scope['url_route']['kwargs']['jogador_id']
        self.nome_grupo_sala = f'jogador_{self.jogador_id}'

        self.jogadores_map[self.nome_grupo_sala] = await sync_to_async(
            JogadorService.get_jogador
        )(self.jogador_id)


            # async_to_sync(channel_layer.group_send)(
            #     f'jogador_{jogador_enviar.id}',
            #     {
            #         'type': 'sala_message',
            #         'estado': response,
            #     }
            # )
        # Join room group
        await self.channel_layer.group_add(
            self.nome_grupo_sala,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.nome_grupo_sala,
            self.channel_name
        )

        self.jogadores_map.pop(self.nome_grupo_sala, None)


    async def receive(self, text_data):
        data: dict = json.loads(text_data)
        message = data['message']
        if message == 'carta':
            carta = data.get('carta')
            # Verifique se há um Future esperando pela carta deste jogador
            if self.jogador_id in PartidaService().futures:
                future = PartidaService().futures[self.jogador_id]
                if not future.done():
                    future.set_result(carta)

        # Send message to room group
        # await self.channel_layer.group_send(
        #     self.nome_grupo_sala,
        #     {
        #         'type': 'sala_message',
        #         'message': message.upper()
        #     }
        # )

    async def partida_message(self, estado):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(estado))