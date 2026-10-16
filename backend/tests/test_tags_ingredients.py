"""Tests for tags and ingredient search."""

import pytest

pytestmark = pytest.mark.django_db


def test_tags_list_without_pagination(anon_client, tags):
    response = anon_client.get('/api/tags/')
    assert response.status_code == 200
    assert [tag['slug'] for tag in response.data] == ['breakfast', 'dinner']


def test_tags_are_read_only(author_client):
    response = author_client.post(
        '/api/tags/', {'name': 'Lunch', 'slug': 'lunch'}
    )
    assert response.status_code == 405


def test_search_ingredients_by_name_prefix(anon_client, ingredients):
    response = anon_client.get('/api/ingredients/', {'name': 'mi'})
    assert response.status_code == 200
    assert [item['name'] for item in response.data] == ['milk']
