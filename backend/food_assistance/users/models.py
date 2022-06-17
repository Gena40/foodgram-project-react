from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ForeignKey


class User(AbstractUser):
    """Модель пользователя, расширенная полем с избранными рецептами."""
    favorite_recipes = models.ManyToManyField(
        'cookbook.Recipe',
        through='cookbook.FavoritRecipes',
        blank=True,
        related_name='favorite_recipes',
        verbose_name='Избранные рецепты',
        help_text='Избранные рецепты'
    )
    shopping_cart_recipes = models.ManyToManyField(
        'cookbook.Recipe',
        through='cookbook.ShoppingCartRecipes',
        blank=True,
        related_name='shopping_cart_recipes',
        verbose_name='Рецепты в корзине',
        help_text='Рецепты в корзине'
    )


class Follow(models.Model):
    """Модель для реализации функционала подписок."""
    user = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик'
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        )

    def __str__(self) -> str:
        return f'Пользователь {self.user} подписан на автора {self.author}'
