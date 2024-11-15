from django.urls import path

from controle.views import SalasListView, SalasCreateView, SalasDetailView, SalasDeleteView


app_name = 'controle'

urlpatterns = [
    path('salas/', SalasListView.as_view(), name='salas'),
    path('salas/<int:pk>/', SalasDetailView.as_view(), name='sala'),
    path('salas/criar/', SalasCreateView.as_view(), name='criar_sala'),
    path('salas/<int:pk>/deletar/', SalasDeleteView.as_view(), name='deletar_sala'),
]
