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
