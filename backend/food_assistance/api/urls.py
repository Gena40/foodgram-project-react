from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import SpecialUserViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', SpecialUserViewSet, basename='user-list')
router.register('tags', TagViewSet, basename='tags-list')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
