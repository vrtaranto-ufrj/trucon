import json
from channels.generic.websocket import AsyncWebsocketConsumer

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
