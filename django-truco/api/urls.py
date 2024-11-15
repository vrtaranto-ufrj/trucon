from api.views import CadastrarApiView, SalaApiView
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

app_name = 'api'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('cadastrar/', CadastrarApiView.as_view(), name='cadastrar'),
    path('salas/', SalaApiView.as_view(), name='salas'),
    path('salas/<int:sala_id>/', SalaApiView.as_view(), name='sala'),
    path('salas/criar/', SalaApiView.as_view(), name='criar_sala'),
    path('salas/<int:sala_id>/entrar/', SalaApiView.as_view(), name='entrar_sala'),
]
