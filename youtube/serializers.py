from rest_framework import serializers
from .models import Creator, YouTube, Category

class CreatorSerializer(serializers.ModelSerializer):
    thumbnail = serializers.CharField(source='thumbnail_url')

    class Meta:
        model = Creator
        fields = ['id', 'name', 'thumbnail']


class RecommendedYouTubeSerializer(serializers.ModelSerializer):
    thumbnailURL = serializers.CharField(source='thumbnails')
    playTime = serializers.CharField(source='play_time')
    link = serializers.SerializerMethodField()

    class Meta:
        model = YouTube
        fields = ['id', 'thumbnailURL', 'playTime', 'link']
    
    def get_link(self, obj):
        return 'https://www.youtube.com/watch?v=' + obj.url_pk

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


class YoutubeAndCreatorSeiralizer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()

    class Meta:
        model = YouTube
        fields = ['video', 'creator']

    def get_video(self, obj):
        serializer = YouTubeSerializer(obj)
        return serializer.data
    
    def get_creator(self, obj):
        serializer = CreatorSerializer(obj.creator)
        return serializer.data

class CategoryListSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['title', 'data']

    def get_data(self, obj):
        serializer = YoutubeAndCreatorSeiralizer(obj.youtube_set.all(), many=True)
        return serializer.data