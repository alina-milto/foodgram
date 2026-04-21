from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username',)


admin.site.register(Subscription)
admin.site.register(User, UserAdmin)
