from api.services import CacheService
from controle.models import Jogador

class JogadorService:
    @staticmethod
    def get_jogador(jogador_id: int) -> Jogador:
        return CacheService.get_cache(
            f'jogador_{jogador_id}',
            lambda: Jogador.objects.get(pk=jogador_id)
        )