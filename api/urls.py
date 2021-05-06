from django.urls import path

from .views import account_data, login, logout, register, edit_account

app_name = 'api'

urlpatterns = [
    path('account_data/', account_data, name='account_data'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('edit_account/', edit_account, name='edit_account')
]
