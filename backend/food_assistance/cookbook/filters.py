from django_filters import FilterSet, rest_framework
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
