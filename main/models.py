from django.db import models
from django.contrib.auth.models import User


class ResetPasswordCode(models.Model):
    """Модель для хранения кодов сброса пароля"""
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    code = models.CharField(verbose_name='Код', max_length=10, unique=True)
    uuid = models.CharField(verbose_name='UUID', max_length=36, unique=True)

    def __str__(self):
        return f'Код для сброса пароля пользователя {self.user}'

    class Meta:
        verbose_name = 'Код сброса паролей'
        verbose_name_plural = 'Коды сброса паролей'


class Group(models.Model):
    """Модель для хранения групп объектов"""

    title = models.CharField(max_length=1024, verbose_name='Наименование')
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    group = models.ForeignKey(
        'self',
        verbose_name='Группа',
        related_name='child_groups',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
