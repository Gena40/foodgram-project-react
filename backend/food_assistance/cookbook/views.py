from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.pagination import CustomPagination
from users.models import Follow
from cookbook.filters import RecipeFilter
from cookbook.models import (FavoritRecipes, Ingredient, Recipe,
                             RecipeIngredients, ShoppingCartRecipes, Tag)
from cookbook.permissions import IsAuthor
from cookbook.serializers import (DownloadShoppingCartSerializer,
                                  FavoriteRecipesSerializer,
                                  IngredientSerializer,
                                  RecipesCreateSerializer, RecipesSerializer,
                                  SbscrptSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
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
        if current_user.id == author_id:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': "You can't subscribe to yourself."}
            )
        author = get_object_or_404(User, id=author_id)
        try:
            Follow.objects.create(
                user=current_user,
                author=author
            )
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'This subscription already exists.'}
            )
        serializer_context = {}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            serializer_context['recipes_limit'] = recipes_limit
        serializer = SbscrptSerializer(
            author,
            context=serializer_context)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, id=None):
        current_user = request.user
        if current_user.id == int(id):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': "You can't subscribe to yourself."}
            )
        author = get_object_or_404(User, id=id)
        try:
            follow = Follow.objects.get(
                user=current_user,
                author=author
            )
        except Exception:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': "Subscription does not exist."}
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipesViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, id=None):
        current_user = request.user
        favorite_recipe = get_object_or_404(Recipe, id=id)
        try:
            FavoritRecipes.objects.create(
                user=current_user,
                recipe=favorite_recipe
            )
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': "Recipe already in favorites."}
            )
        serializer = FavoriteRecipesSerializer(favorite_recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, id=None):
        current_user = request.user
        favorite_recipe = get_object_or_404(Recipe, id=id)
        try:
            favorite_recipe_db = FavoritRecipes.objects.get(
                user=current_user,
                recipe=favorite_recipe
            )
        except Exception:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': "Recipe not in favorites."}
            )
        favorite_recipe_db.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        if self.action == 'partial_update':
            return (IsAuthor(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipesCreateSerializer
        return RecipesSerializer

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        if self.request.user.is_authenticated:
            if is_favorited == '1':
                return self.request.user.favorite_recipes.all()
            if is_favorited == '0':
                return Recipe.objects.exclude(
                    favorit_recipe__user=self.request.user
                )
        return super().get_queryset()

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
        try:
            ShoppingCartRecipes.objects.create(
                user=current_user,
                recipe=recipe_for_cart
            )
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': "Recipe already in shopping cart."}
            )
        serializer = FavoriteRecipesSerializer(recipe_for_cart)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, id=None):
        current_user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        try:
            recipe_in_cart = ShoppingCartRecipes.objects.get(
                user=current_user,
                recipe=recipe
            )
        except Exception:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': "Recipe not in shopping cart."}
            )
        recipe_in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartViewSet(viewsets.ModelViewSet):
    """
    Обрабатывает запрос на скачивание списка покупок.
    """
    queryset = ShoppingCartRecipes.objects.all()
    serializer_class = DownloadShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        resipes_in_cart = request.user.shopping_cart_recipes.all()
        if not resipes_in_cart:
            return Response(status=status.HTTP_204_NO_CONTENT)
        ingredients_dict = dict()
        for recipe in resipes_in_cart:
            for ingr_in_recipe in RecipeIngredients.objects.filter(
                recipe=recipe
            ).all():
                inrg_name = ingr_in_recipe.ingredient.name
                if inrg_name not in ingredients_dict:
                    ingredients_dict[inrg_name] = [
                        ingr_in_recipe.amount,
                        ingr_in_recipe.ingredient.measurement_unit
                    ]
                else:
                    ingredients_dict[inrg_name][0] += ingr_in_recipe.amount
        with open('shopping_list.txt', 'w', encoding='utf-8') as file:
            for ingr in ingredients_dict:
                amount = ingredients_dict[ingr][0]
                unit = ingredients_dict[ingr][1]
                row = f'{ingr} ({unit}) - {amount}\n'
                file.write(row)
        with open('shopping_list.txt', 'r', encoding='utf-8') as file:
            response = HttpResponse(file, content_type='text')
            response['Content-Disposition'] = (
                'attachment; filename=shopping_list.txt'
            )
            return response
