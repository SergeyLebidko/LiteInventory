import string
import random
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse


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
