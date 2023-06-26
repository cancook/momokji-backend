from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from .models import Ingredients
from .serializers import IngredientSerializer


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer