"""Filters for ingredient search and the recipe list."""

from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Search ingredients by the beginning of their name."""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Filter recipes by tags, author, favorites and shopping cart."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def _filter_by_user_relation(self, queryset, value, related_name):
        """Keep recipes linked to the current user via ``related_name``.

        Anonymous users and a false filter value get the queryset
        unchanged.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                **{f'{related_name}__user': self.request.user}
            )
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Keep only recipes in the current user's favorites."""
        return self._filter_by_user_relation(queryset, value, 'favorited_by')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Keep only recipes in the current user's shopping cart."""
        return self._filter_by_user_relation(queryset, value, 'bought_by')
