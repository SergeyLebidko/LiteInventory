from django.db import models
from django.contrib.auth.models import User


class ResetPasswordCode(models.Model):
    """Модель для хранения кодов сброса пароля"""
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    code = models.CharField(verbose_name='Код', max_length=10)
    uuid = models.CharField(verbose_name='UUID', max_length=36)

    def __str__(self):
        return f'Код для сброса пароля пользователя {self.user}'

    class Meta:
        verbose_name = 'Код сброса паролей'
        verbose_name_plural = 'Коды сброса паролей'
