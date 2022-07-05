from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.pagination import CustomPagination
from cookbook.filters import RecipeFilter, CustomSearchFilter
from users.models import Follow
from cookbook.models import (FavoritRecipes, Ingredient, Recipe,
                             RecipeIngredients, ShoppingCartRecipes, Tag)
from cookbook.permissions import IsAuthor
from cookbook.serializers import (DownloadShoppingCartSerializer,
                                  FavoriteRecipesSerializer,
                                  IngredientSerializer,
                                  RecipesCreateSerializer, RecipesSerializer,
                                  TagSerializer)
from users.serializers import SbscrptSerializer


User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)


class SbscrptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SbscrptSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        current_user = self.request.user
        return User.objects.filter(following__user=current_user)


class SubscribeViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        current_user = request.user
        author_id = int(kwargs.get('id'))
        author = get_object_or_404(User, id=author_id)
        serializer_context = {'current_user': current_user}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            serializer_context['recipes_limit'] = recipes_limit
        serializer = SbscrptSerializer(
            author,
            context=serializer_context
        )
        serializer.validate(author_id)
        follow, not_exists = Follow.objects.get_or_create(
            user=current_user,
            author=author
        )
        if not not_exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'This subscription already exists.'}
            )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=('delete',), detail=False)
    def delete(self, request, id=None):
        current_user = request.user
        serializer_context = {'current_user': current_user}
        author = get_object_or_404(User, id=id)
        serializer = SbscrptSerializer(
            author,
            context=serializer_context
        )
        serializer.validate(int(id))
        if not Follow.objects.filter(user=current_user,
                                     author=author).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Subscription does not exist.'}
            )
        Follow.objects.get(user=current_user,
                           author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipesViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, id=None):
        current_user = request.user
        favorite_recipe = get_object_or_404(Recipe, id=id)
        fav, not_exists = FavoritRecipes.objects.get_or_create(
            user=current_user,
            recipe=favorite_recipe
        )
        if not not_exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Recipe already in favorites.'}
            )
        serializer = FavoriteRecipesSerializer(favorite_recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=('delete',), detail=False)
    def delete(self, request, id=None):
        current_user = request.user
        favorite_recipe = get_object_or_404(Recipe, id=id)
        if not FavoritRecipes.objects.filter(user=current_user,
                                             recipe=favorite_recipe).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Recipe not in favorites.'}
            )
        FavoritRecipes.objects.get(user=current_user,
                                   recipe=favorite_recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        if self.action in ('partial_update', 'destroy'):
            return (IsAuthor(),)

        return (permissions.AllowAny(),)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipesCreateSerializer
        return RecipesSerializer

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        in_cart = self.request.query_params.get('is_in_shopping_cart')
        favorit_queryset = None
        cart_queryset = None
        if self.request.user.is_authenticated:
            if is_favorited == '1':
                favorit_queryset = self.request.user.favorite_recipes.all()
            elif is_favorited == '0':
                favorit_queryset = Recipe.objects.exclude(
                    favorit_recipe__user=self.request.user
                )
            if in_cart == '1':
                cart_queryset = self.request.user.shopping_cart_recipes.all()
            elif in_cart == '0':
                cart_queryset = Recipe.objects.exclude(
                    cart_recipe__user=self.request.user
                )
        if favorit_queryset is not None and cart_queryset is not None:
            return favorit_queryset & cart_queryset
        if favorit_queryset is not None:
            return favorit_queryset
        if cart_queryset is not None:
            return cart_queryset
        return Recipe.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        serializer_out = RecipesSerializer(recipe)
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        serializer_out = RecipesSerializer(recipe)
        return Response(serializer_out.data, status=status.HTTP_200_OK)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, id=None):
        current_user = request.user
        recipe_for_cart = get_object_or_404(Recipe, id=id)
        recipe, not_exists = ShoppingCartRecipes.objects.get_or_create(
            user=current_user,
            recipe=recipe_for_cart
        )
        if not not_exists:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Recipe already in shopping cart.'}
            )
        serializer = FavoriteRecipesSerializer(recipe_for_cart)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=('delete',), detail=False)
    def delete(self, request, id=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        if not ShoppingCartRecipes.objects.filter(user=current_user,
                                                  recipe=recipe).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Recipe not in shopping cart.'}
            )
        ShoppingCartRecipes.objects.get(user=current_user,
                                        recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartViewSet(viewsets.ModelViewSet):
    """
    Обрабатывает запрос на скачивание списка покупок.
    """
    queryset = ShoppingCartRecipes.objects.all()
    serializer_class = DownloadShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        all_ingr_in_cart = RecipeIngredients.objects.filter(
            recipe__cart_recipe__user=request.user).values(
                'ingredient').annotate(Sum('amount'))
        if not all_ingr_in_cart:
            return Response(status=status.HTTP_204_NO_CONTENT)
        ingredients_list = []
        for ingr in all_ingr_in_cart:
            amount = ingr.get('amount__sum')
            ingredient = get_object_or_404(
                Ingredient,
                id=ingr.get('ingredient')
            )
            unit = ingredient.measurement_unit
            name = ingredient.name
            row = f'{name} ({unit}) - {amount}'
            ingredients_list.append(row)
        response = HttpResponse(content_type='text')
        response.write('\n'.join(ingredients_list))
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response
