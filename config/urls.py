from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from config import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg       import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="self-dining",
        default_version='0.1',
        description="self-dining API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="chinup1004@naver.com"),
        license=openapi.License(name="mit"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

from config import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('youtube.urls')),

    path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
