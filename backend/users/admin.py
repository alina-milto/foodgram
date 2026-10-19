"""Admin site configuration for users and subscriptions."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for users based on Django's built-in user admin.

    The built-in admin hashes passwords when users are created or
    changed, so passwords are never stored as plain text.
    """

    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff')
    search_fields = ('email', 'username')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Avatar', {'fields': ('avatar',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'first_name',
                'last_name',
                'usable_password',
                'password1',
                'password2',
            ),
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for subscriptions with search by user."""

    list_display = ('follower', 'following')
    search_fields = ('follower__username', 'following__username')
