from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

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
