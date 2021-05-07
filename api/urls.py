from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import account_data, login, logout, register, edit_account, remove_account, change_password, \
    reset_password, reset_password_confirm, GroupViwSet

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
    path('reset_password_confirm/<uuid:_uuid>/', reset_password_confirm, name='reset_password_confirm')
]

router = SimpleRouter()
router.register('groups', GroupViwSet, basename='group')
urlpatterns.extend(router.urls)
