import uuid
import json
import random
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from api.serializers import EquipmentTypeSerializer, EquipmentFeatureSerializer
from main.utils import create_random_sequence
from main.models import ResetPasswordCode, Group, EquipmentCard, EquipmentType, EquipmentFeature
from .models import Token
from .utils import shuffle_string


class UserApiTest(TestCase):
    TEST_USERNAME = 'TestUser'
    TEST_PASSWORD = 'test_user_password'
    TEST_EMAIL = 'test@mail.ru'
    TEST_FIRST_NAME = 'first_name'
    TEST_LAST_NAME = 'last_name'
    TEST_TOKEN = 'token'

    def create_user(self, with_token=True, is_superuser=False, is_staff=False):
        user = User.objects.create_user(
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            email=self.TEST_EMAIL,
            first_name=self.TEST_FIRST_NAME,
            last_name=self.TEST_LAST_NAME,
            is_superuser=is_superuser,
            is_staff=is_staff
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
                'msg': 'Удалось создать пользователя, не предоставив логин, пароль и email'
            },
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
            credentials = {**element}
            del credentials['msg']
            before_exists = User.objects.exists()
            client = APIClient()
            response = client.post(reverse('api:register'), credentials)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f'Некорректный http-статус для следующих данных: {credentials}'
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
        response = self.client.patch(reverse('api:edit_account'), next_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        user = User.objects.first()
        self.assertEqual(
            [username, email, first_name, last_name],
            [user.username, user.email, user.first_name, user.last_name],
            'Данные в БД не были обновлены, либо обновлены некорректно'
        )

    def test_fail_edit(self):
        """Тестируем невозможность редактирования аккаунта при некорректных данных"""

        # Тестируем невозможность указать пользователю такие же логин и email, как у другого пользователя
        username = shuffle_string(self.TEST_USERNAME)
        password = shuffle_string(self.TEST_PASSWORD)
        email = f'{create_random_sequence(10)}@{create_random_sequence(6)}.{create_random_sequence(3)}'
        user1 = User.objects.create_user(username=username, password=password, email=email)
        user2, token = self.create_user()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=token)
        response = client.patch(reverse('api:edit_account'), {'username': username, 'email': email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Некорректный http-статус ответа')

        user2.refresh_from_db()
        self.assertNotEqual(user2.username, username, 'Удалось назначить пользователю уже существующий в БД логин')
        self.assertNotEqual(user2.email, email, 'Удалось назначить пользователю уже имеющийся в БД email')

        # Тестируем невозможность указать пользователю некорректные логин и email
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=token)
        response = client.patch(reverse('api:edit_account'), {'username': '*', 'email': '*'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Некорректный http-статус ответа')

        self.assertNotEqual(user2.username, '*', 'Удалось назначить пользователю некорректный логин')
        self.assertNotEqual(user2.email, '*', 'Удалось назначить пользователю некорректный email')

        # Очистка перед следующим кейсом
        user1.delete()
        user2.delete()

        # Тестируем невозможность редактирования пользователей со статусом Суперпользователь и Персонал
        for is_superuser, is_staff in [(True, True), (True, False), (False, True)]:
            user, token = self.create_user(is_superuser=is_superuser, is_staff=is_staff)
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=token)

            username_before = user.username
            email_before = user.email
            first_name_before = user.first_name
            last_name_before = user.last_name

            response = client.patch(
                reverse('api:edit_account'),
                {
                    'username': shuffle_string(self.TEST_USERNAME),
                    'email': f'{create_random_sequence(10)}@{create_random_sequence(6)}.{create_random_sequence(3)}',
                    'first_name': shuffle_string(self.TEST_FIRST_NAME),
                    'last_name': shuffle_string(self.TEST_LAST_NAME)
                }
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

            user.refresh_from_db()
            username_after = user.username
            email_after = user.email
            first_name_after = user.first_name
            last_name_after = user.last_name

            self.assertEqual(
                [username_before, email_before, first_name_before, last_name_before],
                [username_after, email_after, first_name_after, last_name_after],
                f'Через API далось отредактировать пользователя со статусом(ами): '
                f'{"Суперпользователь" if is_superuser else ""} '
                f'{"Персонал" if is_staff else ""}'
            )

            user.delete()

    def test_success_remove(self):
        """Тестируем успешное удаление аккаунта"""

        user, token = self.create_user()
        self.client.credentials(HTTP_AUTHORIZATION=token)

        response = self.client.delete(reverse('api:remove_account'), {'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'Некорректный http-статус ответа')

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

        # Тестируем невозможность удаления пользователей со статусом Суперпользователь и Персонал
        for is_superuser, is_staff in [(True, True), (True, False), (False, True)]:
            user.delete()
            user, token = self.create_user(is_superuser=is_superuser, is_staff=is_staff)
            client3 = APIClient()
            client3.credentials(HTTP_AUTHORIZATION=token)

            response = client3.delete(reverse('api:remove_account'), {'password': self.TEST_PASSWORD})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

            user_exists = User.objects.exists()
            self.assertTrue(
                user_exists,
                f'Через API далось удалить пользователя со статусом(ами): '
                f'{"Суперпользователь" if is_superuser else ""} '
                f'{"Персонал" if is_staff else ""}'
            )

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

        # Проверяем удаление токена при смене пароля
        token_exists = Token.objects.filter(token=token).exists()
        self.assertFalse(token_exists, 'При смене пароля токен не был удален')

    def test_fail_change_password(self):
        """ Тестируем невозможность смены пароля при некорректных данных"""

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

        # Тестируем невозможность смены пароля пользователей со статусом Суперпользователь и Персонал
        for is_superuser, is_staff in [(True, True), (True, False), (False, True)]:
            user.delete()
            user, token = self.create_user(is_superuser=is_superuser, is_staff=is_staff)
            client3 = APIClient()
            client3.credentials(HTTP_AUTHORIZATION=token)

            password_before = user.password
            response = client3.post(
                reverse('api:change_password'),
                {
                    'password': self.TEST_PASSWORD,
                    'next_password': shuffle_string(self.TEST_PASSWORD)
                }
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

            user.refresh_from_db()
            password_after = user.password

            self.assertEqual(
                password_before,
                password_after,
                f'Через API далось сменить пароль у пользователя со статусом(ами): '
                f'{"Суперпользователь" if is_superuser else ""} '
                f'{"Персонал" if is_staff else ""}'
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


class MultipleUpdateApiTest(TestCase):
    """Класс для тестирования хуков массового обновления данных"""

    def setUp(self):
        self.client = APIClient()

    def test_success_equipment_types_update(self):
        """Тестируем успешную работу хука массового обновления типов оборудования"""

        user, token = UserApiTest().create_user()

        # Создаем в БД список типов, с которым будем работать
        total_count = 30
        count_to_remove = 10
        count_to_update = 10
        count_to_create = 20

        EquipmentType.objects.bulk_create(
            [EquipmentType(user=user, title=f'type_{index}') for index in range(total_count)]
        )
        types_in_bd = EquipmentType.objects.all()

        # Объекты к удалению
        objects_to_remove = types_in_bd[:count_to_remove]
        removed_ids = [obj.pk for obj in objects_to_remove]

        # Объекты к обновлению
        objects_to_update = types_in_bd.exclude(pk__in=removed_ids)[:count_to_update]
        updated_ids = [obj.pk for obj in objects_to_update]
        for index, obj in enumerate(objects_to_update):
            obj.title = f'updated_type_{index}'

        # Объекты, которые надо будет создать
        objects_to_create = [{'title': f'created_type_{index}'} for index in range(count_to_create)]

        to_remove = json.dumps(EquipmentTypeSerializer(objects_to_remove, many=True).data)
        to_update = json.dumps(EquipmentTypeSerializer(objects_to_update, many=True).data)
        to_create = json.dumps(objects_to_create)

        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            reverse('api:update_equipment_types_list'),
            {
                'to_remove': to_remove,
                'to_update': to_update,
                'to_create': to_create
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        # Проверяем удалены ли объекты
        type_exists = EquipmentType.objects.filter(pk__in=removed_ids).exists()
        self.assertFalse(type_exists, 'Объекты не были удалены')

        # Проверяем, обновлены ли объекты
        for pk in updated_ids:
            self.assertTrue(
                EquipmentType.objects.get(pk=pk).title.startswith('updated_type_'),
                'Некорректное обновление объектов'
            )

        # Проверяем, созданы ли объекты
        for index in range(count_to_create):
            type_exists = EquipmentType.objects.filter(title=f'created_type_{index}').exists()
            self.assertTrue(type_exists, 'Объект не был создан')

    def test_fail_equipment_types_update(self):
        """Тестируем работу хука массового обновления типов оборудования при некорректных данных"""

        user1, _ = UserApiTest().create_user()
        user1.username = 'user1'
        user1.save()

        user2, token = UserApiTest().create_user()
        user2.username = 'user2'
        user2.save()

        total_count = 30
        count_to_remove = 10
        count_to_update = 10

        EquipmentType.objects.bulk_create(
            [EquipmentType(user=user1, title=f'custom_type') for _ in range(total_count)]
        )
        types_in_db = EquipmentType.objects.all()

        to_remove = json.dumps(EquipmentTypeSerializer(types_in_db[:count_to_remove], many=True).data)

        to_update = types_in_db[count_to_remove: count_to_remove + count_to_update]
        for obj in to_update:
            obj.title = 'updated_type'
        to_update = json.dumps(EquipmentTypeSerializer(to_update, many=True).data)

        to_create = '[]'

        # Пробуем выполнить удаление или изменение данных у другого пользователя
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            reverse('api:update_equipment_types_list'),
            {
                'to_remove': to_remove,
                'to_update': to_update,
                'to_create': to_create
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Некорректный http-статус ответа')

        # Проверяем состояние БД после выполнения запроса
        count_in_db = EquipmentType.objects.filter(user=user1).count()
        self.assertEqual(count_in_db, total_count, 'Количество объектов в БД изменилось после выполнения запроса')

        updated_exists = EquipmentType.objects.filter(user=user1, title='updated_type').exists()
        self.assertFalse(updated_exists, 'После выполнения запроса в БД были выполнены изменения')

    def test_success_equipment_features_update(self):
        """Тестируем успешную работу хука массового обновления характеристик оборудования"""

        user, token = UserApiTest().create_user()

        group = Group.objects.create(user=user, title='group')
        eq_type = EquipmentType.objects.create(user=user, title='eq_type')
        eq_card = EquipmentCard.objects.create(group=group, equipment_type=eq_type)

        total_count = 50
        count_to_remove = 10
        count_to_update = 10
        count_to_create = 10

        features = []
        for index in range(total_count):
            features.append(
                EquipmentFeature.objects.create(equipment_card=eq_card, name=f'name_{index}', value=f'value_{index}')
            )

        serializer = EquipmentFeatureSerializer(features, many=True)
        to_remove = serializer.data[:count_to_remove]

        to_update = serializer.data[count_to_remove:count_to_remove + count_to_update]
        for index, obj in enumerate(to_update):
            obj['name'] = f'updated_name_{index}'
            obj['value'] = f'updated_value_{index}'

        to_create = []
        for index in range(count_to_create):
            to_create.append(
                {
                    'equipment_card': eq_card.pk,
                    'name': f'name_created_{index}',
                    'value': f'value_created_{index}'
                }
            )

        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(
            reverse('api:update_equipment_features_list'),
            {
                'to_create': json.dumps(to_create),
                'to_update': json.dumps(to_update),
                'to_remove': json.dumps(to_remove)
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        features_count = EquipmentFeature.objects.filter(equipment_card=eq_card).count()
        self.assertEqual(
            features_count,
            total_count - count_to_remove + count_to_create,
            'Неверное количество объектов в БД'
        )

        updated_objects_count = EquipmentFeature.objects.filter(
            pk__in=[item['id'] for item in to_update],
            name__startswith='updated_name_',
            value__startswith='updated_value'
        ).count()
        self.assertEqual(updated_objects_count, count_to_update, 'Не все характеристики были обновлены')

    def test_fail_equipment_features_update(self):
        """Тестируем работу хука массового обновления свойств при некорректных данных"""

        user1, _ = UserApiTest().create_user()
        user1.username = 'user1'
        user1.save()

        user2, token = UserApiTest().create_user()
        user2.username = 'user2'
        user2.save()

        eq_type_1 = EquipmentType.objects.create(user=user1, title='equipment_type_1')
        group1 = Group.objects.create(user=user1, title='group1')
        card_1 = EquipmentCard.objects.create(group=group1, equipment_type=eq_type_1)

        eq_type_2 = EquipmentType.objects.create(user=user2, title='equipment_type_2')
        group2 = Group.objects.create(user=user2, title='group2')
        card_2 = EquipmentCard.objects.create(group=group2, equipment_type=eq_type_2)

        # Пытаемся изменить список характеристик, принадлежащий разным карточкам
        to_request = json.dumps([
            {'equipment_card': card_1.pk},
            {'equipment_card': card_2.pk}
        ])

        client1 = APIClient()
        client1.credentials(HTTP_AUTHORIZATION=token)
        response = client1.post(
            reverse('api:update_equipment_features_list'),
            {
                'to_remove': to_request,
                'to_create': to_request,
                'to_update': to_request
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            'Некорректный http-статус ответа для попытки изменения характеристик в карточках сразу двух пользователей'
        )

        # Пытаемся изменить список характеристик карточки, принадлежащей другому пользователю
        to_request = json.dumps([
            {'equipment_card': card_1.pk}
        ])

        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION=token)
        response = client2.post(
            reverse('api:update_equipment_features_list'),
            {
                'to_remove': to_request,
                'to_create': to_request,
                'to_update': to_request
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            'Некорректный http-статус ответа для попытки изменения характеристик в карточке другого пользователя'
        )
