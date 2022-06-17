from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from cookbook.models import FavoritRecipes, Recipe

User = get_user_model()


class FavoritRecipesTests(APITestCase):
    def setUp(self) -> None:
        self.test_user = User.objects.create(
            email='test_user@yandex.ru',
            username='test_user',
            first_name='test_user_name',
            last_name='test_user_family',
            password='Test**Qwerty123'
        )
        self.author = User.objects.create(
            email='author@yandex.ru',
            username='author',
            first_name='author_name',
            last_name='author_family',
            password='Author**Qwerty123'
        )
        self.test_recipe = Recipe.objects.create(
            author=self.author,
            name='test_recipe_name',
            text='test_recipe_text',
            image='',
            cooking_time=12
        )
        self.test_recipe2 = Recipe.objects.create(
            author=self.author,
            name='test_recipe2_name',
            text='test_recipe2_text',
            image='',
            cooking_time=25
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.test_user)

    def test_add_into_favorites(self):
        """
        Проверка добавления рецепта в избранное.
        """
        len_favorit_recipes_before = FavoritRecipes.objects.filter(
            user=self.test_user
        ).count()
        recipe_id = self.test_recipe.id
        response = self.auth_client.post(f'/api/recipes/{recipe_id}/favorite/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        favorit_recipes_after = FavoritRecipes.objects.filter(
            user=self.test_user
        )
        len_favorit_recipes_after = favorit_recipes_after.count()
        self.assertNotEqual(
            len_favorit_recipes_before,
            len_favorit_recipes_after
        )
        self.assertEqual(
            str(favorit_recipes_after[0]),
            'Рецепт "test_recipe_name" автора author в избранном у test_user'
        )

    def test_add_into_favorites_twice(self):
        """
        Проверка что невозможно добавить рецепт в избранное дважды.
        """
        recipe_id = self.test_recipe.id
        response = self.auth_client.post(f'/api/recipes/{recipe_id}/favorite/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.auth_client.post(f'/api/recipes/{recipe_id}/favorite/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            'Recipe already in favorites.'
        )

    def test_del_from_favorites(self):
        """
        Проверка удаления рецепта из избранного.
        """
        recipe_id = self.test_recipe.id
        len_fav_recipes_before = FavoritRecipes.objects.filter(
            user=self.test_user
        ).count()
        self.assertEqual(len_fav_recipes_before, 0)
        response = self.auth_client.post(f'/api/recipes/{recipe_id}/favorite/')
        len_fav_recipes_after_add = FavoritRecipes.objects.filter(
            user=self.test_user
        ).count()
        self.assertEqual(len_fav_recipes_after_add, 1)
        response = self.auth_client.delete(
            f'/api/recipes/{recipe_id}/favorite/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        len_fav_recipes_after_del = FavoritRecipes.objects.filter(
            user=self.test_user
        ).count()
        self.assertEqual(len_fav_recipes_after_del, 0)

    def test_favorites_not_exist(self):
        """
        Проверка что невозможно удалить из избранного рецепт,
        которого там нет.
        """
        recipe_id = self.test_recipe2.id
        response = self.auth_client.delete(
            f'/api/recipes/{recipe_id}/favorite/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            'Recipe not in favorites.'
        )
