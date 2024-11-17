from rest_framework import serializers

class CartaViradaSerializer(serializers.Serializer):
    """
    Serializer para retornar uma Carta.
    """

    virada = serializers.BooleanField()

class CartaSerializer(CartaViradaSerializer):
    """
    Serializer para retornar uma Carta.
    """
    

    virada = serializers.SerializerMethodField()
    valor = serializers.CharField(source='valor.name')
    valor_original = serializers.CharField(source='valor_original.name')
    naipe = serializers.CharField(source='naipe.name')

    def get_virada(self, obj):
        return False

class MaoSerializer(serializers.Serializer):
    """
    Serializer para retornar uma Mao.
    """

    cartas = CartaViradaSerializer(many=True, max_length=3)
