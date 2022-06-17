from django.contrib import admin
from cookbook.models import (FavoritRecipes, Ingredient, Recipe,
                             RecipeIngredients, ShoppingCartRecipes, Tag)


class FavoritRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')
    list_display_links = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'


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
    readonly_fields = ('favorites_counter',)
    filter_horizontal = ('tags', 'ingredients')
    search_fields = ('name', 'text')
    list_filter = ('author', 'name', 'tags')
    list_display_links = ('name',)
    empty_value_display = '-пусто-'

    def favorites_counter(self, obj):
        return len(obj.favorite_recipes.all())


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(FavoritRecipes, FavoritRecipesAdmin)
admin.site.register(ShoppingCartRecipes, ShoppingCartRecipesAdmin)
