from django.db import models

from foodgram.constants import MAX_NAME_LENGTH, MAX_TEXT_LENGTH
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=MAX_NAME_LENGTH,
        verbose_name='тег')
    slug = models.SlugField(
        'Адрес для страницы с тегом',
        max_length=MAX_NAME_LENGTH,
        unique=True,
        help_text=('Укажите адрес для страницы тега. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания')
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = ('name', 'measurement_unit')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор рецепта'
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='рецепт'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='изображение блюда',)
    text = models.TextField(
        'Описание рецепта',
        max_length=MAX_TEXT_LENGTH,
        help_text=(
            f'Описание рецепта, не более {MAX_TEXT_LENGTH} символов.'
        ),)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления (мин.)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент')
    amount = models.PositiveIntegerField(verbose_name='количество ингредиента')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return (
            f'{self.ingredient} - {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='favorite_list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        related_name='favorited_by',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='shopping_list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        related_name='bought_by',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
