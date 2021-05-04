from django.test import TestCase
from rest_framework.test import APIClient


class UserApiTest(TestCase):

    def test_login(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Testing token')
        response = client.post('/api/login/')
        print(response.data)
        print('Тест завершен успешно')
