from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.exceptions import NotFound
from users.pagination import CustomPagination
from users.serializers import SpecialUserCreateSerializer, UserSerializer

User = get_user_model()


class SpecialUserViewSet(UserViewSet):
    """
    Кастомный ViewSet на основе Djoser-овского для эндпоинтов:
        + api/users/
        + api/users/me
        + api/users/set_password
        + api/users/{id}

    """
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.action == "list":
            return User.objects.all()
        if self.action == 'retrieve':
            return User.objects.all()
        raise NotFound

    def get_serializer_class(self):
        if self.action in ('me', 'list', 'retrieve'):
            return UserSerializer
        if self.action == 'create':
            return SpecialUserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        raise NotFound
