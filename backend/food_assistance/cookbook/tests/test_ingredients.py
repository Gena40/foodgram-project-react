from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from cookbook.models import Ingredient


User = get_user_model()


class IngredientsListTests(APITestCase):
    def setUp(self) -> None:
        self.ingr_1 = Ingredient.objects.create(
            name='ingr1_name',
            measurement_unit='ingr1_unit'
        )
        self.ingr_2 = Ingredient.objects.create(
            name='ingr2_name',
            measurement_unit='ingr2_unit'
        )
        self.ingr_3 = Ingredient.objects.create(
            name='ingr3_name',
            measurement_unit='ingr3_unit'
        )

    def test_get_ingredient_list(self):
        """
        Проверка корректности работы эндпоинта api/ingredients/
        """
        response = self.client.get('/api/ingredients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(len(response_dict), 3)

    def test_corret_json(self):
        """
        Проверка соответствия возвращаемого JSON документации.
        """
        response = self.client.get('/api/ingredients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(type(response_dict), type([]))
        self.assertEqual(
            list(response_dict[0].keys()),
            ['id', 'name', 'measurement_unit']
        )

    def test_search_ingredient_by_name(self):
        """
        Проверка работы поиска по частичному вхождению
        в начале названия ингредиента /api/ingredient/{id}
        """
        response = self.client.get(f'/api/ingredients/?search=ingr2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(len(response_dict), 1)
        self.assertEqual(response_dict[0].get('name'), 'ingr2_name')
        response = self.client.get('/api/ingredients/?search=not_exist_name')
        response_dict = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_dict), 0)

    def test_get_ingredient_by_id(self):
        """
        Проверка эндпоинта /api/ingredients/{id}/
        """
        response = self.client.get(f'/api/ingredients/{self.ingr_3.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(
            list(response_dict.keys()),
            ['id', 'name', 'measurement_unit']
        )
        self.assertEqual(response_dict.get('name'), 'ingr3_name')
        response = self.client.get('/api/ingredients/123/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
