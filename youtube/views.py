from random import shuffle

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from drf_yasg.utils import swagger_auto_schema

from .models import YouTube, Category
from .serializers import RecommendedYouTubeSerializer, CategoryListSerializer, YouTubeSerializer

class HealthCheck(APIView):
    def get(self, request):
        return Response(True)

class RecommendedYouTubeViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    serializer_class = RecommendedYouTubeSerializer

    def get_queryset(self):
        queryset = list(YouTube.objects.all())
        shuffle(queryset)
        return queryset
    


class CategoryViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = CategoryListSerializer

    def get_queryset(self):
        queryset = Category.objects.prefetch_related('youtube_set').all()
        shuffle(queryset)
        return queryset