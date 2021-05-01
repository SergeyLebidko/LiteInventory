from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.views.generic.base import View
from django.contrib.auth import login

from .forms import RegisterForm


class Register(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, 'main/register.html', context={'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(request.POST['password'])
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('main:inventory'))

        return render(request, 'main/register.html', context={'form': form})


class Login(LoginView):
    template_name = 'main/login.html'


class Logout(LogoutView):
    next_page = reverse_lazy('main:index')


class ChangePassword(PasswordChangeView):
    template_name = 'main/change_password.html'
    success_url = reverse_lazy('main:change_password_done')


class ChangePasswordDone(PasswordChangeDoneView):
    template_name = 'main/change_password_done.html'


def index(request):
    return render(request, 'main/index.html', context={})


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})
