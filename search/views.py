from django.db import models
from django.db.models import Case, When

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Ingredients
from .serializers import WordValidationSerializer, IngredientSerializer


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredients.objects.all()

        serializer = WordValidationSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        word = serializer.validated_data['word']

        if word:
            queryset = queryset.filter(name__icontains=word).annotate(
                starts_with=Case(
                    When(name__istartswith=word, then=0),
                    default=1,
                    output_field=models.IntegerField(),
                )
            ).order_by('starts_with', 'name')
        return queryset
    
    @swagger_auto_schema(query_serializer=WordValidationSerializer)
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)