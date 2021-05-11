# Generated by Django 3.2 on 2021-05-10 13:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0006_alter_group_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название характеристики')),
                ('value', models.CharField(max_length=1000, verbose_name='Значение характеристики')),
            ],
            options={
                'verbose_name': 'Характеристика оборудования',
                'verbose_name_plural': 'Характеристики оборудования',
            },
        ),
        migrations.CreateModel(
            name='EquipmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Наименование')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Тип оборудования',
                'verbose_name_plural': 'Типы оборудования',
            },
        ),
        migrations.CreateModel(
            name='EquipmentCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inv_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Инвентарный номер')),
                ('title', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Описание')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('worker', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Пользователь оборудования')),
                ('purchase_date', models.DateField(blank=True, null=True, verbose_name='Дата приобретения')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Стоимость')),
                ('equipment_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.equipmenttype', verbose_name='Тип оборудования')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.group', verbose_name='Группа')),
            ],
            options={
                'verbose_name': 'Учетная карточка',
                'verbose_name_plural': 'Учетные карточки',
            },
        ),
    ]