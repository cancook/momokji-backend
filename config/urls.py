from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from config.settings import base

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg       import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="momokji",
        default_version='0.1',
        description="momokji API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="chinup1004@naver.com"),
        license=openapi.License(name="mit"),
    ),
    url='https://momokji.shop/api/',
    # url='http://127.0.0.1:8000/api/',
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('youtube.urls')),
    path('api/', include('search.urls')),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]+ static(base.STATIC_URL, document_root=base.STATIC_ROOT)