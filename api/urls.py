from django.urls import path

from .views import login, logout, register, edit_account

app_name = 'api'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('edit_account/', edit_account, name='edit_account')
]
