from api.exceptions import (JogadorJaEmOutraSalaException,
                            JogadorJaNaSalaException, SalaCheiaException)
from api.services import JogadorService
from controle.models import Sala, Jogador
from django.db.models import QuerySet


class SalaService:
    @staticmethod
    def get_salas() -> QuerySet[Sala]:
        return Sala.objects.all()

    @staticmethod
    def get_sala(sala_id: int) -> Sala:
        return Sala.objects.get(pk=sala_id)

    @staticmethod
    def criar_sala(dono: Jogador, senha: str = None) -> Sala:
        sala = Sala.objects.create(dono=dono, senha=senha)
        dono.sala = sala
        dono.save()
        return sala
    
    @staticmethod
    def deletar_sala(sala: Sala, jogador: Jogador) -> None:
        if sala.dono != jogador:
            raise PermissionError()
        
        jogador.sala = None        
        sala.delete()

    @staticmethod
    def entrar_sala(sala: Sala, jogador: Jogador) -> Sala:
        if sala.jogador_set.count() == 4:
            raise SalaCheiaException()
        if jogador in sala.jogador_set.all():
            raise JogadorJaNaSalaException()
        
        if jogador.sala is not None:
            raise JogadorJaEmOutraSalaException()

        sala.jogador_set.add(jogador)
        return sala
    
    @staticmethod
    def sair_sala(sala: Sala, jogador: Jogador) -> Sala:
        if sala.dono == jogador:
            raise PermissionError()
        
        sala.jogador_set.remove(jogador)
        return sala
    
    @staticmethod
    def jogador_esta_na_sala(sala: Sala, jogador: Jogador) -> bool:
        return jogador in sala.jogador_set.all()
