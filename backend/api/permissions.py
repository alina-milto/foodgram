"""Custom permission classes for the Foodgram API."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Allow read access to everyone and write access only to the author.

    Anonymous users can only use safe methods (GET, HEAD, OPTIONS).
    Authenticated users can create objects, but can change or delete
    only the objects they authored.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
