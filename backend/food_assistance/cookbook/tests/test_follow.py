from cookbook.models import Follow, Recipe
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class MyFollowsTests(APITestCase):
    def setUp(self) -> None:
        self.follower = User.objects.create(
            email="follower@yandex.ru",
            username="follower",
            first_name="follower_name",
            last_name="follower_family",
            password="Follower**Qwerty123"
        )
        self.test_user = User.objects.create(
            email="test_user@yandex.ru",
            username="test_user",
            first_name="test_user_name",
            last_name="test_user_family",
            password="Test**Qwerty123"
        )
        self.author = User.objects.create(
            email="author@yandex.ru",
            username="author",
            first_name="author_name",
            last_name="author_family",
            password="Author**Qwerty123"
        )
        self.test_recipe = Recipe.objects.create(
            author=self.author,
            name='test_recipe_name',
            text='test_recipe_text',
            image='',
            cooking_time=12
        )
        Follow.objects.create(
            author=self.author,
            user=self.follower
        )
        Follow.objects.create(
            author=self.test_user,
            user=self.follower
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.follower)

    def test_get_my_subscriptions(self):
        """
        Проверка корректности работы эндпоинта api/users/subscriptions/
        """
        response = self.auth_client.get('/api/users/subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(type(response_dict), type([]))
        self.assertEqual(
            list(response_dict[0].keys()),
            [
                'email', 'id', 'username', 'first_name',
                'last_name', 'is_subscribed', 'recipes', 'recipes_count'
            ]
        )
        self.assertEqual(len(response_dict), 2)
        self.assertEqual(type(response_dict[0].get('recipes')), type([]))

    def test_search_ingredient_by_name(self):
        """
        Проверка работы ограничения на количество рецептов
        авторов, на которых подписан.
        """
        self.new_recipe1 = Recipe.objects.create(
            author=self.author,
            name='new_recipe1_name',
            text='new_recipe1_text',
            image='',
            cooking_time=12
        )
        self.new_recipe2 = Recipe.objects.create(
            author=self.author,
            name='new_recipe1_name',
            text='new_recipe1_text',
            image='',
            cooking_time=12
        )
        url = '/api/users/subscriptions/'
        query_params = '?limit=10&page=1&recipes_limit='
        response = self.auth_client.get(url + query_params + '1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json().get('results')[1]
        self.assertEqual(len(response_dict.get('recipes')), 1)
        response = self.auth_client.get(url + query_params + '2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json().get('results')[1]
        self.assertEqual(len(response_dict.get('recipes')), 2)
        response = self.auth_client.get(url + query_params + '12')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json().get('results')[1]
        self.assertEqual(len(response_dict.get('recipes')), 3)


class SubscribeTests(APITestCase):
    def setUp(self) -> None:
        self.follower = User.objects.create(
            email="follower@yandex.ru",
            username="follower",
            first_name="follower_name",
            last_name="follower_family",
            password="Follower**Qwerty123"
        )
        self.test_user = User.objects.create(
            email="test_user@yandex.ru",
            username="test_user",
            first_name="test_user_name",
            last_name="test_user_family",
            password="Test**Qwerty123"
        )
        self.author = User.objects.create(
            email="author@yandex.ru",
            username="author",
            first_name="author_name",
            last_name="author_family",
            password="Author**Qwerty123"
        )
        self.test_recipe = Recipe.objects.create(
            author=self.author,
            name='test_recipe_name',
            text='test_recipe_text',
            image='',
            cooking_time=12
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.follower)

    def test_get_my_subscriptions(self):
        """
        Проверка создания новой подписки через POST api/users/{id}/subscribe/
        """
        test_id = self.test_user.id
        response = self.auth_client.get('/api/users/subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(len(response_dict), 0)
        response = self.auth_client.post(f'/api/users/{test_id}/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscribe_to_yourself(self):
        """
        Проверка что невозможно подписаться на самого себя.
        """
        response = self.auth_client.post(
            f'/api/users/{self.follower.id}/subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            "You can't subscribe to yourself."
        )

    def test_subscribe_twice(self):
        """
        Проверка что невозможно подписаться дважды.
        """
        response = self.auth_client.post(
            f'/api/users/{self.author.id}/subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.auth_client.post(
            f'/api/users/{self.author.id}/subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            "This subscription already exists."
        )

    def test_unsubscribe(self):
        """
        Проверка отписки.
        """
        response = self.auth_client.get('/api/users/subscriptions/')
        self.assertEqual(len(response.json()), 0)
        response = self.auth_client.post(
            f'/api/users/{self.author.id}/subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.auth_client.get('/api/users/subscriptions/')
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0].get('username'), 'author')
        response = self.auth_client.delete(
            f'/api/users/{self.author.id}/subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.auth_client.get('/api/users/subscriptions/')
        self.assertEqual(len(response.json()), 0)

    def test_unfollow_from_yourself(self):
        """
        Проверка что невозможно отписаться от самого себя.
        """
        response = self.auth_client.delete(
            f'/api/users/{self.follower.id}/subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            "You can't subscribe to yourself."
        )

    def test_unfollow_not_exist(self):
        """
        Проверка что невозможно удалить несуществующую подписку.
        """
        response = self.auth_client.delete(
            f'/api/users/{self.test_user.id}/subscribe/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            "Subscription does not exist."
        )
