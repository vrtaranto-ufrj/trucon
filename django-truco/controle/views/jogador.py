from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

from controle.models import Jogador

class CadastroView(CreateView):
    template_name = 'cadastro.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Redireciona para a página de login após o cadastro

    def form_valid(self, form: UserCreationForm) -> HttpResponse:
        # Salva o usuário primeiro
        response = super().form_valid(form)
        # Cria o objeto Jogador associado ao usuário
        Jogador.objects.create(usuario=self.object)
        return response