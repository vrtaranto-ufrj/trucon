from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.models import User

class CadastrarSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar um novo usuário, garantindo que a senha seja criptografada.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True},
        }

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value
    
    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return value

    def create(self, validated_data: dict) -> User:
        password: str = validated_data.pop('password')
        user: User = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
