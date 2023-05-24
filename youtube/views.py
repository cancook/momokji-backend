from rest_framework.response import Response
from rest_framework import viewsets

from .models import YouTube, Category
from .serializers import 

class RecommendedYoutubeViewSet(viewsets.ModelViewSet):
    queryset = '',
    serializer_class = ''

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ''
    seiralizer_class = ''
