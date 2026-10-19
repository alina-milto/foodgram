"""Tests for recipes: CRUD, permissions, validation and filters."""

import pytest

from recipes.models import Favorite, Recipe

pytestmark = pytest.mark.django_db

RECIPES_URL = '/api/recipes/'


def detail_url(recipe_id):
    """Return the URL of one recipe."""
    return f'{RECIPES_URL}{recipe_id}/'


def test_anonymous_can_list_recipes(anon_client, recipe):
    response = anon_client.get(RECIPES_URL)
    assert response.status_code == 200
    assert response.data['count'] == 1
    result = response.data['results'][0]
    assert result['is_favorited'] is False
    assert result['ingredients'][0]['amount'] == 100


def test_anonymous_cannot_create_recipe(anon_client, recipe_payload):
    response = anon_client.post(RECIPES_URL, recipe_payload, format='json')
    assert response.status_code == 401
    assert not Recipe.objects.exists()


def test_create_recipe(author_client, author, recipe_payload):
    response = author_client.post(
        RECIPES_URL, recipe_payload, format='json'
    )
    assert response.status_code == 201
    recipe = Recipe.objects.get(id=response.data['id'])
    assert recipe.author == author
    assert recipe.recipe_ingredients.count() == 2
    assert response.data['author']['id'] == author.id


@pytest.mark.parametrize('field, value', [
    ('ingredients', []),
    ('tags', []),
    ('cooking_time', 0),
    ('cooking_time', 40000),
])
def test_create_recipe_with_invalid_data(
    author_client, recipe_payload, field, value
):
    recipe_payload[field] = value
    response = author_client.post(
        RECIPES_URL, recipe_payload, format='json'
    )
    assert response.status_code == 400
    assert field in response.data


@pytest.mark.parametrize('amount', [0, -1, 40000])
def test_create_recipe_with_invalid_amount(
    author_client, recipe_payload, amount
):
    recipe_payload['ingredients'][0]['amount'] = amount
    response = author_client.post(
        RECIPES_URL, recipe_payload, format='json'
    )
    assert response.status_code == 400


def test_create_recipe_with_repeated_ingredients(
    author_client, recipe_payload
):
    recipe_payload['ingredients'].append(recipe_payload['ingredients'][0])
    response = author_client.post(
        RECIPES_URL, recipe_payload, format='json'
    )
    assert response.status_code == 400
    assert 'ingredients' in response.data


def test_author_can_update_recipe(author_client, recipe, recipe_payload):
    recipe_payload['name'] = 'Better pancakes'
    response = author_client.patch(
        detail_url(recipe.id), recipe_payload, format='json'
    )
    assert response.status_code == 200
    recipe.refresh_from_db()
    assert recipe.name == 'Better pancakes'
    assert recipe.recipe_ingredients.count() == 2


def test_update_without_ingredients_is_rejected(author_client, recipe):
    response = author_client.patch(
        detail_url(recipe.id), {'name': 'New name'}, format='json'
    )
    assert response.status_code == 400


def test_other_user_cannot_change_recipe(
    reader_client, recipe, recipe_payload
):
    url = detail_url(recipe.id)
    response = reader_client.patch(url, recipe_payload, format='json')
    assert response.status_code == 403
    assert reader_client.delete(url).status_code == 403


def test_author_can_delete_recipe(author_client, recipe):
    response = author_client.delete(detail_url(recipe.id))
    assert response.status_code == 204
    assert not Recipe.objects.exists()


def test_filter_by_tag(anon_client, make_recipe, tags):
    make_recipe(name='Porridge', tag=tags[0])
    make_recipe(name='Steak', tag=tags[1])
    response = anon_client.get(RECIPES_URL, {'tags': 'dinner'})
    names = [item['name'] for item in response.data['results']]
    assert names == ['Steak']


def test_filter_by_author(anon_client, make_recipe, reader):
    make_recipe(name='Mine')
    make_recipe(name='Theirs', recipe_author=reader)
    response = anon_client.get(RECIPES_URL, {'author': reader.id})
    names = [item['name'] for item in response.data['results']]
    assert names == ['Theirs']


def test_filter_favorited(reader_client, reader, make_recipe):
    liked = make_recipe(name='Liked')
    make_recipe(name='Other')
    Favorite.objects.create(user=reader, recipe=liked)
    response = reader_client.get(RECIPES_URL, {'is_favorited': 1})
    results = response.data['results']
    assert [item['name'] for item in results] == ['Liked']
    assert results[0]['is_favorited'] is True


def test_pagination_limit(anon_client, make_recipe):
    for number in range(5):
        make_recipe(name=f'Recipe {number}')
    response = anon_client.get(RECIPES_URL, {'limit': 2})
    assert response.data['count'] == 5
    assert len(response.data['results']) == 2


def test_recipe_list_query_count_does_not_grow(
    reader_client, make_recipe, django_assert_max_num_queries
):
    for number in range(6):
        make_recipe(name=f'Recipe {number}')
    with django_assert_max_num_queries(8):
        response = reader_client.get(RECIPES_URL, {'limit': 6})
    assert len(response.data['results']) == 6


def test_get_short_link(anon_client, recipe):
    response = anon_client.get(f'{detail_url(recipe.id)}get-link/')
    assert response.status_code == 200
    assert response.data['short-link'].endswith(f'/s/{recipe.id}/')


def test_short_link_redirects_to_recipe(anon_client, recipe):
    response = anon_client.get(f'/s/{recipe.id}/')
    assert response.status_code == 302
    assert response.url == f'/recipes/{recipe.id}/'


def test_links_for_missing_recipe_return_404(anon_client):
    assert anon_client.get(f'{detail_url(999)}get-link/').status_code == 404
    assert anon_client.get('/s/999/').status_code == 404
