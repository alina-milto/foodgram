"""Admin site configuration for recipes and related models."""

from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    """Edit recipe ingredients right on the recipe page."""

    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Admin for recipes with ingredients inline and favorites count."""

    list_display = ('name', 'author', 'favorites_count',)
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)

    @admin.display(description='in favorites')
    def favorites_count(self, obj):
        """Return how many users added the recipe to favorites."""
        return obj.favorited_by.count()


class IngredientAdmin(admin.ModelAdmin):
    """Admin for ingredients with search by name."""

    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
