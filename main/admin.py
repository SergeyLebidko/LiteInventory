from django.contrib import admin

from .models import ResetPasswordCode, Group


@admin.register(ResetPasswordCode)
class ResetPasswordCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'uuid']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'title']
