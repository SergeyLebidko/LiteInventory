import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django.views.generic.base import View
from django.contrib.auth import login, logout

from .models import ResetPasswordCode, EquipmentCard, EquipmentType
from .forms import UserRegisterForm, UserEditForm, ResetPasswordConfirmForm
from .utils import ActionAccountMixin, send_password_reset_code, create_default_equipment_types, get_stat


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
            create_default_equipment_types(user)
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


class RemoveAccountView(View, ActionAccountMixin):

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


class EditAccountView(View, ActionAccountMixin):

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
        'username': 'thanos',
        'email': 'th@nos.com',
        'first_name': 'Танос',
        'last_name': 'Завоеватель'
    }
    reset_password_json = {
        'uuid': 'c0690dc0-0181-4471-95b4-5a6926901a56'
    }
    group_json = [
        {
            'id': 7,
            'title': 'Отдел контроля',
            'group': 1
        },
        {
            'id': 3,
            'title': 'Отдел закупок',
            'group': None
        },
        {
            'id': 6,
            'title': 'Отдел начисления ЗП',
            'group': 1
        }
    ]
    equipment_cards_json = [
        {
            'id': 2,
            'inv_number': '0002',
            'title': 'Futjitsu',
            'comment': 'Старый сервер',
            'worker': 'Админ',
            'purchase_date': '2021-05-12',
            'price': '60000.00',
            'group': 44,
            'equipment_type': 3
        },
        {
            'id': 3,
            'inv_number': '0001',
            'title': 'Cisco',
            'comment': 'Главный маршрутизатор офиса',
            'worker': 'Админ',
            'purchase_date': '2021-05-12',
            'price': '10000.25',
            'group': 44,
            'equipment_type': 7
        },
        {
            'id': 4,
            'inv_number': '0004',
            'title': '',
            'comment': 'Пока стоит в серверной. Нужна замена барабана',
            'worker': 'Секретарь',
            'purchase_date': None,
            'price': '1200.00',
            'group': 44,
            'equipment_type': 5
        }
    ]
    equipment_types_json = [
        {
            'id': 1,
            'title': 'Десктоп'
        },
        {
            'id': 7,
            'title': 'Коммутатор'
        },
        {
            'id': 5,
            'title': 'МФУ'
        }
    ]
    equipment_features_json = [
        {
            'id': 6,
            'name': 'LAN',
            'value': '2 x 1000Gbit',
            'equipment_card': 2
        },
        {
            'id': 5,
            'name': 'SSD',
            'value': '4 TB',
            'equipment_card': 2
        },
        {
            'id': 4,
            'name': 'Оперативная память',
            'value': '32 Gb',
            'equipment_card': 2
        },
        {
            'id': 7,
            'name': 'Операционная система',
            'value': 'Ubuntu Linux',
            'equipment_card': 2
        },
        {
            'id': 3,
            'name': 'Процессор',
            'value': 'Intel Core i9 11900',
            'equipment_card': 2
        }
    ]
    stat_json = {
        'total_count': 6,
        'total_price': 71500.25,
        'count_by_groups': [
            {
                'id': 16,
                'title': 'Пост охраны',
                'equipment_count': 3
            },
            {
                'id': 44,
                'title': 'Серверная',
                'equipment_count': 3
            }
        ],
        'price_by_groups': [
            {
                'id': 16,
                'title': 'Пост охраны',
                'equipment_price': 300.0
            },
            {
                'id': 44,
                'title': 'Серверная',
                'equipment_price': 71200.25
            }
        ],
        'count_by_types': [
            {
                'id': 1,
                'title': 'Десктоп',
                'equipment_count': 2
            },
            {
                'id': 2,
                'title': 'Ноутбук',
                'equipment_count': 1
            },
            {
                'id': 3,
                'title': 'Сервер',
                'equipment_count': 1
            },
            {
                'id': 5,
                'title': 'МФУ',
                'equipment_count': 1
            },
            {
                'id': 7,
                'title': 'Коммутатор',
                'equipment_count': 1
            }
        ],
        'price_by_types': [
            {
                'id': 1,
                'title': 'Десктоп',
                'equipment_price': 300.0
            },
            {
                'id': 3,
                'title': 'Сервер',
                'equipment_price': 60000.0
            },
            {
                'id': 5,
                'title': 'МФУ',
                'equipment_price': 1200.0
            },
            {
                'id': 7,
                'title': 'Коммутатор',
                'equipment_price': 10000.25
            }
        ]
    }

    context = {
        'login_json': json.dumps(login_json, indent=2, ensure_ascii=False, sort_keys=False),
        'account_data_json': json.dumps(account_data_json, indent=2, ensure_ascii=False, sort_keys=False),
        'reset_password_json': json.dumps(reset_password_json, indent=2, ensure_ascii=False, sort_keys=False),
        'group_json': json.dumps(group_json, indent=2, ensure_ascii=False, sort_keys=False),
        'equipment_cards_json': json.dumps(equipment_cards_json, indent=2, ensure_ascii=False, sort_keys=False),
        'equipment_types_json': json.dumps(equipment_types_json, indent=2, ensure_ascii=False, sort_keys=False),
        'equipment_features_json': json.dumps(equipment_features_json, indent=2, ensure_ascii=False, sort_keys=False),
        'stat_json': json.dumps(stat_json, indent=2, ensure_ascii=False, sort_keys=False),
    }
    return render(request, 'main/api_description.html', context=context)


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})


@login_required
def equipment_card(request, card_id):
    user = request.user
    try:
        card = EquipmentCard.objects.get(pk=card_id)
    except EquipmentCard.DoesNotExist:
        return Http404()

    if card.group.user != user:
        return Http404()

    types = EquipmentType.objects.filter(user=user)

    context = {
        'equipment_card': card,
        'equipment_types': types
    }
    return render(request, 'main/equipment_card.html', context=context)


@login_required
def equipment_types(request):
    user = request.user
    types = EquipmentType.objects.filter(user=user)

    context = {
        'equipment_types': types
    }
    return render(request, 'main/equipment_types.html', context=context)


@login_required
def stat(request):
    user = request.user
    context = get_stat(user)
    return render(request, 'main/stat.html', context=context)
