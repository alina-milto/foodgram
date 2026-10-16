"""API views for users, subscriptions, tags, ingredients and recipes."""

from django.db.models import Count, Exists, OuterRef, Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeMinifiedSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
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


def redirect_short_link(request, pk):
    """Redirect a short link ``/s/<pk>/`` to the recipe page."""
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(f'/recipes/{recipe.pk}/')


def annotate_is_subscribed(queryset, user):
    """Add ``is_subscribed`` to users: does ``user`` follow each of them."""
    if not user.is_authenticated:
        return queryset
    return queryset.annotate(
        is_subscribed=Exists(
            Subscription.objects.filter(
                follower=user,
                following=OuterRef('pk'),
            )
        )
    )


class UserApiViewSet(UserViewSet):
    """Djoser user endpoints extended with avatar and subscriptions."""

    def get_permissions(self):
        """Allow only authenticated users to use the ``me`` endpoint."""
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_queryset(self):
        """Return users annotated with the subscription status."""
        return annotate_is_subscribed(
            super().get_queryset(), self.request.user
        )

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[
            IsAuthenticated
        ],
    )
    def avatar(self, request):
        """Set (PUT) or delete (DELETE) the current user's avatar."""
        user = request.user
        if request.method == 'PUT':
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        permission_classes=[
            IsAuthenticated
        ],
    )
    def subscribe(self, request, id=None):
        """Subscribe to (POST) or unsubscribe from (DELETE) an author."""
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            follower=request.user,
            following=author
        )
        is_subscribed = subscription.exists()
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'You cannot subscribe to yourself.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if is_subscribed:
                return Response(
                    {'errors': 'You are already subscribed to this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(
                follower=request.user,
                following=author
            )
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not is_subscribed:
            return Response(
                {'errors': 'You are not subscribed to this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Return a paginated list of authors the user is subscribed to."""
        authors = annotate_is_subscribed(
            User.objects.filter(followers__follower=request.user),
            request.user,
        ).annotate(
            recipes_count=Count('recipes'),
        ).prefetch_related('recipes').order_by('username')
        pages = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Read-only list of tags, without pagination."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Read-only list of ingredients with search by name prefix."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Recipes CRUD plus favorites, shopping cart and short links.

    Anyone can read recipes; only authenticated users can create them,
    and only the author can change or delete a recipe.
    """

    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Return recipes with related data loaded in few queries.

        Tags, ingredients and authors are prefetched. For authenticated
        users each recipe is annotated with ``is_favorited`` and
        ``is_in_shopping_cart``, and each author with ``is_subscribed``.
        """
        user = self.request.user
        queryset = Recipe.objects.prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
            Prefetch(
                'author',
                queryset=annotate_is_subscribed(User.objects.all(), user),
            ),
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                ),
            )
        return queryset

    def get_serializer_class(self):
        """Use the read serializer for reading, the write one otherwise."""
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def add_or_remove(self, request, pk, model):
        """Add a recipe to (POST) or remove it from (DELETE) a user list.

        ``model`` is the user-recipe relation to change, such as
        ``Favorite`` or ``ShoppingCart``.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        relation = model.objects.filter(user=request.user, recipe=recipe)
        in_list = relation.exists()
        if request.method == 'POST':
            if in_list:
                return Response(
                    {'errors': 'The recipe is already in this list.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not in_list:
            return Response(
                {'errors': 'The recipe is not in this list.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Add the recipe to or remove it from favorites."""
        return self.add_or_remove(request, pk, Favorite)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[
            IsAuthenticated
        ],
    )
    def shopping_cart(self, request, pk=None):
        """Add the recipe to or remove it from the shopping cart."""
        return self.add_or_remove(request, pk, ShoppingCart)

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Return a text file with ingredients from the shopping cart.

        Amounts of the same ingredient from different recipes are summed.
        """
        ingredients = RecipeIngredient.objects.filter(
            recipe__bought_by__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )
        text = ''
        for item in ingredients:
            text += (
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}\n"
            )
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Return a short link to the recipe."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.pk}/')
        return Response({'short-link': short_link})
