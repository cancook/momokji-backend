from django.db import models
from django.db.models import Case, When, Count, Q

from rest_framework.response import Response
from rest_framework import viewsets, mixins, generics
from rest_framework.filters import OrderingFilter

from drf_yasg.utils import swagger_auto_schema

from youtube.models import YouTube
from .filters import CustomOrderingFilter
from .models import CategoryIngredients, Ingredients, Ingredients_Youtube
from .serializers import GetCategoryIngredientSerializer, GetIngredientDataSerializer, GetYouTubeFromIngredientSerializer, WordValidationSerializer


class GetCategoryIngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = GetCategoryIngredientSerializer

    def get_queryset(self):
        queryset = CategoryIngredients.objects.prefetch_related('category_ingredients').all()
        return queryset.order_by('sequence')
    
    @swagger_auto_schema(
            responses={200: GetCategoryIngredientSerializer(many=True)}
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)


class GetIngredientDataViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = GetIngredientDataSerializer

    def get_queryset(self):
        queryset = Ingredients.objects.all()

        serializer = WordValidationSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        word = serializer.validated_data['word']

        if word:
            queryset = queryset.filter(name__icontains=word).exclude(is_valid=False).annotate(
                starts_with=Case(
                    When(is_valid=True, category_id=True, then=0),
                    When(aligned_name__icontains=word, then=0),
                    default=1,
                    output_field=models.IntegerField(),
                )
            ).order_by('starts_with', 'name')
        return queryset
    
    @swagger_auto_schema(
            query_serializer=WordValidationSerializer,
            responses={200: GetIngredientDataSerializer}
    )
    def list(self, request):
        queryset = self.get_queryset()
        lst = []
        for q in queryset:
            if q.starts_with == 0 and q.aligned_name:
                lst.append(q.aligned_name)
            else:
                lst.append(q.name)
        data={'nameList': lst}
        serializer = self.get_serializer(data)

        return Response(serializer.data, status=200)


class GetYouTubeFromIngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = YouTube.objects.all()
    serializer_class = GetYouTubeFromIngredientSerializer

    filter_backends = [CustomOrderingFilter]

    ordering_fields = ['view_count', 'published']

    def get_queryset(self):
        serializer = GetIngredientDataSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        ingredient_name_list = serializer.validated_data['nameList'][0].split(',')

        queryset = YouTube.objects.prefetch_related('ingredients').filter(
            ingredients__name__in=ingredient_name_list
        ).annotate(
            num_references=Count('ingredients')
        ).order_by('-num_references')

        queryset = self.filter_queryset(queryset)

        return queryset
    
    @swagger_auto_schema(
            query_serializer=GetIngredientDataSerializer,
            responses={200: GetYouTubeFromIngredientSerializer(many=True)}
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=200)
