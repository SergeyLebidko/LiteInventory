from django.urls import path
from .views import Register, Login, Logout, ChangePassword, change_password_done, RemoveAccountView, \
    EditAccountView, remove_account_done, ResetPasswordView, ResetPasswordConfirmView, index, api_description, \
    inventory, equipment_card, equipment_types, stat

app_name = 'main'

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('change_password_done/', change_password_done, name='change_password_done'),
    path('remove_account/', RemoveAccountView.as_view(), name='remove_account'),
    path('remova_account_done/', remove_account_done, name='remove_account_done'),
    path('edit_account/', EditAccountView.as_view(), name='edit_account'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
    path('reset_password_confirm/<uuid:_uuid>/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('index/', index, name='index'),
    path('api_description/', api_description, name='api_description'),
    path('inventory/', inventory, name='inventory'),
    path('equipment_card/<int:card_id>/', equipment_card, name='equipment_card'),
    path('equipment_types/', equipment_types, name='equipment_types'),
    path('stat/', stat, name='stat')
]
