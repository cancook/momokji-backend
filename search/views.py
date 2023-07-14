from django.db import models
from django.db.models import Case, When

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from youtube.models import YouTube
from .models import Ingredients, Ingredients_Youtube
from .serializers import IngredientSerializer, IngredientYouTubeSerializer, WordValidationSerializer


class GetIngredientDataViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer

    @swagger_auto_schema(request_body=GetIngredientDataSerializer)
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        ingredient_list = []

        validated_data = serializer.data
        for data in validated_data:
            target = list(data.values())
            ingredient_list.append(target[0])

        return Response(ingredient_list, status=200)
    

# * 사용자가 입력한 ['정수물, 무'] 데이터를 가져와서 YouTube 데이터를 매칭해서 노출
# * Response youtube_id, Ingredients_id
class IngredientYouTubeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientYouTubeSerializer

    def get_queryset(self):
        serializer = WordValidationSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        word = serializer.validated_data['word']

        if word:
            queryset = self.queryset.filter(name__in=word[0])
            self.queryset = Ingredients_Youtube.objects.filter(ingredients_id__in=queryset)
                
        return self.queryset
    
    @swagger_auto_schema(query_serializer=WordValidationSerializer)
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)