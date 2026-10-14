"""Root URL configuration of the Foodgram project."""

from django.contrib import admin
from django.urls import include, path

from api.views import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('s/<int:pk>/', redirect_short_link, name='short-link'),
]
