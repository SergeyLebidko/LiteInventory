from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView


class Login(LoginView):
    template_name = 'main/login.html'


class Logout(LogoutView):
    next_page = reverse_lazy('main:index')


def index(request):
    return render(request, 'main/index.html', context={})


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})
