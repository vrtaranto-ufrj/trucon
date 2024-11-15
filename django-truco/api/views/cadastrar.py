from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
from api.serializers import CadastrarSerializer

class CadastrarApiView(APIView):
    """
    API View para registrar um novo usuário.
    """

    # permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        register_serializer = CadastrarSerializer(data=request.data)
        
        if register_serializer.is_valid():
            register_serializer.save()  # Cria o usuário
            return Response(
                {"message": "Usuário registrado com sucesso!"},
                status=status.HTTP_201_CREATED
            )
        
        # Se os dados não forem válidos, retorna os erros de validação
        return Response(
            {"error": "Erro ao registrar o usuário", "details": register_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
