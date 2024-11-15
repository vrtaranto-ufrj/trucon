from django.db import models
from django.contrib.auth.models import User

from controle.models.sala import Sala

class Jogador(models.Model):
    """
    Modelo do jogador
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jogador')
    vitorias = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.usuario.username
    
    class Meta:
        verbose_name = 'Jogador'
        verbose_name_plural = 'Jogadores'
