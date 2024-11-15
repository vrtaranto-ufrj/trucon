# views.py
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse

from controle.models import Sala, Jogador

class SalasListView(ListView):
    model = Sala
    template_name = 'salas.html'
    context_object_name = 'salas'


class SalasCreateView(CreateView):
    model = Sala
    template_name = 'sala_criar.html'
    fields = ['senha',]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        jogador: Jogador = request.user.jogador
        if jogador.sala is not None:
            return render(request, 'sala_erro.html', {'erro': 'Jogador já está em outra sala!', 'mensagem': 'Você já está em outra sala!'})
        
        return super().get(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponseRedirect:
        jogador: Jogador = self.request.user.jogador
        if jogador.sala is not None:
            return render(self.request, 'sala_erro.html', {'erro': 'Jogador já está em outra sala!', 'mensagem': 'Você já está em outra sala!'})
        
        form.instance.dono = self.request.user.jogador
        nova_sala = form.save()
        jogador.sala = nova_sala
        jogador.save()
        return redirect('controle:sala', pk=nova_sala.id)
    

class SalasDetailView(DetailView):
    model = Sala
    template_name = 'sala.html'
    context_object_name = 'sala'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        sala: Sala = self.get_object()
        jogador = request.user.jogador
        
        if sala.dono == jogador or jogador in sala.jogador_set.all():
            return super().get(request, *args, **kwargs)
        
        if jogador.sala is not None:
            return render(request, 'sala_erro.html', {'sala': sala, 'erro': 'Jogador já está em outra sala!', 'mensagem': 'Você já está em outra sala!'})

        if sala.jogador_set.count() == 4:
            return render(request, 'sala_erro.html', {'sala': sala, 'erro': 'Sala cheia!', 'mensagem': 'A sala está cheia!'})
        
        return render(request, 'sala_entrar.html', {'sala': sala})
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        sala: Sala = self.get_object()
        senha_digitada = request.POST.get('senha')

        if senha_digitada == sala.senha and sala.jogador_set.count() < 4:
            jogador: Jogador = request.user.jogador
            jogador.sala = sala
            jogador.save()
            return redirect('controle:sala', pk=sala.id)
        
        return render(request, 'sala_entrar.html', {'sala': sala, 'erro': 'Senha incorreta!'})
    
    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        jogador: Jogador = request.user.jogador
        jogador.sala = None
        jogador.save()
        return HttpResponse(status=204)


class SalasDeleteView(DeleteView):
    model = Sala
    template_name = 'sala_deletar.html'
    context_object_name = 'sala'

    def get_success_url(self) -> str:
        return reverse('controle:salas')
