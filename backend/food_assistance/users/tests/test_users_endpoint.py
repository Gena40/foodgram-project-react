from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from cookbook.models import Follow


User = get_user_model()


class CreateUserTests(APITestCase):
    def setUp(self) -> None:
        self.url = '/api/users/'
        self.data = {
            "email": "vpupkin@yandex.ru",
            "username": "vasya.pupkin",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "123**Qwerty123"
        }

    def test_create_new_user(self):
        """
        При корректных полях POST запрос на api/users/
        создает нового пользователя.
        """
        response = self.client.post(self.url, self.data)
        response_dict = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_dict.get('email'), self.data.get('email'))
        self.assertEqual(response_dict.get('username'), self.data.get('username'))
        self.assertEqual(response_dict.get('first_name'), self.data.get('first_name'))
        self.assertEqual(response_dict.get('last_name'), self.data.get('last_name'))

    def test_response_content_is_correct(self):
        """
        При создании нового user возвращается JSON, соответствующий ReDoc.
        """
        response_dict = self.client.post(self.url, self.data).json()
        self.assertEqual(list(response_dict.keys()), ['email', 'id', 'username', 'first_name', 'last_name'])

    def test_not_create_new_user(self):
        """
        При отсутствии одного из обязательных полей POST запрос на api/users/
        НЕ создает нового пользователя.
        """
        data_without_email = self.data.copy()
        data_without_email.pop('email')
        data_without_username = self.data.copy()
        data_without_username.pop('username')
        data_without_first_name = self.data.copy()
        data_without_first_name.pop('first_name')
        data_without_last_name = self.data.copy()
        data_without_last_name.pop('last_name')
        data_without_field = {
            'email': data_without_email,
            'username': data_without_username,
            'first_name': data_without_first_name,
            'last_name': data_without_last_name
        }
        for field, data in data_without_field.items():
            with self.subTest(data=data):
                response = self.client.post(self.url, data)
                response_dict = response.json()
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response_dict.keys())


class ListUsersTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email = "user@yandex.ru",
            username = "user_me",
            first_name = "me_name",
            last_name = "me_family",
            password = "Me**Qwerty123"
        )

        self.url = '/api/users/'
        self.data = {
            "email": "vpupkin@yandex.ru",
            "username": "vasya.pupkin",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "123**Qwerty123"
        }
        self.number_of_test_users: int = 10
        for i in range(self.number_of_test_users):
            data = self.data.copy()
            data['username'] = "vasya.pupkin" + str(i)
            self.client.post(self.url, data)
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.user)

    def test_pagination_of_users_list(self):
        """
        Проверка работы пагинации.
        """
        all_users = User.objects.all()
        response = self.auth_client.get(self.url + '?limit=5&page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(len(all_users), self.number_of_test_users + 1)
        self.assertEqual(response_dict.get('count'), self.number_of_test_users + 1)
        self.assertEqual(len(response_dict.get('results')), 5)


class ProfileUsersTests(APITestCase):
    def setUp(self) -> None:
        self.url = '/api/users/'
        self.user = User.objects.create_user(
            email = "user@yandex.ru",
            username = "user_me",
            first_name = "me_name",
            last_name = "me_family",
            password = "Me**Qwerty123"
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.user)
        self.data1 = {
            "email": "vpupkin@yandex.ru",
            "username": "vasya",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "123**Qwerty123"
        }
        self.data2 = {
            "email": "ppupkin@yandex.ru",
            "username": "petya",
            "first_name": "Петя",
            "last_name": "Пупкин",
            "password": "123**Qwerty123"
        }
        self.client.post(self.url, self.data1)
        self.client.post(self.url, self.data2)

    def test_is_subscribed_field(self):
        """
        Проверка корректности поля is_subscribed.
        """
        follower = User.objects.get(username='vasya')
        response = self.auth_client.get(f'/api/users/{follower.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('is_subscribed'), False)
        Follow.objects.create(user=self.user, author=follower)
        response = self.auth_client.get(f'/api/users/{follower.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('is_subscribed'), True)

    def test_404_profile(self):
        """
        Проверка возвращает ли запрос несуществующего id ошибку 404.
        """
        response = self.auth_client.get('/api/users/12345/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_401_profile(self):
        """
        Проверка возвращает ли запрос от незалогиненого пользователя ошибку 401.
        """
        exist_user = User.objects.get(username='vasya')
        response = self.auth_client.get(f'/api/users/{exist_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'/api/users/{exist_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.auth_client.get(f'/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetTokenTests(APITestCase):
    def setUp(self) -> None:
        self.data = {
            "email": "vpupkin@yandex.ru",
            "username": "vasya.pupkin",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "password": "123**Qwerty123"
        }
        self.client.post('/api/users/', self.data)

    def test_get_token_endpoint_available(self):
        """Проверка работоспособности эндпоинта получения токена.
        """
        url = '/api/auth/token/login/'
        data = {
            "email": self.data.get('email'),
            "password": self.data.get('password')
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertIsNotNone(response_dict.get('auth_token'))
