import uuid
import string
import random
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import ResetPasswordCode, Group, EquipmentCard, EquipmentType


class ActionAccountMixin:
    """Миксин добавляет редирект в зависимости от статуса пользователя (персонал, суперюзер или анонимный)"""

    @staticmethod
    def check_user(user):
        if user.is_superuser or user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))

        if user.is_anonymous:
            return HttpResponseRedirect(reverse('main:login'))

        return None


def username_checker(username):
    if not username:
        return 'Пустое имя пользователя недопустимо'
    for letter in username:
        if letter not in string.ascii_letters + '_0123456789':
            return 'Разрешены только английские буквы, цифры и знак подчеркивания'
    return None


class UsernameCheckMixin:
    """Миксин для форм, добавляющий кастомную проверку имени пользователя"""

    def clean_username(self):
        username = self.cleaned_data['username']
        error = username_checker(username)
        if error:
            raise ValidationError(error)
        return username


class EmailCheckMixin:
    """Миксин для форм, добавляющий кастомную проверку email"""

    def clean_email(self):
        email = self.cleaned_data['email']
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            raise ValidationError('Пользователь с таким email уже зарегистрирован')
        return email


def create_random_sequence(code_size=8):
    code = [random.choice(string.ascii_letters + '0123456789') for _ in range(code_size)]
    random.shuffle(code)
    return ''.join(code)


def send_password_reset_code(user):
    """Функция отправляет письмо с кодом сброса пароля. Возвращает необходимый для сброса uuid"""

    code_exist = _uuid_exist = True
    while code_exist or _uuid_exist:
        code = create_random_sequence()
        _uuid = str(uuid.uuid4())
        code_exist = ResetPasswordCode.objects.filter(code=code).exists()
        _uuid_exist = ResetPasswordCode.objects.filter(uuid=_uuid).exists()

    email_letter_template = settings.EMAIL_LETTER_TEMPLATE
    send_mail(
        settings.EMAIL_LETTER_HEADER,
        email_letter_template % code,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True
    )

    reset_password_code = ResetPasswordCode.objects.create(user=user, code=code, uuid=_uuid)
    return reset_password_code.uuid


def create_default_equipment_types(user):
    """Функция создает несколько типов оборудования, доступных для только что зарегистрировавшихся пользователей"""

    titles = ['Десктоп', 'Ноутбук', 'Сервер', 'Принтер', 'МФУ', 'Сканер', 'Коммутатор', 'Роутер']
    for title in titles:
        EquipmentType.objects.create(user=user, title=title)


def get_stat(user):
    """ Функция возвращает статистику по пользователю"""

    result = {}

    queryset = EquipmentCard.objects.filter(group__user=user)
    result['total_count'] = len(queryset)
    result['total_price'] = queryset.aggregate(total_price=Sum('price'))['total_price']

    result['count_by_groups'] = []
    queryset = Group.objects.annotate(equipment_count=Count('equipmentcard')).filter(equipment_count__gt=0)
    for group in queryset:
        result['count_by_groups'].append({
            'id': group.pk,
            'title': group.title,
            'equipment_count': group.equipment_count
        })

    return result
