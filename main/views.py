import json
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.contrib.auth import login, logout
from django.core.mail import send_mail
import uuid

from .models import ResetPasswordCode
from .forms import UserRegisterForm, UserEditForm, ResetPasswordConfirmForm
from .utils import ActionAccountMixin, create_random_sequence, send_password_reset_code


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


class RemoveAccountMixin(View, ActionAccountMixin):

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


class EditAccountMixin(View, ActionAccountMixin):

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
        except User.DoesNotExist:
            return render(
                request,
                'main/reset_password.html',
                context={'error': 'Пользователь с таким e-mail не обнаружен'}
            )

        _uuid = send_password_reset_code(user)
        return HttpResponseRedirect(reverse('main:reset_password_confirm', args=(_uuid,)))


class ResetPasswordConfirmView(View):

    def get(self, request, *args, **kwargs):
        form = ResetPasswordConfirmForm()
        return render(request, 'main/reset_password_confirm.html', context={'form': form})

    def post(self, request, *args, **kwargs):
        # Если пользователь залогинен, то редиректим на главную страницу
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse('main:index'))

        _uuid = kwargs['_uuid']

        try:
            reset_password_code = ResetPasswordCode.objects.get(uuid=_uuid)
        except ResetPasswordCode.DoesNotExist:
            return Http404()

        form = ResetPasswordConfirmForm(request.POST, valid_code=reset_password_code.code)
        if form.is_valid():
            user = reset_password_code.user
            user.set_password(form.cleaned_data['password1'])
            user.save()
            reset_password_code.delete()
            return HttpResponseRedirect(reverse('main:login'))

        return render(request, 'main/reset_password_confirm.html', context={'form': form})


def index(request):
    return render(request, 'main/index.html', context={})


def api_description(request):
    login_json = {
        'token': 'f1b8c722-d7dc-4784-9596-365902dc5920'
    }
    account_data_json = {
        'login': 'thanos',
        'email': 'th@nos.com',
        'first_name': 'Танос',
        'last_name': 'Завоеватель'
    }

    context = {
        'login_json': json.dumps(login_json, indent=2, ensure_ascii=False, sort_keys=False),
        'account_data_json': json.dumps(account_data_json, indent=2, ensure_ascii=False, sort_keys=False)
    }
    return render(request, 'main/api_description.html', context=context)


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})
