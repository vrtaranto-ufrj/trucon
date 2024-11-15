from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm

class CadastroView(CreateView):
    template_name = 'cadastro.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Redireciona para a página de login após o cadastro
