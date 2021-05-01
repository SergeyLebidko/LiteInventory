from django.urls import path
from .views import Register, Login, Logout, index, inventory

app_name = 'main'

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('index/', index, name='index'),
    path('inventrory/', inventory, name='inventory')
]
