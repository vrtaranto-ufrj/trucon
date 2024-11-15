from api.services import CacheService
from controle.models import Jogador

class JogadorService:
    def get_jogador(self, jogador_id: int) -> Jogador:
        return CacheService.get_cache(
            f'jogador_{jogador_id}',
            lambda: Jogador.objects.get(jogador_id)
        )