from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from cookbook.models import (Ingredient, Recipe, RecipeIngredients,
                             ShoppingCartRecipes, Tag)

User = get_user_model()


class ShoppingCartTests(APITestCase):
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
            author=self.author,
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
        RecipeIngredients.objects.create(
            recipe=self.test_recipe,
            ingredient=self.test_ingr2,
            amount=6
        )
        self.test_recipe2 = Recipe.objects.create(
            author=self.author,
            name='test_recipe2_name',
            text='test_recipe2_text',
            image='',
            cooking_time=25
        )
        self.test_recipe2.tags.add(self.tag1)
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.test_user)

    def test_add_recipe_in_shopping_cart(self):
        """
        Проверка добавления рецепта в список покупок.
        """
        len_shopping_cart_before = ShoppingCartRecipes.objects.filter(
            user=self.test_user
        ).all().count()
        recipe_id = self.test_recipe.id
        response = self.auth_client.post(
            f'/api/recipes/{recipe_id}/shopping_cart/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        len_shopping_cart_after = ShoppingCartRecipes.objects.filter(
            user=self.test_user
        ).all().count()
        self.assertNotEqual(len_shopping_cart_before, len_shopping_cart_after)

        response = self.auth_client.post(
            f'/api/recipes/{recipe_id}/shopping_cart/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            'Recipe already in shopping cart.'
        )

        response = self.client.post(
            f'/api/recipes/{recipe_id}/shopping_cart/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_recipe_from_shopping_cart(self):
        """
        Проверка удаления рецепта из списка покупок.
        """
        ShoppingCartRecipes.objects.create(
            user=self.test_user,
            recipe=self.test_recipe2
        )
        len_shopping_cart_before = ShoppingCartRecipes.objects.filter(
            user=self.test_user
        ).all().count()
        recipe_id = self.test_recipe2.id
        response = self.auth_client.delete(
            f'/api/recipes/{recipe_id}/shopping_cart/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        len_shopping_cart_after = ShoppingCartRecipes.objects.filter(
            user=self.test_user
        ).all().count()
        self.assertEqual(len_shopping_cart_before - 1, len_shopping_cart_after)

        response = self.auth_client.delete(
            f'/api/recipes/{recipe_id}/shopping_cart/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_dict = response.json()
        self.assertEqual(
            response_dict.get('errors'),
            'Recipe not in shopping cart.'
        )

        response = self.client.delete(
            f'/api/recipes/{recipe_id}/shopping_cart/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_download_shopping_cart(self):
        """
        Проверка эндпоинта списка покупок.
        """
        ShoppingCartRecipes.objects.create(
            user=self.test_user,
            recipe=self.test_recipe
        )
        response = self.client.get('/api/recipes/download_shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.auth_client.get('/api/recipes/download_shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('ingr1_name' in str(response.content), True)
        self.assertEqual('ingr2_name' in str(response.content), True)
