"""
URL configuration for journal_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import FileResponse
import os

def serve_favicon(request):
    """Serve favicon.ico directly from staticfiles directory for maximum compatibility"""
    favicon_path = os.path.join(settings.STATIC_ROOT, 'images', 'favicon.ico')
    if os.path.exists(favicon_path):
        return FileResponse(open(favicon_path, 'rb'), content_type='image/x-icon')
    # Fallback: redirect to static URL served by WhiteNoise
    return RedirectView.as_view(url='/static/images/favicon.ico', permanent=False)(request)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('journal.urls')),
    # Serve favicon.ico at root URL - browsers automatically request /favicon.ico
    # Using direct file serving for maximum compatibility with WhiteNoise
    path('favicon.ico', serve_favicon, name='favicon'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
