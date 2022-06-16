from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """Проверка авторства."""
    def has_object_permission(self, request, view, obj):
        return (request.user == obj.author)
