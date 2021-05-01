from django.urls import path
from .views import Login, index, inventory

app_name = 'main'

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('index/', index, name='index'),
    path('inventrory/', inventory, name='inventory')
]
