"""Application config for the REST API."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration of the ``api`` application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
