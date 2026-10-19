"""Tests for registration, profiles, avatars and subscriptions."""

import pytest

from tests.conftest import IMAGE
from users.models import Subscription

pytestmark = pytest.mark.django_db


def test_register_user(anon_client):
    response = anon_client.post('/api/users/', {
        'email': 'new@example.com',
        'username': 'newbie',
        'first_name': 'New',
        'last_name': 'User',
        'password': 'Str0ng-pass!',
    })
    assert response.status_code == 201
    assert response.data['email'] == 'new@example.com'
    assert 'password' not in response.data


def test_get_token_with_email_and_password(anon_client, author):
    response = anon_client.post('/api/auth/token/login/', {
        'email': author.email,
        'password': 'Str0ng-pass!',
    })
    assert response.status_code == 200
    assert 'auth_token' in response.data


def test_me_requires_authentication(anon_client):
    assert anon_client.get('/api/users/me/').status_code == 401


def test_me_returns_current_user(author_client, author):
    response = author_client.get('/api/users/me/')
    assert response.status_code == 200
    assert response.data['id'] == author.id


def test_set_and_delete_avatar(author_client, author):
    response = author_client.put(
        '/api/users/me/avatar/', {'avatar': IMAGE}, format='json'
    )
    assert response.status_code == 200
    author.refresh_from_db()
    assert author.avatar

    response = author_client.delete('/api/users/me/avatar/')
    assert response.status_code == 204
    author.refresh_from_db()
    assert not author.avatar


def test_subscribe_and_unsubscribe(reader_client, reader, author, recipe):
    url = f'/api/users/{author.id}/subscribe/'

    response = reader_client.post(url)
    assert response.status_code == 201
    assert response.data['is_subscribed'] is True
    assert response.data['recipes_count'] == 1

    assert reader_client.post(url).status_code == 400

    assert reader_client.delete(url).status_code == 204
    assert not Subscription.objects.filter(
        follower=reader, following=author
    ).exists()
    assert reader_client.delete(url).status_code == 400


def test_cannot_subscribe_to_yourself(author_client, author):
    response = author_client.post(f'/api/users/{author.id}/subscribe/')
    assert response.status_code == 400


def test_subscribe_requires_authentication(anon_client, author):
    response = anon_client.post(f'/api/users/{author.id}/subscribe/')
    assert response.status_code == 401


@pytest.mark.parametrize('limit, expected', [
    ('1', 1),
    ('abc', 3),
    ('-1', 3),
])
def test_subscriptions_recipes_limit(
    reader_client, reader, author, make_recipe, limit, expected
):
    for number in range(3):
        make_recipe(name=f'Recipe {number}')
    Subscription.objects.create(follower=reader, following=author)

    response = reader_client.get(
        '/api/users/subscriptions/', {'recipes_limit': limit}
    )
    assert response.status_code == 200
    subscription = response.data['results'][0]
    assert len(subscription['recipes']) == expected
    assert subscription['recipes_count'] == 3
