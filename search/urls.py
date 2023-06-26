from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'search'

router = DefaultRouter()
router.register('ingredient-list', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('search/', include(router.urls)),
]
