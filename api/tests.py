from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from .models import Token


class UserApiTest(TestCase):
    TEST_USERNAME = 'TestUser'
    TEST_PASSWORD = 'test_user_password'
    TEST_TOKEN = 'token'

    def setUp(self):
        self.client = APIClient()

    def test_success_login(self):
        """Тестируем успешность выполнения логина"""

        user = User.objects.create_user(username='TestUser', password='test_user_password')
        response = self.client.post(
            reverse('api:login'),
            {
                'username': self.TEST_USERNAME,
                'password': self.TEST_PASSWORD
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        response_token = response.data['token']
        try:
            db_token = Token.objects.get(user=user).token
        except Token.DoesNotExist:
            raise AssertionError('В БД не создается токен для пользователя при успешном логине')
        except Token.MultipleObjectsReturned:
            raise AssertionError('В БД создается сразу несколько токенов для пользователя при успешном логине')

        self.assertEqual(db_token, response_token, 'Токены в ответе хука и БД не совпадают')

    def test_fail_login(self):
        """Тестируем невозможность выполнения логина при неверных учетных данных"""

        user = User.objects.create_user(username='TestUser', password='test_user_password')
        response = self.client.post(
            reverse('api:login'),
            {
                'username': self.TEST_USERNAME + '*',
                'password': self.TEST_PASSWORD + '*'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

        token_exists = Token.objects.filter(user=user).exists()
        self.assertFalse(token_exists, 'Токен создается при логине с некорректными учетными данными')

    def test_success_logout(self):
        """Тестируем успешность выхода из системы через api"""

        user = User.objects.create_user(username='TestUser', password='test_user_password')
        token = Token.objects.create(user=user, token=self.TEST_TOKEN)

        self.client.credentials(HTTP_AUTHORIZATION=token.token)
        response = self.client.post(reverse('api:logout'))

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        token_base_count = Token.objects.count()
        self.assertEqual(token_base_count, 0, 'Токен не был удален из БД')

    def test_fail_logout(self):
        """Тестируем невозможность выполнения выхода из системы при некорректных данных"""

        user = User.objects.create_user(username='TestUser', password='test_user_password')
        Token.objects.create(user=user, token=self.TEST_TOKEN)

        response = self.client.post(reverse('api:logout'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

        token_base_count = Token.objects.count()
        self.assertEqual(token_base_count, 1, 'Токен был удален из БД после некорректного запроса')
