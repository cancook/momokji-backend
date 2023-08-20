import json

from rest_framework import serializers

from youtube.models import YouTube, Creator
from youtube.serializers import YouTubeSerializer, CreatorSerializer
from .models import CategoryIngredients


class GetCategoryIngredientSerializer(serializers.ModelSerializer):
    categoryName = serializers.CharField(source='name')
    ingredientNameList = serializers.SerializerMethodField()

    class Meta:
        model = CategoryIngredients
        fields = ['sequence', 'categoryName', 'ingredientNameList']

    def get_ingredientNameList(self, obj) -> list:
        # TODO obj 에 아래의 제약조건이 없어 '찌용돼지고기'가 나오고 있다.
        # queryset = queryset.filter(name__icontains=word).exclude(is_valid=False).annotate(
        #                 starts_with=Case(
        #                     When(is_valid=True, category_id=True, then=0),
        #                     When(aligned_name__icontains=word, then=0),
        #                     default=1,
        #                     output_field=models.IntegerField(),
        #                 )
        #             ).order_by('starts_with', 'name')
        return obj.category_ingredients.values_list('name', flat=True)


class GetIngredientDataSerializer(serializers.Serializer):
    nameList = serializers.ListField(child=serializers.CharField(), help_text="재료 리스트")


class WordValidationSerializer(serializers.Serializer):
    word = serializers.CharField(help_text="단어로 검색")


class GetYouTubeFromIngredientSerializer(serializers.ModelSerializer):
    video = YouTubeSerializer(source='*')
    creator = CreatorSerializer()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = YouTube
        fields = ['video', 'creator', 'ingredients']

    def get_ingredients(self, obj):
        return obj.ingredients.values_list('name', flat=True)