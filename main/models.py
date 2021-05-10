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
        blank=True,
        default=None
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['title']


class EquipmentCard(models.Model):
    """Модель для хранения учетных карточек оборудования"""

    group = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE)
    inv_number = models.CharField(max_length=100, verbose_name='Инвентарный номер', null=True, blank=True)
    equipment_type = models.ForeignKey('EquipmentType', verbose_name='Тип оборудования', on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, verbose_name='Описание', null=True, blank=True)
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    worker = models.CharField(max_length=1000, verbose_name='Пользователь оборудования', null=True, blank=True)
    purchase_date = models.DateField(verbose_name='Дата приобретения', null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Стоимость', null=True, blank=True)

    class Meta:
        verbose_name = 'Учетная карточка'
        verbose_name_plural = 'Учетные карточки'


class EquipmentType(models.Model):
    """Модель для хранения типов оборудования (например, десктоп, ноутбук, сервер и т.д.)"""

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='Наименование')

    class Meta:
        verbose_name = 'Тип оборудования'
        verbose_name_plural = 'Типы оборудования'


class EquipmentFeature(models.Model):
    """Модель для хранения характеристик оборудования (например, модель процессора, объем памяти и т.д.)"""

    name = models.CharField(max_length=100, verbose_name='Название характеристики')
    value = models.CharField(max_length=1000, verbose_name='Значение характеристики')

    class Meta:
        verbose_name = 'Характеристика оборудования'
        verbose_name_plural = 'Характеристики оборудования'
