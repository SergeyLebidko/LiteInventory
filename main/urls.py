from django.urls import path
from .views import Register, Login, Logout, ChangePassword, change_password_done, RemoveAccount, remove_account_done, \
    index, inventory

app_name = 'main'

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('change_password_done/', change_password_done, name='change_password_done'),
    path('remove_account/', RemoveAccount.as_view(), name='remove_account'),
    path('remova_account_done/', remove_account_done, name='remove_account_done'),
    path('index/', index, name='index'),
    path('inventory/', inventory, name='inventory')
]
