# Generated by Django 3.2 on 2021-05-04 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='token',
            field=models.CharField(max_length=36, unique=True, verbose_name='Токен'),
        ),
    ]
