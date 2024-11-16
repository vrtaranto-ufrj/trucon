from rest_framework import serializers

from controle.models import Sala

class SalaSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar uma sala.
    """

    dono = serializers.StringRelatedField()
    jogador_set = serializers.StringRelatedField(many=True)

    class Meta:
        model = Sala
        fields = '__all__'

class SalasSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar uma lista de salas.
    """

    dono = serializers.StringRelatedField()
    jogador_set = serializers.StringRelatedField(many=True)

    class Meta:
        model = Sala
        fields = ['id', 'dono', 'jogador_set']
