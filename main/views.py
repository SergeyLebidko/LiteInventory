from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic.base import View
from django.contrib.auth import login, logout

from .forms import RegisterForm


class Register(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, 'main/register.html', context={'form': form})

    def post(self, request):
        # Если пользователь залогинен - редиректим на главную страницу
        user = request.user
        if not user.is_anonymous:
            return HttpResponseRedirect(reverse('main:index'))

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
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


def change_password_done(request):
    return render(request, 'main/change_password_done.html', context={})


class RemoveAccount(View):

    @staticmethod
    def check_staff(user):
        return user.is_superuser or user.is_staff

    def get(self, request):
        return render(request, 'main/remove_account.html', context={'error': None})

    def post(self, request):
        # Если нет залогинившегося пользователя - редиректим на страницу логина
        user = request.user
        if user.is_anonymous:
            return HttpResponseRedirect(reverse('main:login'))

        # Суперпользователя или персонал - редиректим на стандарную админку Django
        if self.check_staff(user):
            return HttpResponseRedirect(reverse('admin:index'))

        password = request.POST['password']
        if request.user.check_password(password):
            logout(request)
            user.delete()
            return HttpResponseRedirect(reverse('main:remove_account_done'))

        return render(request, 'main/remove_account.html', context={'error': 'Неверный пароль'})


def remove_account_done(request):
    return render(request, 'main/remove_account_done.html', context={})


def index(request):
    return render(request, 'main/index.html', context={})


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})
