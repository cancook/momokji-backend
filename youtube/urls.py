from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'youtube'

router = DefaultRouter()
router.register('recommended-list', views.RecommendedYouTubeViewSet, basename='recommended')
router.register('category-list', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
