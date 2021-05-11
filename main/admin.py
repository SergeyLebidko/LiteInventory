from django.contrib import admin

from .models import ResetPasswordCode, Group, EquipmentCard, EquipmentType, EquipmentFeature


@admin.register(ResetPasswordCode)
class ResetPasswordCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'uuid']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'title']
    list_display_links = ['title']


@admin.register(EquipmentCard)
class EquipmentCardAdmin(admin.ModelAdmin):
    list_display = ['equipment_user', 'group', 'equipment_type', 'title']
    list_display_links = ['equipment_type', 'title']

    def equipment_user(self, rec):
        return rec.group.user

    equipment_user.short_description = 'Пользователь'


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['user', 'title']
    list_display_links = ['title']


@admin.register(EquipmentFeature)
class EquipmentFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    list_display_links = ['name', 'value']
