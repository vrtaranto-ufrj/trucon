import asyncio

from controle.models import (Carta, Jogador, Partida, PartidaModel, Rodada,
                             Sala, Time)
from django.db.models import QuerySet


class PartidaService:
    futures: dict[int,asyncio.Future] = {}
    @staticmethod
    def criar_partida(sala: Sala, jogador: Jogador) -> int:
        if sala.dono != jogador:
            raise PermissionError()
        
        partida = PartidaModel.objects.create()

        return partida.id


    def iniciar_partida(self, sala: Sala, partida_id: int):
        jogadores = list(sala.jogador_set.all())

        partida = Partida(jogadores, partida_id=partida_id, futures=self.futures)
        partida.escolher_primeiro_jogador()

        while partida.get_pontos_rodada(time=1) < 12 and partida.get_pontos_rodada(time=2) < 12:
            rodada = Rodada(partida.get_primeiro_jogador_rodada(), partida.time1, partida.time2)
            # partida.enviar_maos(rodada.get_maos_iniciais())
            # partida.enviar_estado(rodada)

            while rodada.get_pontos_subrodada(time=1) < 2 and rodada.get_pontos_subrodada(time=2) < 2:  # TEM QUE AJUSTAR PARA ACEITAR O CASO DE DOIS EMPATES (C++)
                for _ in range(4):
                    jogador_da_vez = rodada.get_jogador_da_vez()
                    # partida.enviar_vez(jogador_da_vez)
                    partida.enviar_estado(rodada)

                    carta_jogada = partida.sua_vez(jogadores[jogador_da_vez])  # Bloqueia aqui esperando a resposta

                    if not rodada.jogar_carta(carta_jogada, jogador_da_vez):
                        raise Exception('Jogador nao tem a carta')
                    
                    partida.enviar_carta_jogada(carta_jogada)
                    
                    rodada.proximo_jogador()

                
                time = rodada.dar_ponto_subrodada()
                rodada.reset_maior_carta()
                rodada.limpar_mesa()
                # partida.enviar_fim_subrodada(time)

            partida.dar_pontos_rodada(rodada.get_vencedor_rodada(), rodada.get_pontos_valendo())
            partida.enviar_fim_rodada(rodada.get_vencedor_rodada(), rodada.get_pontos_valendo())
            partida.proximo_primeiro_jogador_rodada()

        partida.enviar_vencedor()