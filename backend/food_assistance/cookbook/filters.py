from django_filters import FilterSet, rest_framework
from cookbook.models import Recipe


class RecipeFilter(FilterSet):
    tags = rest_framework.CharFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
