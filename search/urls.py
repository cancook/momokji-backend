from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'search'

router = DefaultRouter()
router.register('get-youtube-from-ingredient', views.GetYouTubeFromIngredientViewSet, basename='ingredient-youtube')

urlpatterns = [
    path('search/', include(router.urls)),
]
