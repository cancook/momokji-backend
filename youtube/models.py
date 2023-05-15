from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class YouTube(models.Model):
    url_pk = models.CharField(max_length=64)
    channel_id = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnails = models.URLField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    published = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        return f"{self.url_pk}의 {self.title}"


class Category(BaseModel):
    category_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=128)

    def __init__(self, *args, **kwargs):
        return f"{self.category_id}의 {self.title}"
