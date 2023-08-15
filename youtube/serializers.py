from rest_framework import serializers
from .models import Creator, YouTube, Category
from search.models import Ingredients

class CreatorSerializer(serializers.ModelSerializer):
    thumbnail = serializers.CharField(source='thumbnail_url')

    class Meta:
        model = Creator
        fields = ['id', 'name', 'thumbnail']


class YouTubeSerializer(serializers.ModelSerializer):
    thumbnailURL = serializers.CharField(source='thumbnails')
    playTime = serializers.CharField(source='play_time')
    views = serializers.IntegerField(source='view_count')
    link = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='published')

    class Meta:
        model = YouTube
        fields = ['id', 'title', 'thumbnailURL', 'playTime', 'views', 'link', 'createdAt']
    
    def get_link(self, obj):
        return 'https://www.youtube.com/watch?v=' + obj.url_pk


class RecommendedYouTubeSerializer(serializers.ModelSerializer):
    thumbnailURL = serializers.CharField(source='thumbnails')
    playTime = serializers.CharField(source='play_time')
    link = serializers.SerializerMethodField()

    class Meta:
        model = YouTube
        fields = ['id', 'thumbnailURL', 'playTime', 'link']
    
    def get_link(self, obj):
        return 'https://www.youtube.com/watch?v=' + obj.url_pk


class YoutubeAndCreatorSeiralizer(serializers.ModelSerializer):
    video = YouTubeSerializer(source='*')
    creator = CreatorSerializer()

    class Meta:
        model = YouTube
        fields = ['video', 'creator']

class CategoryListSerializer(serializers.ModelSerializer):
    data = YoutubeAndCreatorSeiralizer(many=True, source='youtube_set')

    class Meta:
        model = Category
        fields = ['title', 'data']

    
class YouTubeDetailSerializer(serializers.ModelSerializer):
    urlPk = serializers.CharField(source='url_pk')
    views = serializers.IntegerField(source='view_count')
    createdAt = serializers.DateTimeField(source='published')
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = YouTube
        fields = ['urlPk', 'title', 'description', 'ingredients', 'views', 'createdAt']

    def get_ingredients(self, obj):
        result = obj.ingredients.values_list('name', flat=True)
        return result
    

class YouTubeCreatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Creator
        fields = '__all__'