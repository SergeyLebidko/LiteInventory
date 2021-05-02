import string
import random
from django.http import HttpResponseRedirect
from django.urls import reverse


class ActionAccount:

    @staticmethod
    def check_user(user):
        if user.is_superuser or user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))

        if user.is_anonymous:
            return HttpResponseRedirect(reverse('main:login'))

        return None


def create_reset_code():
    code = [random.choice(string.ascii_letters + '0123456789') for _ in range(8)]
    random.shuffle(code)
    return ''.join(code)
