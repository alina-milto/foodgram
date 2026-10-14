"""Application config for recipes."""

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Configuration of the ``recipes`` application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
