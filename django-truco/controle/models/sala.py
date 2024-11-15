from django.db import models


class Sala(models.Model):
    """
    Modelo de uma sala de espera.
    """
    dono = models.ForeignKey('Jogador', on_delete=models.CASCADE, related_name='dono')
    criacao = models.DateTimeField(auto_now_add=True)
    senha = models.CharField(max_length=31, null=True, blank=True)

    def __str__(self) -> str:
        return f'Sala de {self.dono}'
