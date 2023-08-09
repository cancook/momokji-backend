from rest_framework import serializers

from .models import Ingredients_Youtube
from youtube.models import YouTube
from .models import CategoryIngredients,Ingredients


class GetCategoryIngredientSerializer(serializers.ModelSerializer):
    categoryName = serializers.CharField(source='name')
    ingredientNameList = serializers.SerializerMethodField()

    class Meta:
        model = CategoryIngredients
        fields = ['categoryName', 'ingredientNameList']

    def get_ingredientNameList(self, obj) -> list:
        return obj.category_ingredients.values_list('name', flat=True)


class GetIngredientDataSerializer(serializers.Serializer):
    nameList = serializers.ListField(child=serializers.CharField(), help_text="재료 리스트")


class WordValidationSerializer(serializers.Serializer):
    word = serializers.CharField(help_text="단어로 검색")


class GetYouTubeFromIngredientSerializer(serializers.ModelSerializer):
    thumbnailURL = serializers.CharField(source='thumbnails')
    playTime = serializers.CharField(source='play_time')
    views = serializers.IntegerField(source='view_count')
    link = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='published')
    link = serializers.SerializerMethodField()

    class Meta:
        model = YouTube
        fields = ['id', 'title', 'thumbnailURL', 'playTime', 'views', 'link', 'createdAt']

    def get_link(self, obj):
        return 'https://www.youtube.com/watch?v=' + obj.url_pk
