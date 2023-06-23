from django.contrib import admin
from django.urls import path, include

from config import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/youtube/', include('youtube.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
