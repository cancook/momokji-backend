from rest_framework import serializers
from .models import Ingredients

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'is_valid']
