from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import View
from django.contrib.auth import login

from .forms import RegisterForm


class Login(LoginView):
    template_name = 'main/login.html'


class Logout(LogoutView):
    next_page = reverse_lazy('main:index')


class Register(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, 'main/register.html', context={'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('main:inventory'))

        return render(request, 'main/register.html', context={'form': form})


def index(request):
    return render(request, 'main/index.html', context={})


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})
