from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import account_data, login, logout, register, edit_account, remove_account, change_password, \
    reset_password, reset_password_confirm, GroupViwSet, EquipmentCardViewSet, EquipmentTypeViewSet, \
    EquipmentFeatureViewSet, stat, update_equipment_types_list, update_equipment_features_list

app_name = 'api'

urlpatterns = [
    path('account_data/', account_data, name='account_data'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('edit_account/', edit_account, name='edit_account'),
    path('remove_account/', remove_account, name='remove_account'),
    path('change_password/', change_password, name='change_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('reset_password_confirm/<uuid:_uuid>/', reset_password_confirm, name='reset_password_confirm'),
    path('stat/', stat, name='stat'),
    path('update_equipment_types_list/', update_equipment_types_list, name='update_equipment_types_list'),
    path('update_equipment_features_list/', update_equipment_features_list, name='update_equipment_features_list')
]

router = SimpleRouter()
router.register('groups', GroupViwSet, basename='group')
router.register('equipment_cards', EquipmentCardViewSet, basename='equipment_card')
router.register('equipment_types', EquipmentTypeViewSet, basename='equipment_type')
router.register('equipment_features', EquipmentFeatureViewSet, basename='equipment_feature')
urlpatterns.extend(router.urls)
