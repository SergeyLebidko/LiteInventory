from django.urls import path
from .views import Register, Login, Logout, ChangePassword, ChangePasswordDone, index, inventory

app_name = 'main'

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('change_password_done/', ChangePasswordDone.as_view(), name='change_password_done'),
    path('index/', index, name='index'),
    path('inventrory/', inventory, name='inventory')
]
