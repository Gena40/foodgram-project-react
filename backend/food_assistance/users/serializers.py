from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from cookbook.models import Recipe

User = get_user_model()


class SpecialUserCreateSerializer(UserCreateSerializer):
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer для профиля пользователя (текущего или по id).
    """
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj) -> bool:
        """
        Проверка подписан ли текущий пользователь на obj.
        """
        current_user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_user = request.user
            if current_user.is_authenticated:
                return obj.following.filter(user=current_user).exists()
        return False


class RecipesSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer для поля recipes в SbscrptSerializer.
    """
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SbscrptSerializer(serializers.ModelSerializer):
    """
    Serializer для просмотра информации о подписках.
    """
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def validate(self, author_id):
        current_user = self.context.get('current_user')
        if current_user.id == author_id:
            raise serializers.ValidationError(
                detail={"errors": "You can't subscribe to yourself."}
            )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = self.context.get('recipes_limit')
        if not recipes_limit and request:
            recipes_limit = request.query_params.get('recipes_limit')
        obj_recipes = obj.recipes.all()
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
            if recipes_limit >= 0:
                obj_recipes = obj_recipes[:recipes_limit]
        return RecipesSimpleSerializer(instance=obj_recipes, many=True).data

    def get_is_subscribed(self, obj) -> bool:
        """
        Проверка подписан ли текущий пользователь на obj.
        """
        current_user = None
        request = self.context.get('request')
        if not request:
            return True
        if request and hasattr(request, 'user'):
            current_user = request.user
        if request.user.is_authenticated:
            return obj.following.filter(user=current_user).exists()
        return False

    def get_recipes_count(self, obj) -> int:
        """
        Возвращает число рецептов пользователя.
        """
        return len(obj.recipes.all())
