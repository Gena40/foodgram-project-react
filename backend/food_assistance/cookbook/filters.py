from django_filters import FilterSet, rest_framework
from rest_framework import filters
from cookbook.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')


class CustomSearchFilter(filters.SearchFilter):
    search_param = 'name'
