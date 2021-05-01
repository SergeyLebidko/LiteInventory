from django.urls import path
from .views import Login, Logout, index, inventory

app_name = 'main'

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('index/', index, name='index'),
    path('inventrory/', inventory, name='inventory')
]
