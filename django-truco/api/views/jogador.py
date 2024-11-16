from typing import Optional

from api.serializers import JogadorSerializer
from api.services import JogadorService
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from controle.models import Jogador
from api.exceptions import SalaException

class JogadorApiView(APIView):
    """
    API View do Jogador.
    """

    # permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            return Response(
                {"error": "Usuário não autenticado"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        jogador = request.user.jogador
        jogador_serializer = JogadorSerializer(jogador)
        return Response(jogador_serializer.data, status=status.HTTP_200_OK)
