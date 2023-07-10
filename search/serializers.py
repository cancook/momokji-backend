from rest_framework import serializers

from .models import Ingredients, Ingredients_Youtube
from youtube.models import YouTube

class WordValidationSerializer(serializers.Serializer):
    word = serializers.ListField(
        child=serializers.CharField(),
        help_text="사용자가 입력한 단어로 유튜브 url_pk 검색"
    )

class IngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingredients
        fields = ['name']


class IngredientYouTubeSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField()

    class Meta:
        model = Ingredients_Youtube
        fields = ['ingredients_id', 'youtube_id', 'link']

    def get_link(self, obj):
        url_pk = YouTube.objects.get(id=obj.youtube_id).url_pk
        return 'https://www.youtube.com/watch?v=' + url_pk
    
    # def to_representation(self, instance):
    #     data = super(IngredientYouTubeSerializer, self).to_representation(instance)

    #     response_dict = dict()
    #     response_dict = {
    #         'ingredients_id': instance.ingredients_id,
    #         'youtube_id': instance.youtube_id,
    #         'link': data['link']
    #     }
    #     return response_dict
