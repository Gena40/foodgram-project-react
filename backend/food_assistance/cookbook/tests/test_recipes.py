from cookbook.models import (FavoritRecipes, Ingredient, Recipe,
                             RecipeIngredients, Tag)
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class RecipesListTests(APITestCase):
    def setUp(self) -> None:
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
        self.tag1 = Tag.objects.create(
            name='tag1_name',
            color='#A12345',
            slug='tag1'
        )
        self.tag2 = Tag.objects.create(
            name='tag2_name',
            color='#B12345',
            slug='tag2'
        )
        self.test_recipe = Recipe.objects.create(
            author=self.author,
            name='test_recipe_name',
            text='test_recipe_text',
            image='',
            cooking_time=12
        )
        self.test_recipe.tags.add(self.tag1)
        self.test_recipe.tags.add(self.tag2)
        self.test_recipe2 = Recipe.objects.create(
            author=self.author,
            name='test_recipe2_name',
            text='test_recipe2_text',
            image='',
            cooking_time=25
        )
        self.test_recipe2.tags.add(self.tag1)
        self.test_recipe3 = Recipe.objects.create(
            author=self.test_user,
            name='test_recipe3_name',
            text='test_recipe3_text',
            image='',
            cooking_time=33
        )
        FavoritRecipes.objects.create(
            user=self.test_user,
            recipe=self.test_recipe
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.test_user)

    def test_recipes_list_access(self):
        """
        Проверка доступности эндпоинта
        /api/recipes/ для всех пользователей.
        """
        response = self.auth_client.get('/api/recipes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recipe_detail_access(self):
        """
        Проверка доступности эндпоинта
        /api/recipes/id для всех пользователей.
        """
        recipe_id = self.test_recipe.id
        response = self.auth_client.get(f'/api/recipes/{recipe_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'/api/recipes/{recipe_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recipes_list_pagination(self):
        """
        Проверка что пагинация включена.
        """
        response = self.auth_client.get('/api/recipes/?page=1&limit=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(
            list(response_dict.keys()),
            ['count', 'next', 'previous', 'results']
        )
        response = self.client.get('/api/recipes/?page=1&limit=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(
            list(response_dict.keys()),
            ['count', 'next', 'previous', 'results']
        )

    def test_recipes_list_is_favorited(self):
        """
        Проверка параметров запроса is_favorited.
        """
        response = self.auth_client.get(
            '/api/recipes/?page=1&limit=10&is_favorited=1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('count'), 1)
        self.assertEqual(
            response_dict.get('results')[0].get('name'),
            'test_recipe_name'
        )
        self.assertEqual(
            response_dict.get('results')[0].get('is_favorited'),
            True
        )

        response = self.auth_client.get(
            '/api/recipes/?page=1&limit=10&is_favorited=0'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('count'), 2)
        self.assertEqual(
            response_dict.get('results')[0].get('is_favorited'),
            False
        )

    def test_recipes_list_author(self):
        """
        Проверка параметра запроса author.
        """
        author_id = self.test_user.id
        response = self.auth_client.get(
            f'/api/recipes/?page=1&limit=10&author={author_id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('count'), 1)
        self.assertEqual(
            response_dict.get('results')[0].get('name'),
            'test_recipe3_name'
        )

    def test_recipes_list_tags(self):
        """
        Проверка параметра запроса tags.
        """
        tag1_slug = self.tag1.slug
        response = self.auth_client.get(
            f'/api/recipes/?page=1&limit=10&tags={tag1_slug}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('count'), 2)

        tag2_slug = self.tag2.slug
        response = self.auth_client.get(
            f'/api/recipes/?page=1&limit=10&tags={tag2_slug}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('count'), 1)
        self.assertEqual(
            response_dict.get('results')[0].get('name'),
            'test_recipe_name'
        )

    def test_recipes_list_tags_access(self):
        """
        Проверка доступности фильтрации по тегам для
        неавторизованных пользователей.
        """
        tag1_slug = self.tag1.slug
        response = self.client.get(
            f'/api/recipes/?page=1&limit=10&tags={tag1_slug}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('count'), 2)

        tag2_slug = self.tag2.slug
        response = self.client.get(
            f'/api/recipes/?page=1&limit=10&tags={tag2_slug}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('count'), 1)
        self.assertEqual(
            response_dict.get('results')[0].get('name'),
            'test_recipe_name'
        )


class CreateRecipeTests(APITestCase):
    def setUp(self) -> None:
        self.test_user = User.objects.create(
            email="test_user@yandex.ru",
            username="test_user",
            first_name="test_user_name",
            last_name="test_user_family",
            password="Test**Qwerty123"
        )
        self.tag1 = Tag.objects.create(
            name='tag1_name',
            color='#A12345',
            slug='tag1'
        )
        self.tag2 = Tag.objects.create(
            name='tag2_name',
            color='#B12345',
            slug='tag2'
        )
        self.test_ingr1 = Ingredient.objects.create(
            name='ingr1_name',
            measurement_unit='шт'
        )
        self.test_ingr2 = Ingredient.objects.create(
            name='ingr2_name',
            measurement_unit='кг'
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.test_user)
        self.data = {
            'ingredients': [
                {
                    'id': self.test_ingr1.id,
                    'amount': 5
                }
            ],
            'tags': [
                self.tag1.id,
                self.tag2.id
            ],
            'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA'
                      'BAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMA'
                      'AA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJR'
                      'U5ErkJggg=='),
            'name': 'new_recipe',
            'text': 'text about new recipe',
            'cooking_time': 30
        }

    def test_create_new_recipe(self):
        """
        При корректных полях POST запрос на api/recipes/
        создает новый рецепт.
        """
        response = self.auth_client.post('/api/recipes/', self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_dict = response.json()
        self.assertEqual(response_dict.get('name'), 'new_recipe')
        self.assertEqual(response_dict.get('text'), 'text about new recipe')
        self.assertEqual(response_dict.get('cooking_time'), 30)
        self.assertEqual(
            response_dict.get('author').get('username'),
            'test_user'
        )
        self.assertEqual(len(response_dict.get('tags')), 2)
        self.assertEqual(
            response_dict.get('ingredients')[0].get('name'),
            'ingr1_name'
        )

    def test_response_content_is_correct(self):
        """
        При создании нового рецепта возвращается JSON, соответствующий ReDoc.
        """
        response_dict = self.auth_client.post(
            '/api/recipes/',
            self.data
        ).json()
        self.assertEqual(
            list(response_dict.keys()),
            [
                'id', 'tags', 'author', 'ingredients', 'is_favorited',
                'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
            ]
        )
        self.assertEqual(type(response_dict.get('tags')), type([]))
        self.assertEqual(type(response_dict.get('ingredients')), type([]))
        self.assertEqual(type(response_dict.get('author')), type(dict()))
        self.assertEqual(type(response_dict.get('is_favorited')), type(True))
        self.assertEqual(
            type(response_dict.get('is_in_shopping_cart')),
            type(True)
        )

    def test_not_create_new_recipe(self):
        """
        При отсутствии одного из обязательных полей POST запрос на api/recipes/
        НЕ создает новый рецепт.
        """
        data_without_ingredients = self.data.copy()
        data_without_ingredients.pop('ingredients')
        data_without_tags = self.data.copy()
        data_without_tags.pop('tags')
        data_without_image = self.data.copy()
        data_without_image.pop('image')
        data_without_name = self.data.copy()
        data_without_name.pop('name')
        data_without_text = self.data.copy()
        data_without_text.pop('text')
        data_without_cooking_time = self.data.copy()
        data_without_cooking_time.pop('cooking_time')
        data_without_field = {
            'ingredients': data_without_ingredients,
            'tags': data_without_tags,
            'image': data_without_image,
            'name': data_without_name,
            'text': data_without_text,
            'cooking_time': data_without_cooking_time
        }
        for field, data in data_without_field.items():
            with self.subTest(data=data):
                response = self.auth_client.post('/api/recipes/', data)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST
                )
                response_dict = response.json()
                self.assertIn(field, response_dict.keys())

    def test_response_not_auth(self):
        """
        Невозможно создать новый рецепт неавторизованному пользователю.
        """
        response = self.client.post('/api/recipes/', self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetPatchDelRecipeTests(APITestCase):
    def setUp(self) -> None:
        self.test_user = User.objects.create(
            email="test_user@yandex.ru",
            username="test_user",
            first_name="test_user_name",
            last_name="test_user_family",
            password="Test**Qwerty123"
        )
        self.test_user2 = User.objects.create(
            email="test_user2@yandex.ru",
            username="test_user2",
            first_name="test_user2_name",
            last_name="test_user2_family",
            password="Test**Qwerty123"
        )
        self.tag1 = Tag.objects.create(
            name='tag1_name',
            color='#A12345',
            slug='tag1'
        )
        self.tag2 = Tag.objects.create(
            name='tag2_name',
            color='#B12345',
            slug='tag2'
        )
        self.test_ingr1 = Ingredient.objects.create(
            name='ingr1_name',
            measurement_unit='шт'
        )
        self.test_ingr2 = Ingredient.objects.create(
            name='ingr2_name',
            measurement_unit='кг'
        )
        self.test_recipe = Recipe.objects.create(
            author=self.test_user,
            name='test_recipe_name',
            text='test_recipe_text',
            image='',
            cooking_time=12
        )
        self.test_recipe.tags.add(self.tag1)
        self.test_recipe.tags.add(self.tag2)
        RecipeIngredients.objects.create(
            recipe=self.test_recipe,
            ingredient=self.test_ingr1,
            amount=10
        )
        self.test_recipe2 = Recipe.objects.create(
            author=self.test_user,
            name='test_recipe2_name',
            text='test_recipe2_text',
            image='',
            cooking_time=25
        )
        self.test_recipe2.tags.add(self.tag1)
        self.test_recipe2.tags.add(self.tag2)
        RecipeIngredients.objects.create(
            recipe=self.test_recipe2,
            ingredient=self.test_ingr1,
            amount=125
        )
        RecipeIngredients.objects.create(
            recipe=self.test_recipe2,
            ingredient=self.test_ingr2,
            amount=6
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.test_user)
        self.auth_client2 = APIClient()
        self.auth_client2.force_authenticate(user=self.test_user2)

    def test_get_recipe(self):
        """
        При корректном запросе возвращается ответ в соответствии с ReDoc.
        """
        recipe_id = self.test_recipe.id
        response = self.auth_client.get(f'/api/recipes/{recipe_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('id'), recipe_id)
        self.assertEqual(response_dict.get('name'), 'test_recipe_name')
        self.assertEqual(response_dict.get('text'), 'test_recipe_text')
        self.assertEqual(response_dict.get('cooking_time'), 12)
        self.assertEqual(
            response_dict.get('author').get('username'),
            'test_user'
        )
        self.assertEqual(len(response_dict.get('tags')), 2)
        self.assertEqual(
            response_dict.get('ingredients')[0].get('name'),
            'ingr1_name'
        )

    def test_update_recipe(self):
        """
        Проверка обновления рецепта.
        """
        update_data = {
            'ingredients': [
                {
                    'id': self.test_ingr1.id,
                    'amount': 100
                }
            ],
            "tags": [
                self.tag2.id
            ],
            "image": ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA'
                      'BAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMA'
                      'AA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJR'
                      'U5ErkJggg=='),
            "name": "updating_name",
            "text": "updating_text",
            "cooking_time": 60
        }
        recipe_id = self.test_recipe2.id
        response = self.auth_client.patch(
            f'/api/recipes/{recipe_id}/',
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(response_dict.get('id'), recipe_id)
        self.assertEqual(response_dict.get('name'), 'updating_name')
        self.assertEqual(response_dict.get('text'), 'updating_text')
        self.assertEqual(response_dict.get('cooking_time'), 60)
        self.assertEqual(
            response_dict.get('author').get('username'),
            'test_user'
        )
        self.assertEqual(len(response_dict.get('tags')), 1)
        self.assertEqual(
            response_dict.get('ingredients')[0].get('name'),
            'ingr1_name'
        )
        self.assertEqual(
            response_dict.get('ingredients')[0].get('amount'),
            100
        )

    def test_update400error_recipe(self):
        """
        Проверка ошибок валидации отдельных полей.
        """
        update_data = {
            'ingredients': [
                {
                    'id': self.test_ingr1.id,
                    'amount': 0
                }
            ],
            "tags": [],
            "image": ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA'
                      'BAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMA'
                      'AA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJR'
                      'U5ErkJggg=='),
            "name": "new_name",
            "text": "new_text",
            "cooking_time": 30
        }
        recipe_id = self.test_recipe2.id
        response = self.auth_client.patch(
            f'/api/recipes/{recipe_id}/',
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(type(response_dict.get('ingredients')), type([]))
        self.assertEqual(
            response_dict.get('ingredients')[0].get('amount'),
            ['Amount of ingredients must be > 0']
        )

    def test_update_permission_error_recipe(self):
        """
        Проверка что менять рецепт может только его автор.
        """
        update_data = {
            'ingredients': [
                {
                    'id': self.test_ingr1.id,
                    'amount': 1
                }
            ],
            "tags": [],
            "image": ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA'
                      'BAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMA'
                      'AA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJR'
                      'U5ErkJggg=='),
            "name": "new_name",
            "text": "new_text",
            "cooking_time": 30
        }
        recipe_id = self.test_recipe2.id
        response = self.auth_client2.patch(
            f'/api/recipes/{recipe_id}/',
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_recipe(self):
        """
        Проверка удаления рецепта.
        """
        recipe_id = self.test_recipe.id
        len_all_recipes_before = len(Recipe.objects.all())
        response = self.auth_client.delete(f'/api/recipes/{recipe_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        len_all_recipes_after = len(Recipe.objects.all())
        self.assertNotEqual(len_all_recipes_before, len_all_recipes_after)
