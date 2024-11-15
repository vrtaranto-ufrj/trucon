# views.py no app controle
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView

# Redireciona para 'salas' se o usuário estiver logado, caso contrário, para 'login'
class HomeRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return '/salas/'  # Redireciona para salas se estiver logado
        return '/login/'  # Redireciona para login se não estiver logado
