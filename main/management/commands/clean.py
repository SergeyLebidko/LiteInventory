from django.core.management.base import BaseCommand

from api.models import Token
from main.models import ResetPasswordCode


class Command(BaseCommand):

    def handle(self, *args, **options):
        token_delete_count, _ = Token.objects.all().delete()
        code_delete_count, _ = ResetPasswordCode.objects.all().delete()
        print(f'Удалено токенов: {token_delete_count}')
        print(f'Удалено кодов сброса: {code_delete_count}')
