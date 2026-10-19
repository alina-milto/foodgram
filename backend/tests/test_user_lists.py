"""Tests for favorites and the shopping cart."""

import pytest

from recipes.models import Favorite, ShoppingCart

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('endpoint, model', [
    ('favorite', Favorite),
    ('shopping_cart', ShoppingCart),
])
def test_add_and_remove_recipe(reader_client, reader, recipe,
                               endpoint, model):
    url = f'/api/recipes/{recipe.id}/{endpoint}/'

    response = reader_client.post(url)
    assert response.status_code == 201
    assert response.data['id'] == recipe.id
    assert model.objects.filter(user=reader, recipe=recipe).exists()

    assert reader_client.post(url).status_code == 400

    assert reader_client.delete(url).status_code == 204
    assert not model.objects.filter(user=reader, recipe=recipe).exists()
    assert reader_client.delete(url).status_code == 400


@pytest.mark.parametrize('endpoint', ['favorite', 'shopping_cart'])
def test_lists_require_authentication(anon_client, recipe, endpoint):
    response = anon_client.post(f'/api/recipes/{recipe.id}/{endpoint}/')
    assert response.status_code == 401


def test_add_missing_recipe_returns_404(reader_client):
    response = reader_client.post('/api/recipes/999/favorite/')
    assert response.status_code == 404


def test_download_shopping_cart_sums_amounts(
    reader_client, reader, make_recipe
):
    first = make_recipe(name='First', amount=100)
    second = make_recipe(name='Second', amount=50)
    ShoppingCart.objects.create(user=reader, recipe=first)
    ShoppingCart.objects.create(user=reader, recipe=second)

    response = reader_client.get('/api/recipes/download_shopping_cart/')
    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert 'attachment' in response['Content-Disposition']
    assert response.content.decode() == 'flour (g) - 150\n'


def test_download_shopping_cart_requires_authentication(anon_client):
    response = anon_client.get('/api/recipes/download_shopping_cart/')
    assert response.status_code == 401
