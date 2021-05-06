import random
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from main.utils import username_checker


def extract_user_data_from_request(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    email = request.data.get('email', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    return username, password, email, first_name, last_name


def check_user_data(username=None, password=None, email=None):
    if username is not None:
        error = username_checker(username)
        if error:
            return error

    if password is not None:
        try:
            validate_password(password)
        except ValidationError as ex:
            return ' '.join(ex.messages)

    if email is not None:
        try:
            EmailValidator('Некорректный email')(email)
        except ValidationError as ex:
            return ex.message

    if username is not None and email is not None:
        user_exists = User.objects.filter(Q(username=username) | Q(email=email)).exists()
        if user_exists:
            return 'Пользователь с таким логином или email уже существует'

    return None


def shuffle_string(source):
    if not source or len(source) == 1:
        return source

    source_as_list = list(source)
    result = source
    while result == source:
        random.shuffle(source_as_list)
        result = ''.join(source_as_list)
    return result
