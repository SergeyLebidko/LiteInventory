import uuid
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from main.utils import create_random_sequence
from .models import Token
from .utils import shuffle_string


class UserApiTest(TestCase):
    TEST_USERNAME = 'TestUser'
    TEST_PASSWORD = 'test_user_password'
    TEST_EMAIL = 'test@mail.ru'
    TEST_FIRST_NAME = 'first_name'
    TEST_LAST_NAME = 'last_name'
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

    def test_success_register(self):
        """Тестируем успешную регистрацию пользователей"""

        exists_before = User.objects.exists()

        response = self.client.post(
            reverse('api:register'),
            {
                'username': self.TEST_USERNAME,
                'password': self.TEST_PASSWORD,
                'email': self.TEST_EMAIL,
                'first_name': self.TEST_FIRST_NAME,
                'last_name': self.TEST_LAST_NAME
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'Некорректный http-статус ответа')

        exists_after = User.objects.exists()
        self.assertEqual([exists_before, exists_after], [False, True], 'Пользователь не был создан')

    def test_fail_register(self):
        """Тестируем невозможность регистрации пользователя при некорректных входных данных"""

        data = [
            {
                'username': '',
                'msg': 'Удалось создать пользователя с некорректным логином'
            },
            {
                'username': self.TEST_USERNAME,
                'password': '',
                'msg': 'Удалось создать пользователя с некорректным паролем'
            },
            {
                'username': self.TEST_USERNAME,
                'password': self.TEST_PASSWORD,
                'email': '',
                'msg': 'Удалось создать пользователя с некорректным email'
            }
        ]

        for element in data:
            before_exists = User.objects.exists()
            client = APIClient()
            response = client.post(reverse('api:register'), element)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f'Некорректный http-статус для следующих данных: {element}'
            )
            after_exists = User.objects.exists()
            self.assertEqual([before_exists, after_exists], [False, False], element['msg'])

        initial = dict(username=self.TEST_USERNAME, password=self.TEST_PASSWORD, email=self.TEST_EMAIL)
        User.objects.create_user(**initial)
        client = APIClient()
        response = client.post(reverse('api:register'), initial)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            'Некорректный http-статус ответа при попытке создать двух одинаковых пользователей'
        )

    def test_success_edit(self):
        """Тестируем успешное редактирование аккаунта"""

        user = User.objects.create_user(
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            email=self.TEST_EMAIL,
            first_name=self.TEST_FIRST_NAME,
            last_name=self.TEST_LAST_NAME
        )
        token = Token.objects.create(user=user, token=str(uuid.uuid4()))

        username = shuffle_string(self.TEST_USERNAME)
        email = f'{create_random_sequence(10)}@{create_random_sequence(10)}.{create_random_sequence(3)}'
        first_name = create_random_sequence(10)
        last_name = create_random_sequence(10)

        next_data = dict(username=username, email=email, first_name=first_name, last_name=last_name)

        self.client.credentials(HTTP_AUTHORIZATION=token.token)
        response = self.client.post(reverse('api:edit_account'), next_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        user = User.objects.first()
        self.assertEqual(
            [username, email, first_name, last_name],
            [user.username, user.email, user.first_name, user.last_name],
            'Данные в БД не были обновлены, либо обновлены некорректно'
        )

    def test_fail_edit(self):
        """Тестируем невозможность редактирования аккаунта при некорректных данных"""

        user = User.objects.create_user(
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            email=self.TEST_EMAIL,
            first_name=self.TEST_FIRST_NAME,
            last_name=self.TEST_LAST_NAME
        )
        token = Token.objects.create(user=user, token=str(uuid.uuid4()))

        data = [
            {
                'username': '',
                'email': self.TEST_EMAIL
            },
            {
                'username': self.TEST_USERNAME,
                'email': ''
            },
            {
                'username': '',
                'email': ''
            }
        ]
        for element in data:
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=token.token)
            response = client.post(reverse('api:edit_account'), element)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f'Некорректный http-статус ответа для данных: {element}'
            )
