"""Serializers for users, subscriptions, tags, ingredients and recipes."""

from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from foodgram.constants import (
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User
from .fields import Base64ImageField


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Register a new user."""

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )


class UserSerializer(DjoserUserSerializer):
    """Show a user profile with subscription status and avatar."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        """Return True if the current user is subscribed to ``obj``."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=request.user,
            following=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Show a tag."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Show an ingredient with its measurement unit."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Show an ingredient of a recipe together with its amount."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Show a recipe with author, tags, ingredients and user flags."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def is_in_user_list(self, obj, model):
        """Return True if the current user has ``obj`` in ``model`` list.

        ``model`` is a user-recipe relation such as ``Favorite`` or
        ``ShoppingCart``. Anonymous users always get False.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        """Return True if the recipe is in the user's favorites."""
        return self.is_in_user_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        """Return True if the recipe is in the user's shopping cart."""
        return self.is_in_user_list(obj, ShoppingCart)


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Accept an ingredient id and amount when saving a recipe."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Create and update recipes.

    Ingredients and tags are required on every write, including partial
    updates, because the recipe is saved together with them.
    """

    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        """Check that ingredients and tags are present and unique."""
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'At least one ingredient is required.'}
            )
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'At least one tag is required.'}
            )
        ingredient_ids = [item['id'] for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ingredients must not repeat.'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Tags must not repeat.'}
            )
        return data

    def set_tags_and_ingredients(self, recipe, tags, ingredients):
        """Attach tags and create ingredient rows for the recipe."""
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
        ) for ingredient in ingredients])

    def create(self, validated_data):
        """Create a recipe authored by the current user."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.set_tags_and_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Update a recipe, replacing its tags and ingredients."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        self.set_tags_and_ingredients(instance, tags, ingredients)
        return instance

    def to_representation(self, instance):
        """Return the saved recipe in the read format."""
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Show a short version of a recipe (for lists and subscriptions)."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    """Show an author the user is subscribed to, with their recipes."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """Return the author's recipes, limited by ``recipes_limit``."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeMinifiedSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """Return the total number of the author's recipes."""
        return obj.recipes.count()
