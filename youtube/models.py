from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class YouTube(models.Model):
    url_pk = models.CharField(max_length=64, unique=True)
    channel_id = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnails = models.URLField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    published = models.DateTimeField(auto_now_add=True)
    play_time = models.CharField(max_length=8)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['url_pk'],
                name='url_pk')
        ]


class Category(BaseModel):
    category_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=128)

    def __init__(self, *args, **kwargs):
        return f"{self.category_id}의 {self.title}"
