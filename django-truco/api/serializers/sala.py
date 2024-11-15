from rest_framework import serializers

from controle.models import Sala

class SalaSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar uma sala.
    """

    dono = serializers.StringRelatedField()

    class Meta:
        model = Sala
        fields = '__all__'

class SalasSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar uma lista de salas.
    """

    dono = serializers.StringRelatedField()

    class Meta:
        model = Sala
        fields = ['id', 'dono']