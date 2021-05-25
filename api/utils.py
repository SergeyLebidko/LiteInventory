import random
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password


def check_password(password):
    try:
        validate_password(password)
    except ValidationError as ex:
        return ' '.join(ex.messages)
    return None


def check_email(email):
    try:
        EmailValidator('Некорректный email')(email)
    except ValidationError as ex:
        return ex.message
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
