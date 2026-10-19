"""Fixtures for API tests."""

import pytest
from rest_framework.test import APIClient

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User

# A valid 1x1 PNG image encoded as a base64 data URL.
IMAGE = (
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAA'
    'AADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
)


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    """Save uploaded files to a temporary folder during tests."""
    settings.MEDIA_ROOT = tmp_path


def make_user(username):
    """Create a user with predictable credentials."""
    return User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        first_name=username.capitalize(),
        last_name='Tester',
        password='Str0ng-pass!',
    )


def make_client(user=None):
    """Return an API client, authenticated as ``user`` if given."""
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
    return client


@pytest.fixture
def author(db):
    """User who authors recipes."""
    return make_user('author')


@pytest.fixture
def reader(db):
    """Another authenticated user."""
    return make_user('reader')


@pytest.fixture
def anon_client():
    """Client without authentication."""
    return make_client()


@pytest.fixture
def author_client(author):
    """Client authenticated as the recipe author."""
    return make_client(author)


@pytest.fixture
def reader_client(reader):
    """Client authenticated as another user."""
    return make_client(reader)


@pytest.fixture
def tags(db):
    """Two tags."""
    return [
        Tag.objects.create(name='Breakfast', slug='breakfast'),
        Tag.objects.create(name='Dinner', slug='dinner'),
    ]


@pytest.fixture
def ingredients(db):
    """Three ingredients."""
    return [
        Ingredient.objects.create(name='flour', measurement_unit='g'),
        Ingredient.objects.create(name='milk', measurement_unit='ml'),
        Ingredient.objects.create(name='egg', measurement_unit='pcs'),
    ]


@pytest.fixture
def recipe_payload(tags, ingredients):
    """Valid request body for creating a recipe."""
    return {
        'name': 'Pancakes',
        'text': 'Mix everything and fry.',
        'cooking_time': 20,
        'image': IMAGE,
        'tags': [tags[0].id],
        'ingredients': [
            {'id': ingredients[0].id, 'amount': 200},
            {'id': ingredients[1].id, 'amount': 300},
        ],
    }


@pytest.fixture
def make_recipe(author, tags, ingredients):
    """Factory that creates a recipe directly in the database."""
    def _make_recipe(name='Pancakes', recipe_author=None, tag=None,
                     amount=100):
        recipe = Recipe.objects.create(
            author=recipe_author or author,
            name=name,
            text='Text',
            cooking_time=10,
            image='recipes/images/test.png',
        )
        recipe.tags.set([tag or tags[0]])
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredients[0], amount=amount
        )
        return recipe
    return _make_recipe


@pytest.fixture
def recipe(make_recipe):
    """One recipe by the author."""
    return make_recipe()
