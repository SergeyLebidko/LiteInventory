from django.urls import path

from .views import login

app_name = 'api'

urlpatterns = [
    path('login/', login, name='login')
]
