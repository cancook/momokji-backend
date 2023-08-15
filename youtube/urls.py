from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'youtube'

router = DefaultRouter()
router.register('creator-list', views.YouTubeCreatorViewSet, basename='creator')
router.register('detail', views.YouTubeDetailViewSet, basename='detail')
router.register('recommended-list', views.RecommendedYouTubeViewSet, basename='recommended')
router.register('category-list', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('youtube/', include(router.urls)),
    path('health_check', views.HealthCheck.as_view(), name='health_check')
]
