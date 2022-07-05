from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from users.serializers import UserSerializer
from cookbook.models import (Ingredient, Recipe, RecipeIngredients,
                             ShoppingCartRecipes, Tag)
from food_assistance.settings import MINIMUM_AMOUNT_OF_INGREDIENT as MIN_AMOUNT

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer для просмотра тегов.
    """
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer для просмотра ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer для просмотра ингредиентов в составе рецепта.
    """
    id = serializers.SerializerMethodField(
        method_name='get_id'
    )
    name = serializers.SerializerMethodField(
        method_name='get_name'
    )
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )
    amount = serializers.SerializerMethodField(
        method_name='get_amount'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )

    def get_id(self, obj):
        """
        Возвращает id ингредиента в рецепте.
        """
        return obj.ingredient.id

    def get_name(self, obj):
        """
        Возвращает название ингредиента в рецепте.
        """
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        """
        Возвращает единицу измерения ингредиента в рецепте.
        """
        return obj.ingredient.measurement_unit

    def get_amount(self, obj):
        """
        Возвращает количество ингредиента в рецепте.
        """
        return obj.amount


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_user = request.user
        try:
            current_user.shopping_cart_recipes.get(
                id=obj.id
            )
            return True
        except Exception:
            return False

    def get_ingredients(self, recipe_obj):
        ingr_in_recipe_obj = recipe_obj.igredients_in_recipe.all()
        return IngredientInRecipeSerializer(
            instance=ingr_in_recipe_obj,
            read_only=True,
            many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_user = request.user
        try:
            current_user.favorite_recipes.get(
                id=obj.id
            )
            return True
        except Exception:
            return False


class IngredientInCreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer для просмотра ингредиентов в составе рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount'
        )

    def validate_amount(self, value):
        """
        Проверка amount >= MINIMUM_AMOUNT_OF_INGREDIENT.
        """
        if value < MIN_AMOUNT:
            raise serializers.ValidationError(
                detail=f'Amount of ingredients should not be < {MIN_AMOUNT}'
            )
        return value


class RecipesCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientInCreateUpdateRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for full_ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=full_ingredient.get('id'),
                amount=full_ingredient.get('amount')
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        empty_required_fields = dict()
        required_fields = (
            'ingredients', 'name', 'cooking_time', 'text', 'tags'
        )
        for field in required_fields:
            if validated_data.get(field) is None:
                empty_required_fields[field] = 'This field is required.'
        if empty_required_fields:
            raise serializers.ValidationError(detail=empty_required_fields)
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        if tags_data:
            instance.tags.set(tags_data)
        RecipeIngredients.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                ingredient=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount']
            )
        instance.save()
        return instance


class DownloadShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCartRecipes
        fields = ('user', 'resipe')
