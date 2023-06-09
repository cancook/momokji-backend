from rest_framework.response import Response
from rest_framework import viewsets

from .models import YouTube, Category
from .serializers import RecommendedYouTubeSerializer, CategoryListSerializer

class RecommendedYouTubeViewSet(viewsets.ModelViewSet):
    queryset = YouTube.objects.all()
    serializer_class = RecommendedYouTubeSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('youtube_set').all()
    serializer_class = CategoryListSerializer
