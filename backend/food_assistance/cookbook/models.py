from datetime import datetime

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields.related import ForeignKey

from food_assistance.settings import (MINIMUM_AMOUNT_OF_INGREDIENT,
                                      MINIMUM_COOKING_TIME)
from users.models import User


def get_img_path(instanse: 'Recipe', filename: str) -> str:
    """
    Возвращает путь до изображения для Recipe.image.
    """
    timestamp = str(int(datetime.timestamp(datetime.now())))
    return timestamp + filename


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=False,
        verbose_name='Тег',
        help_text='Введите название тега'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        unique=True,
        db_index=False,
        verbose_name='Цветовой HEX-код',
        help_text='Укажите цветовой HEX-код '
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        unique=True,
        db_index=False,
        verbose_name='Слаг',
        help_text='Введите слаг для тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='uniq_name-measurement_unit_pair'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes_by_tag',
        verbose_name='Тег рецепта',
        help_text='Тег рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты для рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to=get_img_path,
        help_text='Изображение для рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.',
        help_text='Введите время приготовления (в минутах)',
        validators=(MinValueValidator(MINIMUM_COOKING_TIME),)
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'Рецепт "{self.name}" автора {self.author}'


class RecipeIngredients(models.Model):
    """Модель для связи рецепта с ингредиентами."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='igredients_in_recipe',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента в рецепте',
        help_text='Количество ингредиента в рецепте',
        validators=(MinValueValidator(MINIMUM_AMOUNT_OF_INGREDIENT),)
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецептах'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self) -> str:
        return (f'Количество ингредиента {self.ingredient}'
                f' в рецепте {self.recipe} - {self.amount}')


class FavoritRecipes(models.Model):
    """Модель для реализации функционала избранных рецептов."""
    user = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='who_added',
        verbose_name='Добавивший',
        help_text='Тот, кто добавил рецепт в избранное'
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorit_recipe',
        verbose_name='Рецепт',
        help_text='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_set_favorites_recipes'
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCartRecipes(models.Model):
    """Модель для реализации функционала списка покупок."""
    user = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_owner',
        verbose_name='Владелец корзины',
        help_text='Тот, кто добавил рецепт в корзину'
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        verbose_name='Рецепт',
        help_text='Рецепт в корзину'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_set_cart_recipes'
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe} в корзине у {self.user}'
