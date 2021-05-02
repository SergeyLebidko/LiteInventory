from django.contrib import admin

from .models import ResetPasswordCode


@admin.register(ResetPasswordCode)
class ResetPasswordCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'uuid']
