import uuid
import random
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from main.utils import create_random_sequence
from main.models import ResetPasswordCode, Group, EquipmentCard, EquipmentType
from .models import Token
from .utils import shuffle_string


class UserApiTest(TestCase):
    TEST_USERNAME = 'TestUser'
    TEST_PASSWORD = 'test_user_password'
    TEST_EMAIL = 'test@mail.ru'
    TEST_FIRST_NAME = 'first_name'
    TEST_LAST_NAME = 'last_name'
    TEST_TOKEN = 'token'

    def create_user(self, with_token=True):
        user = User.objects.create_user(
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            email=self.TEST_EMAIL,
            first_name=self.TEST_FIRST_NAME,
            last_name=self.TEST_LAST_NAME
        )
        if not with_token:
            return user

        token = Token.objects.create(user=user, token=str(uuid.uuid4()))
        return user, token.token

    def setUp(self):
        self.client = APIClient()

    def test_success_login(self):
        """Тестируем успешность выполнения логина"""

        user = self.create_user(with_token=False)
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

        user = self.create_user(with_token=False)
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

        user, token = self.create_user()

        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(reverse('api:logout'))

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        token_base_count = Token.objects.count()
        self.assertEqual(token_base_count, 0, 'Токен не был удален из БД')

    def test_fail_logout(self):
        """Тестируем невозможность выполнения выхода из системы при некорректных данных (отсутствие токена)"""

        self.create_user()

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

        equipment_type_exists = EquipmentType.objects.exists()
        self.assertTrue(
            equipment_type_exists,
            'Не создан набор типов оборудования для зарегистрированного пользователя'
        )

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

        user, token = self.create_user()

        username = shuffle_string(self.TEST_USERNAME)
        email = f'{create_random_sequence(10)}@{create_random_sequence(10)}.{create_random_sequence(3)}'
        first_name = create_random_sequence(10)
        last_name = create_random_sequence(10)

        next_data = dict(username=username, email=email, first_name=first_name, last_name=last_name)

        self.client.credentials(HTTP_AUTHORIZATION=token)
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

        user, token = self.create_user()

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
            client.credentials(HTTP_AUTHORIZATION=token)
            response = client.post(reverse('api:edit_account'), element)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f'Некорректный http-статус ответа для данных: {element}'
            )

    def test_success_remove(self):
        """Тестируем успешное удаление аккаунта"""

        user, token = self.create_user()
        self.client.credentials(HTTP_AUTHORIZATION=token)

        response = self.client.delete(reverse('api:remove_account'), {'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        user_exists = User.objects.exists()
        self.assertFalse(user_exists, 'Пользователь не был удален')

    def test_fail_remove(self):
        """Тестируем невозможность удаления аккаунта при некорректных данных"""

        user, token = self.create_user()
        client1 = APIClient()
        client1.credentials(HTTP_AUTHORIZATION=token)

        response = client1.delete(reverse('api:remove_account'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

        user_exists = User.objects.exists()
        self.assertTrue(user_exists, 'Удалось удалить пользователя не передав его пароль')

        client2 = APIClient()

        response = client2.delete(reverse('api:remove_account'), {'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

        user_exists = User.objects.exists()
        self.assertTrue(user_exists, 'Удалось удалить пользователя не передав его токен')

    def test_success_change_password(self):
        """Тестируем успешное изменение пароля"""

        user, token = self.create_user()
        self.client.credentials(HTTP_AUTHORIZATION=token)

        before_pass_hash = user.password

        response = self.client.post(
            reverse('api:change_password'),
            {
                'password': self.TEST_PASSWORD,
                'next_password': shuffle_string(self.TEST_PASSWORD)
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        user.refresh_from_db()
        after_pass_hash = user.password
        self.assertNotEqual(before_pass_hash, after_pass_hash, 'Пароль не изменился')

    def test_fail_change_password(self):
        """ тестируем невозможность смены пароля при некорректных данных"""

        user, token = self.create_user()
        pass_hash_before = user.password

        client1 = APIClient()
        client1.credentials(HTTP_AUTHORIZATION=token)

        response = client1.post(
            reverse('api:change_password'),
            {
                'password': shuffle_string(self.TEST_PASSWORD),
                'next_password': create_random_sequence(10)
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

        user.refresh_from_db()
        pass_hash_after = user.password
        self.assertEqual(
            pass_hash_before,
            pass_hash_after,
            'Удалось изменить пароль при передаче некорректного текущего пароля'
        )

        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION=token)

        response = client2.post(
            reverse('api:change_password'),
            {
                'password': self.TEST_PASSWORD,
                'next_password': ''
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Некорректный http-статус ответа')

        user.refresh_from_db()
        pass_hash_after = user.password
        self.assertEqual(
            pass_hash_before,
            pass_hash_after,
            'Удалось изменить пароль при передаче некорректного нового пароля'
        )

    def test_success_reset_password(self):
        """Тестируем успешный сброс пароля"""

        # Фейковая функция, имитирующая отправку email
        def fake_send_password_reset_code(u):
            return ResetPasswordCode.objects.create(user=u, code=create_random_sequence(), uuid=str(uuid.uuid4())).uuid

        user = self.create_user(with_token=False)
        password_hash_before = user.password

        from . import views
        send_password_reset_code = views.send_password_reset_code
        views.send_password_reset_code = fake_send_password_reset_code

        # Запрашиваем отправку email с кодом сброса пароля
        client1 = APIClient()
        response = client1.post(reverse('api:reset_password'), {'email': self.TEST_EMAIL})
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            'Некорректный http-статус ответа при запросе письма с кодом сброса пароля'
        )

        # Отправляем код сброса и новый пароль на хук подтверждения кода
        _uuid = response.data['uuid']
        code = ResetPasswordCode.objects.get(user=user).code

        client2 = APIClient()
        response = client2.post(
            reverse('api:reset_password_confirm', args=(_uuid,)),
            {
                'code': code,
                'password': shuffle_string(self.TEST_PASSWORD)
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            'Некорректный http-статус ответа при подтверждении кода сброса пароля'
        )
        user.refresh_from_db()
        password_hash_after = user.password
        self.assertNotEqual(password_hash_before, password_hash_after, 'Пароль не был сброшен')

        views.send_password_reset_code = send_password_reset_code

    def test_fail_reset_password(self):
        """Тестируем невозможность сброса пароля при некорректных данных"""

        user = self.create_user(with_token=False)

        # Проверяем ответ хука при некорректном email
        client1 = APIClient()
        response = client1.post(
            reverse('api:reset_password'),
            {'mail': f'{create_random_sequence(10)}@{create_random_sequence(10)}.{create_random_sequence(3)}'}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            'Некорректный http-статус ответа при попытке получить код на фиктивный email'
        )

        # Проверяем невозможность сбросить пароль при использовании некорректного uuid
        reset_password_code = ResetPasswordCode.objects.create(
            user=user,
            code=create_random_sequence(),
            uuid=str(uuid.uuid4())
        )
        client2 = APIClient()
        response = client2.post(reverse('api:reset_password_confirm', args=(str(uuid.uuid4()),)))
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            'Некорректный http-статус ответа при попытке получить код на некорректный uuid'
        )

        # Проверяем невозможность сбросить пароль при вводе некорректного кода
        client3 = APIClient()
        response = client3.post(
            reverse('api:reset_password_confirm', args=(reset_password_code.uuid,)),
            {'code': shuffle_string(reset_password_code.code)}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            'Неверный статус http-ответа при попытке сбросить пароль с некорректным кодом'
        )

        # Проверяем невозможность сбросить пароль, если новый пароль не удоавлетворяет требованиям
        client4 = APIClient()
        response = client4.post(
            reverse('api:reset_password_confirm', args=(reset_password_code.uuid,)),
            {
                'code': reset_password_code.code,
                'password': ''
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            'Неверный статус http-ответа при попытке сбросить пароль с некорректным новым паролем'
        )


class StatApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_stat(self):
        """Тестируем работу хука получения статистики"""

        user, token = UserApiTest().create_user()

        count_by_groups = {}
        count_by_types = {}
        price_by_groups = {}
        price_by_types = {}
        for index in range(3):
            group = Group.objects.create(user=user, title=f'group{index}')
            eq_type = EquipmentType.objects.create(user=user, title=f'eq_type{index}')

            count_by_groups[group.pk] = 0
            count_by_types[eq_type.pk] = 0
            price_by_groups[group.pk] = 0
            price_by_types[eq_type.pk] = 0

        groups = Group.objects.all()
        eq_types = EquipmentType.objects.all()

        total_count = random.randint(10, 1000)
        total_price = 0
        for index in range(total_count):
            group = random.choice(groups)
            eq_type = random.choice(eq_types)

            price = random.randint(1000, 9999)
            total_price += price

            count_by_groups[group.pk] += 1
            count_by_types[eq_type.pk] += 1
            price_by_groups[group.pk] += price
            price_by_types[eq_type.pk] += price

            EquipmentCard.objects.create(group=group, equipment_type=eq_type, price=price)

        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(reverse('api:stat'))

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        self.assertEqual(response.data['total_count'], total_count, 'Неверное значение общего количества оборудования')
        self.assertEqual(response.data['total_price'], total_price, 'Неверное значение общей стоимости оборудования')

        for group in response.data['count_by_groups']:
            self.assertEqual(
                group['equipment_count'],
                count_by_groups[group['id']],
                'Некорректный подсчет количества оборудования в отдельных группах'
            )

        for group in response.data['price_by_groups']:
            self.assertEqual(
                group['equipment_price'],
                price_by_groups[group['id']],
                'Некорректный подсчет стоимости оборудования в отдельных группах'
            )

        for eq_type in response.data['count_by_types']:
            self.assertEqual(
                eq_type['equipment_count'],
                count_by_types[eq_type['id']],
                'Некорректный подсчет количества оборудования по типам'
            )

        for eq_type in response.data['price_by_types']:
            self.assertEqual(
                eq_type['equipment_price'],
                price_by_types[eq_type['id']],
                'Некорректный подсчет стоимости оборудования по типам'
            )
