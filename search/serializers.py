from rest_framework import serializers
from .models import Ingredients

class WordValidationSerializer(serializers.Serializer):
    word = serializers.CharField(help_text="단어로 검색")

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ['name']
