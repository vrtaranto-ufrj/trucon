import asyncio
from typing import Optional

from api.consumers import SalaConsumer
from api.exceptions import SalaException
from api.serializers import SalaSerializer, SalasSerializer
from api.services import PartidaService, SalaService
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from controle.models import Jogador, Sala
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SalaApiView(APIView):
    """
    API View para devolver a lista das salas.
    """

    # permission_classes = [IsAuthenticated]

    def get(self, request: Request, sala_id: Optional[int] = None) -> Response:
        if sala_id:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Usuário não autenticado"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            jogador = request.user.jogador
            return self.__get_sala(sala_id, jogador)
        else:
            return self.__get_salas()
        
    def post(self, request: Request, sala_id: Optional[int] = None) -> Response:
        if not request.user.is_authenticated:
            return Response(
                {"error": "Usuário não autenticado"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        jogador = request.user.jogador
        senha_request = request.data.get('senha')

        if request.path.endswith('/entrar/') and sala_id:
            return self.__entrar_sala(sala_id, senha_request, jogador)
        elif request.path.endswith('/criarPartida/') and sala_id:
            return self.__criar_partida(sala_id, jogador)
        elif sala_id is None:
            return self.__criar_sala(senha_request, jogador)
        else:
            return Response(
                {"error": "Rota inválida"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, sala_id: int) -> Response:
        if not request.user.is_authenticated:
            return Response(
                {"error": "Usuário não autenticado"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        jogador = request.user.jogador

        return self.__deletar_sala(sala_id, jogador)

    def put(self, request: Request, sala_id: int) -> Response:
        if not request.user.is_authenticated:
            return Response(
                {"error": "Usuário não autenticado"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        jogador = request.user.jogador

        return self.__sair_sala(sala_id, jogador)

    def patch(self, request):
        sala = Sala.objects.get(id=87)
        
        # async def main():
        partida = PartidaService()
        partida.iniciar_partida(sala, 1)

        # # Run the async function in a new event loop
        # asyncio.run(main())

        return Response(status=status.HTTP_201_CREATED)

    def __get_sala(self, sala_id: int, jogador: Jogador) -> Response:
            try:
                sala = SalaService.get_sala(sala_id)
            except Sala.DoesNotExist:
                return Response(
                    {"error": "Sala não encontrada"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not SalaService.jogador_esta_na_sala(sala, jogador):
                if jogador.sala is not None:
                    return Response(
                        {"error": "Jogador já está em outra sala"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                return Response(
                    {"error": "Jogador não está na sala"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            sala_serializer = SalaSerializer(sala)
            
            return Response(sala_serializer.data, status=status.HTTP_200_OK)

    def __get_salas(self) -> Response:
        salas = SalaService.get_salas()
        salas_serializer = SalasSerializer(salas, many=True)
        return Response(salas_serializer.data, status=status.HTTP_200_OK)
    
    def __entrar_sala(self, sala_id: int, senha_request: str, jogador: Jogador) -> Response:
        try:
            sala = SalaService.get_sala(sala_id)
        except Sala.DoesNotExist:
            return Response(
                {"error": "Sala não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        sala_serializer = SalaSerializer(sala)

        if SalaService.jogador_esta_na_sala(sala, jogador):
            Response(sala_serializer.data, status=status.HTTP_200_OK)
        
        if sala.senha:
            if senha_request != sala.senha:
                return Response(
                    {"error": "Senha incorreta"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        try:
            SalaService.entrar_sala(sala, jogador)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'sala_{sala.id}',
                {
                    'type': 'sala_message',
                    'message': 'update'
                }
            )
        except SalaException as e:
            return Response(
                {"error": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(sala_serializer.data, status=status.HTTP_200_OK)

    def __criar_sala(self, senha_request: str, jogador: Jogador) -> Response:
        if jogador.sala:
            return Response(
                {"error": "Jogador já está em uma sala"},
                status=status.HTTP_400_BAD_REQUEST
            )

        sala = SalaService.criar_sala(jogador, senha_request)
        sala_serializer = SalaSerializer(sala)
        

        return Response(sala_serializer.data, status=status.HTTP_201_CREATED)

    def __deletar_sala(self, sala_id: int, jogador: Jogador) -> Response:
        try:
            sala = SalaService.get_sala(sala_id)
        except Sala.DoesNotExist:   
            return Response(
                {"error": "Sala não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'sala_{sala.id}',
            {
                'type': 'sala_message',
                'message': 'delete'
            }
        )
        
        try:
            SalaService.deletar_sala(sala, jogador)
        except PermissionError:
            return Response(
                {"error": "Você não tem permissão para deletar esta sala"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def __sair_sala(self, sala_id: int, jogador: Jogador) -> Response:
        try:
            sala = SalaService.get_sala(sala_id)
        except Sala.DoesNotExist:
            return Response(
                {"error": "Sala não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not SalaService.jogador_esta_na_sala(sala, jogador):
            return Response(
                {"error": "Jogador não está na sala"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            SalaService.sair_sala(sala, jogador)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'sala_{sala.id}',
                {
                    'type': 'sala_message',
                    'message': 'update'
                }
            )
        except PermissionError:
            return Response(
                {"error": "Você não tem permissão para sair desta sala"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def __criar_partida(self, sala_id: int, jogador: Jogador) -> Response:
        try:
            sala = SalaService.get_sala(sala_id)
        except Sala.DoesNotExist:
            return Response(
                {"error": "Sala não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            partida_id = PartidaService.criar_partida(sala, jogador)
        except PermissionError:
            return Response(
                {"error": "Apenas o dono pode iniciar a partida"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'sala_{sala.id}',
            {
                'type': 'sala_message',
                'message': 'start',
                'partida_id': partida_id,
            }
        )

        async def run_in_background():
            partida = PartidaService()
            await partida.iniciar_partida(sala, partida_id)

        loop = asyncio.get_running_loop()
        loop.create_task(run_in_background())

        return Response(status=status.HTTP_201_CREATED)
