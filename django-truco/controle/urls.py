from django.urls import path
from django.contrib.auth.views import LoginView

from controle.views import CadastroView

app_name = 'controle'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('cadastrar/', CadastroView.as_view(), name='cadastrar'),
]
