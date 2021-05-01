from django.urls import path
from .views import index, inventory

app_name = 'main'

urlpatterns = [
    path('index/', index, name='index'),
    path('inventrory/', inventory, name='inventory')
]
