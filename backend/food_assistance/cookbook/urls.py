from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import SpecialUserViewSet
from cookbook.views import (DownloadShoppingCartViewSet,
                            FavoriteRecipesViewSet, IngredientViewSet,
                            RecipesViewSet, SbscrptViewSet,
                            ShoppingCartViewSet, SubscribeViewSet, TagViewSet)

app_name = 'cookbook'

router = DefaultRouter()
router.register(
    'users/subscriptions',
    SbscrptViewSet,
    basename='subscriptions'
)
router.register('users', SpecialUserViewSet, basename='users-list')
router.register('tags', TagViewSet, basename='tags-list')
router.register('ingredients', IngredientViewSet, basename='ingredients-list')
router.register(
    r'users/(?P<id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)
router.register(
    'recipes/download_shopping_cart',
    DownloadShoppingCartViewSet,
    basename='download_shopping_cart'
)
router.register(
    r'recipes/(?P<id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)
router.register(
    r'recipes/(?P<id>\d+)/favorite',
    FavoriteRecipesViewSet,
    basename='favorite'
)
router.register('recipes', RecipesViewSet, basename='recipes-list')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
