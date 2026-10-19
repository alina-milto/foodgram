"""Models for recipes, tags, ingredients, favorites and shopping cart."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.constants import (
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MAX_NAME_LENGTH,
    MAX_TEXT_LENGTH,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
)
from users.models import User


class Tag(models.Model):
    """Recipe tag, for example "Breakfast" or "Dinner"."""

    name = models.CharField(
        unique=True,
        max_length=MAX_NAME_LENGTH,
        verbose_name='name')
    slug = models.SlugField(
        'slug',
        max_length=MAX_NAME_LENGTH,
        unique=True,
        help_text=('Tag page address. Use only Latin letters, digits, '
                   'hyphens and underscores.')
    )

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient with its measurement unit, loaded from a CSV file."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='name'
    )
    measurement_unit = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='measurement unit'
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe published by a user."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='author'
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='name'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='image',)
    text = models.TextField(
        'description',
        max_length=MAX_TEXT_LENGTH,
        help_text=(
            f'Recipe description, up to {MAX_TEXT_LENGTH} characters.'
        ),)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='cooking time (min)',
        validators=(
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME),
        ),
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='publication date'
    )

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Ingredient used in a recipe, with its amount."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ingredient')
    amount = models.PositiveIntegerField(
        verbose_name='amount',
        validators=(
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT),
        ),
    )

    class Meta:
        verbose_name = 'recipe ingredient'
        verbose_name_plural = 'recipe ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """Recipe added to a user's favorites."""

    user = models.ForeignKey(
        User,
        verbose_name='user',
        related_name='favorite_list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        related_name='favorited_by',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} in favorites of {self.user}'


class ShoppingCart(models.Model):
    """Recipe added to a user's shopping cart."""

    user = models.ForeignKey(
        User,
        verbose_name='user',
        related_name='shopping_list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        related_name='bought_by',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'shopping cart item'
        verbose_name_plural = 'shopping cart items'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} in shopping cart of {self.user}'
