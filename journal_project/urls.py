"""
URL configuration for journal_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('journal.urls')),
    # Serve favicon.ico at root URL - browsers automatically request /favicon.ico
    # Redirect to the static file location served by WhiteNoise
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True), name='favicon'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

