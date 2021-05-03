from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    token = models.CharField(verbose_name='Токен', max_length=36)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return f'Токен пользователя {self.user}'

    class Meta:
        verbose_name = 'Токен пользователя'
        verbose_name_plural = 'Токены пользователей'
