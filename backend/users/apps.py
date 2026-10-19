"""Application config for users and subscriptions."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration of the ``users`` application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
