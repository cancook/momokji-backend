from random import shuffle

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from drf_yasg.utils import swagger_auto_schema

from .models import YouTube, Category, Creator
from .serializers import RecommendedYouTubeSerializer, CategoryListSerializer, YouTubeDetailSerializer, YouTubeCreatorSerializer


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
    

class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategoryListSerializer

    def get_queryset(self):
        queryset = Category.objects.prefetch_related('youtube').all().order_by('?')
        return queryset
    

class YouTubeDetailViewSet(mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    
    queryset = YouTube.objects.all()
    serializer_class = YouTubeDetailSerializer

    def get_object(self):
        pk = self.kwargs['pk']
        obj = YouTube.objects.get(id=pk)
        return obj
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class YouTubeCreatorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
      
    queryset = Creator.objects.all()
    serializer_class = YouTubeCreatorSerializer
