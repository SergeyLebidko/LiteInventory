from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.contrib.auth import login, logout
from django.core.mail import send_mail

from .forms import UserRegisterForm, UserEditForm
from .utils import ActionAccount


class Register(View):

    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'main/register.html', context={'form': form})

    def post(self, request):
        # Если пользователь залогинен - редиректим на главную страницу
        user = request.user
        if not user.is_anonymous:
            return HttpResponseRedirect(reverse('main:index'))

        form = UserRegisterForm(request.POST)
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


class RemoveAccount(View, ActionAccount):

    def get(self, request):
        return render(request, 'main/remove_account.html', context={'error': None})

    def post(self, request):
        user = request.user
        redirect = self.check_user(user)
        if redirect:
            return redirect

        password = request.POST['password']
        if request.user.check_password(password):
            logout(request)
            user.delete()
            return HttpResponseRedirect(reverse('main:remove_account_done'))

        return render(request, 'main/remove_account.html', context={'error': 'Неверный пароль'})


def remove_account_done(request):
    return render(request, 'main/remove_account_done.html', context={})


class EditAccount(View, ActionAccount):

    def get(self, request):
        form = UserEditForm(instance=request.user)
        return render(request, 'main/edit_account.html', context={'form': form})

    def post(self, request):
        user = request.user
        redirect = self.check_user(user)
        if redirect:
            return redirect

        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('main:index'))

        return render(request, 'main/edit_account.html', context={'form': form})


class ResetPasswordView(View):

    def get(self, request):
        return render(request, 'main/reset_password.html', context={'error': None})

    def post(self, request):
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return render(
                request,
                'main/reset_password.html',
                context={'error': 'Пользователь с таким e-mail не обнаружен'}
            )

        try:
            send_mail('Тестовое письмо', 'Если ты это читаешь, то все прошло хорошо', ['sergeyler@gmail.com'])
            print('Письмо отправлено нормально')
        except Exception as ex:
            print('При отправке писма произошла ошибка')
            print(ex)

        return HttpResponseRedirect(reverse('main:index'))


def index(request):
    return render(request, 'main/index.html', context={})


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})
