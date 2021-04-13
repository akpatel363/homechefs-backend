from django_filters import rest_framework as filters
from .models import Recipe


class RecipeFilter(filters.FilterSet):
    cooking_time = filters.RangeFilter()
    created = filters.DateRangeFilter()
    stars = filters.RangeFilter()
    tags = filters.CharFilter('tags', 'name__exact')

    class Meta:
        model = Recipe
        fields = ('food_type', 'cooking_time', 'created', 'stars', 'tags')
