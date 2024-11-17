import asyncio
from enum import Enum
from random import choice, shuffle
from typing import Optional

from api.serializers import (CartaSerializer, CartaViradaSerializer,
                             MaoSerializer)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from controle.models import Jogador
from django.db import models


class NAIPE(Enum):
    OUROS = 0
    ESPADAS = 1
    COPAS = 2
    PAUS = 3

class VALOR_CARTA(Enum):
    QUATRO = 0
    CINCO = 1
    SEIS = 2
    SETE = 3
    DAMA = 4
    VALETE = 5
    REI = 6
    AS = 7
    DOIS = 8
    TRES = 9
    OUROS = 10
    ESPADAS = 11
    COPAS = 12
    PAUS = 13

class Time:
    """
    Classe de um time.
    """

    def __init__(self, jogadores: list[Jogador]) -> None:
        self.jogadores = jogadores
        self.pontos = 0
        self.pontos_rodada = 0
        self.pontos_subrodada = 0

    def adicionar_pontos(self, pontos: int) -> bool:
        self.pontos += pontos
        if self.pontos >= 12:
            return True
        
    def adicionar_pontos_subrodada(self) -> None:
        self.pontos_subrodada += 1

    def __str__(self) -> str:
        return f'partida_{self.id}'
    

class Carta:
    """
    Classe de uma carta.
    """
    def __init__(self, valor: VALOR_CARTA, naipe: NAIPE) -> None:
        self.valor = valor
        self.valor_original = valor
        self.naipe = naipe
        self.virada = True

    def manilha(self) -> None:
        if self.naipe == NAIPE.OUROS:
            self.valor = VALOR_CARTA.COPAS
        elif self.naipe == NAIPE.COPAS:
            self.valor = VALOR_CARTA.OUROS
        elif self.naipe == NAIPE.ESPADAS:
            self.valor = VALOR_CARTA.PAUS
        elif self.naipe == NAIPE.PAUS:
            self.valor = VALOR_CARTA.ESPADAS

    def retirar_manilha(self) -> None:
        self.valor = self.valor_original

    def __str__(self) -> str:
        return f'{self.valor} de {self.naipe}'
    
class Mao:
    """
    Classe de uma mão.
    """
    def __init__(self) -> None:
        self.cartas: list[Carta] = []

    def receber_carta(self, carta: Carta) -> None:
        self.cartas.append(carta)

    def jogar_carta(self, carta: Carta) -> Carta:
        return self.cartas.remove(carta)

    
class Baralho:
    """
    Classe de um baralho.
    """
    def __init__(self) -> None:
        self.cartas: list[Carta] = []
        for valor in VALOR_CARTA:
            if valor == VALOR_CARTA.OUROS: break
            for naipe in NAIPE:
                self.cartas.append(Carta(valor, naipe))

        self.embaralhar()
        self.vira = self.__abrir_o_vira()
        self.__setar_valor_manilhas()


    def embaralhar(self) -> None:
        shuffle(self.cartas)

    def distribuir_todos(self, maos: list[Mao]) -> None:
        for i in range(3):  
            for mao in maos:
                mao.receber_carta(self.cartas.pop())

    def distribuir(self, maos: list[Mao]) -> None:
        for mao in maos:
            for i in range(3):
                mao.receber_carta(self.cartas.pop())

    def __abrir_o_vira(self) -> Carta:
        return self.cartas.pop()
    
    def __setar_valor_manilhas(self) -> None:
        if self.vira.valor == VALOR_CARTA.TRES:
            valor = VALOR_CARTA.QUATRO
        else:
            valor = VALOR_CARTA(self.vira.valor.value + 1)

        for carta in self.cartas:
            if carta.valor == valor:
                carta.manilha()
    

class Rodada:
    """
    Classe de uma rodada.
    """
    def __init__(self, comeca: int, time1: Time, time2: Time) -> None:
        self.valendo = 1
        self._vez = comeca
        self.baralho = Baralho()
        self._maos = [Mao(), Mao(), Mao(), Mao()]
        self.__distribuir_inicial()
        self._mesa: list[Carta] = []
        self.time1 = time1
        self.time2 = time2
        self._maior_carta: Optional[Carta] = None
        self._maior_jogador: Optional[int] = None

    def proximo_jogador(self) -> None:
        self._vez = (self._vez + 1) % 4

    def get_maos(self) -> list[Mao]:
        return self._maos
        
    def aumentar_valor(self) -> None:
        if self.valendo == 1:
            self.valendo += 2
        else:
            self.valendo += 3

    def jogar_carta(self, carta: Carta, jogador: int) -> bool:
        if carta not in self._maos[jogador].cartas:
            return False
        
        self._maos[jogador].jogar_carta(carta)  # Retira a carta da mao do jogador
        self._mesa.append(carta)  # Adiciona a carta à mesa

        if self._maior_carta is None or self._maior_carta.valor > self._maior_carta.valor:
            # Caso seja a primera carta da subrodada ou a carta seja a maior carta
            self._maior_carta = carta
            self._maior_jogador = jogador

    def dar_ponto_subrodada(self) -> Time:
        if self._maior_jogador % 2 == 0:
            self.time1.adicionar_pontos_subrodada()
            return self.time1
        else:
            self.time2.adicionar_pontos_subrodada()
            return self.time2

    def get_pontos_subrodada(self, time: int) -> int:
        if time == 1:
            return self.time1().pontos_subrodada
        else:
            return self.time2().pontos_subrodada
        
    def limpar_mesa(self) -> None:
        self._mesa.clear()

    def reset_maior_carta(self):
        self._maior_carta = None    
    
    def get_maos_iniciais(self) -> list[Mao]:
        return self._maos
    
    def get_jogador_da_vez(self) -> int:
        if self._maior_jogador is not None:
            self._vez = self._maior_jogador
            self._maior_jogador = None
            
        return self._vez
    
    def get_vencedor_rodada(self) -> Optional[Time]:
        if self.get_pontos_subrodada(1) > self.get_pontos_subrodada(2):
            return self.time1
        elif self.get_pontos_subrodada(1) < self.get_pontos_subrodada(2):
            return self.time2
        else:
            return None
        
    def get_pontos_valendo(self) -> int:
        return self.valendo
    
    def get_vira(self) -> Carta:
        return self.baralho.vira
    
    def __distribuir_inicial(self) -> None:
        self.baralho.distribuir(self._maos)
    

class PartidaModel(models.Model):
    vencedor1 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='vencedor1')
    vencedor2 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='vencedor2')
    perdedor1 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='perdedor1')
    perdedor2 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='perdedor2')


class Partida:
    """
    Classe de uma partida.
    """
    def __init__(self, jogadores: list[Jogador], partida_id: int, futures: dict[int,asyncio.Future]) -> None:
        self.jogadores = jogadores
        self.times = [Time(jogadores[::2]), Time(jogadores[1::2])]  # Divide os jogadores em dois times alternados
        self.partida_id = partida_id

    def time1(self) -> Time:
        return self.times[0]
    
    def time2(self) -> Time:
        return self.times[1]
    
    def dar_pontos_rodada(self, time: Optional[Time], pontos: int) -> None:
        if time is None:
            return
        
        time.adicionar_pontos(pontos)

    def get_pontos_rodada(self, time: int) -> int:
        return self.times[time-1].pontos_rodada

    def escolher_primeiro_jogador(self) -> None:
        self.vez = choice([0, 1, 2, 3])
    
    def get_primeiro_jogador_rodada(self) -> int:
        return self.vez
    
    def proximo_primeiro_jogador_rodada(self) -> None:
        self.vez = (self.vez + 1) % 4

    def get_mao_jogador(self, jogador: Jogador) -> list[Carta]:
        pass

    def enviar_maos(self, maos: list[Mao]) -> None:
        pass

    def enviar_vez(self, jogador_da_vez):
        pass

    def enviar_carta_jogada(self, carta):
        pass

    def enviar_fim_subrodada(self, time):
        pass

    def enviar_fim_rodada(self, time, pontos):
        pass

    def sua_vez(self, jogador: Jogador) -> Carta:
        pass

    def enviar_vencedor(self):
        pass

    def enviar_vira(self):
        pass

    def enviar_estado(self, rodada: Rodada) -> None:
        for e, jogador_enviar in enumerate(self.jogadores):
            response = {
                'maos': [
                    {
                        'jogador_pos': e,
                        'username': jogador.__str__(),
                        'cartas': [
                            CartaSerializer(carta).data
                            if jogador_enviar.id == jogador.id
                            else CartaViradaSerializer(carta).data
                            for carta in mao.cartas
                        ]
                    } for jogador, mao in zip(self.jogadores, rodada.get_maos())
                ],
                'vez': rodada.get_jogador_da_vez(),
                'vira': CartaSerializer(rodada.get_vira()).data,
                'pontos': [self.get_pontos_rodada(time=1), self.get_pontos_rodada(time=2)],
                'subpontos': [rodada.get_pontos_subrodada(time=1), rodada.get_pontos_subrodada(time=2)],
                'valendo': rodada.get_pontos_valendo(),
            }

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'jogador_{jogador_enviar.id}',
                {
                    'type': 'partida_message',
                    'estado': response,
                }
            )

            
# async def main():
#     jogadores = [Jogador('jogador1'), Jogador('jogador2'), Jogador('jogador3'), Jogador('jogador4')]
#     partida = Partida(1, jogadores)
#     partida.escolher_primeiro_jogador()

#     while partida.get_pontos_subrodada(time=1) < 12 and partida.get_pontos_subrodada(time=2) < 12:
#         rodada = Rodada(partida.get_primeiro_jogador_rodada())
#         partida.enviar_maos(rodada.get_maos_iniciais())
#         partida.enviar_vira(rodada.get_vira())

#         while rodada.get_pontos_subrodada(time=1) < 2 and rodada.get_pontos_subrodada(time=2) < 2:  # TEM QUE AJUSTAR PARA ACEITAR O CASO DE DOIS EMPATES (C++)
#             for _ in range(4):
#                 jogador_da_vez = rodada.get_jogador_da_vez()
#                 partida.enviar_vez(jogador_da_vez)

#                 carta_jogada = await partida.sua_vez(jogadores[jogador_da_vez])  # Bloqueia aqui esperando a resposta

#                 if rodada.jogar_carta(carta_jogada, jogador_da_vez):
#                     raise Exception('Jogador nao tem a carta')
                
#                 partida.enviar_carta_jogada(carta_jogada)
                
#                 rodada.proximo_jogador()

            
#             time = rodada.dar_ponto_subrodada()
#             rodada.reset_maior_carta()
#             rodada.limpar_mesa()
#             partida.enviar_fim_subrodada(time)

#         partida.dar_pontos_rodada(rodada.get_vencedor_rodada(), rodada.get_pontos_valendo())
#         partida.enviar_fim_rodada(rodada.get_vencedor_rodada(), rodada.get_pontos_valendo())
#         partida.proximo_primeiro_jogador_rodada()

#     partida.enviar_vencedor()