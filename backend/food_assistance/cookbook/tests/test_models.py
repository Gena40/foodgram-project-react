from django.db.utils import DataError, IntegrityError
from rest_framework.test import APITestCase
from users.models import Follow, User
from cookbook.models import (Ingredient, Recipe, RecipeIngredients,
                             Tag)

from food_assistance.settings import MEDIA_ROOT


class StrModelsTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            email='vpupkin@yandex.ru',
            username='vasya',
            first_name='Вася',
            last_name='Пупкин',
            password='123**Qwerty123'
        )
        cls.author = User.objects.create_user(
            email='author@yandex.ru',
            username='author',
            first_name='Автор',
            last_name='Шеф',
            password='123**sheff!'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )
        cls.tag = Tag.objects.create(
            name='test_tag_name',
            color='#49B64E',
            slug='test_tag_slug'
        )
        cls.ingredient = Ingredient.objects.create(
            name='test_ingr',
            measurement_unit='кг'
        )
        cls.recipe = Recipe.objects.create(
            name='Запеканка по-домашнему',
            author=cls.user,
            text='test_recipe_text',
            image=MEDIA_ROOT + 'test.jpg',
            cooking_time=30
        )
        cls.resipe_ingr = RecipeIngredients.objects.create(
            recipe=cls.recipe,
            ingredient=cls.ingredient,
            amount=13
        )

    def test_models_have_correct_object_names(self):
        """Проверяем что у моделей корректно работает __str__."""
        obj2tring = {
            StrModelsTest.tag: 'test_tag_name',
            StrModelsTest.ingredient: 'test_ingr, кг',
            StrModelsTest.recipe: (
                'Рецепт "Запеканка по-домашнему" автора vasya'
            ),
            StrModelsTest.follow: (
                'Пользователь vasya подписан на автора author'
            ),
            StrModelsTest.resipe_ingr: (
                'Количество ингредиента test_ingr, кг в рецепте'
                ' Рецепт "Запеканка по-домашнему" автора vasya - 13'
            )
        }
        for obj, obj_str in obj2tring.items():
            with self.subTest(obj=obj):
                self.assertEqual(str(obj), obj_str)

    def test_validate_cooking_time(self):
        """
        Проверка невозможности создания рецепта
        с отрицательным временем приготовления.
        """
        with self.assertRaises(IntegrityError):
            Recipe.objects.create(
                name='Полдник метафизика',
                author=StrModelsTest.user,
                text='impossible recipe',
                image=MEDIA_ROOT + 'test.jpg',
                cooking_time=-15
            )


class TagsModelTests(APITestCase):
    def test_invalid_name(self):
        """
        Проверка соблюдения ограничения на длинну поля name.
        """
        with self.assertRaises(DataError):
            Tag.objects.create(
                name='too_long_name' * 20,
                color='#h12345',
                slug='test_slug1'
            )

    def test_invalid_color(self):
        """
        Проверка соблюдения ограничения на поле color.
        """
        with self.assertRaises(DataError):
            Tag.objects.create(
                name='tag_name1',
                color='wrong_color',
                slug='test_slug2'
            )

    def test_invalid_slug(self):
        """
        Проверка соблюдения ограничения на длинну поля slug.
        """
        with self.assertRaises(DataError):
            Tag.objects.create(
                name='tag_name2',
                color='#h23456',
                slug='too_long_slug' * 20
            )
