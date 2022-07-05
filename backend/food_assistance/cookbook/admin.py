from django.contrib import admin
from cookbook.forms import RecipeIngredientsFormset
from cookbook.models import (FavoritRecipes, Ingredient, Recipe,
                             RecipeIngredients, ShoppingCartRecipes, Tag)


class FavoritRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = (
        'user__email',
        'user__username',
        'recipe__name'
    )


class ShoppingCartRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = (
        'user__email',
        'user__username',
        'recipe__name'
    )


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = (
        'recipe__name',
        'ingredient__name'
    )
    list_filter = ('recipe',)
    list_display_links = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'


class RecipeIngredientsInline(admin.TabularInline):
    formset = RecipeIngredientsFormset
    model = RecipeIngredients
    extra: int = 1
    verbose_name_plural = 'Ингредиенты'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'cooking_time',
        'created',
        'favorites_counter'
    )
    fields = (
        ('name', 'author'),
        'text',
        'cooking_time'
    )
    inlines = (RecipeIngredientsInline,)
    readonly_fields = ('favorites_counter',)
    filter_horizontal = ('tags', 'ingredients')
    search_fields = ('name', 'text', 'author__email', 'author__username')
    list_filter = ('tags',)
    list_display_links = ('name',)
    empty_value_display = '-пусто-'

    def favorites_counter(self, obj):
        return len(obj.favorite_recipes.all())


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(FavoritRecipes, FavoritRecipesAdmin)
admin.site.register(ShoppingCartRecipes, ShoppingCartRecipesAdmin)
