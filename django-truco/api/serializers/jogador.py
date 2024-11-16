from rest_framework import serializers

from controle.models import Jogador

class JogadorSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar um Jogador.
    """

    usuario = serializers.StringRelatedField()

    class Meta:
        model = Jogador
        fields = '__all__'