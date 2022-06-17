from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from cookbook.models import Tag

User = get_user_model()


class TagsListTests(APITestCase):
    def setUp(self) -> None:
        self.tag_1 = Tag.objects.create(
            name='tag_1_name',
            color='#f36223',
            slug='tag_1_slug'
        )
        self.tag_2 = Tag.objects.create(
            name='tag_2_name',
            color='#g53798',
            slug='tag_2_slug'
        )
        self.tag_3 = Tag.objects.create(
            name='tag_3_name',
            color='#h12345',
            slug='tag_3_slug'
        )

    def test_get_tags_list(self):
        """
        Проверка корректности работы эндпоинта api/tags/
        """
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(len(response_dict), 3)

    def test_corret_json(self):
        """
        Проверка соответствия возвращаемого JSON документации.
        """
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(type(response_dict), type([]))
        self.assertEqual(
            list(response_dict[0].keys()),
            ['id', 'name', 'color', 'slug']
        )

    def test_get_tag_by_id(self):
        """
        Проверка эндпоинта /api/tags/{id}
        """
        response = self.client.get(f'/api/tags/{self.tag_2.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.json()
        self.assertEqual(
            list(response_dict.keys()),
            ['id', 'name', 'color', 'slug']
        )
        response = self.client.get('/api/tags/123/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
