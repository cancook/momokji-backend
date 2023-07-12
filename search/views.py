from django.db import models
from django.db.models import Case, When

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from youtube.models import YouTube
from .models import Ingredients, Ingredients_Youtube
from .serializers import GetYouTubeFromIngredientSerializer, WordValidationSerializer


class GetYouTubeFromIngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = GetYouTubeFromIngredientSerializer

    def get_queryset(self):
        serializer = WordValidationSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        word = serializer.validated_data['word']

        if word:
            queryset = self.queryset.filter(name__icontains=word).annotate(
                starts_with=Case(
                    When(name__istartswith=word, then=0),
                    default=1,
                    output_field=models.IntegerField(),
                )
            ).order_by('starts_with', 'name')
        return queryset
    
    @swagger_auto_schema(query_serializer=WordValidationSerializer)
    def list(self, request):
        queryset = Ingredients_Youtube.objects.filter(
            ingredients_id__in=self.get_queryset().values('id')).values('youtube_id')
        queryset = YouTube.objects.filter(id__in=queryset)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)