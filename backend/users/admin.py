"""Admin site configuration for users and subscriptions."""

from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    """Admin for users with search by email and username."""

    search_fields = ('email', 'username',)


admin.site.register(Subscription)
admin.site.register(User, UserAdmin)
