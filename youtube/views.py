from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from drf_yasg.utils import swagger_auto_schema

from .models import YouTube, Category
from .serializers import RecommendedYouTubeSerializer, CategoryListSerializer, YouTubeSerializer

class HealthCheck(APIView):
    def get(self, request):
        return Response(True)

class RecommendedYouTubeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = YouTube.objects.all()
    serializer_class = RecommendedYouTubeSerializer
    


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('youtube_set').all()
    serializer_class = CategoryListSerializer