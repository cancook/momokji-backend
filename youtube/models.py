from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Creator(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.URLField(max_length=255)

    class Meta:
        db_table = 'youtube_creator'

    def __str__(self):
        return f"{self.name}"


class YouTube(models.Model):
    url_pk = models.CharField(unique=True, max_length=64)
    channel_id = models.CharField(max_length=64)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, null=True, default=None)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnails = models.URLField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    published = models.DateTimeField(auto_now_add=True)
    play_time = models.CharField(max_length=8)

    class Meta:
        db_table = 'youtube'
        constraints = [
            models.UniqueConstraint(
                fields=['url_pk'],
                name='url_pk')
        ]

    def __str__(self):
        return f"{self.url_pk}"


class YouTubeIngredients(models.Model):
    youtube = models.ForeignKey(YouTube, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, unique=True)
    is_valid = models.BooleanField(default=False)

    class Meta:
        db_table = "youtube_ingredients"


class Category(BaseModel):
    category_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    youtube = models.ManyToManyField(YouTube, through="Category_Youtube", related_name='youtube')

    class Meta:
        db_table = 'category'

    def __str__(self, *args, **kwargs):
        return f"{self.title}"


# Category_Youtube 중간 테이블(중간에 따로 넣어야 할 데이터가 필요하면 생성... 뭐가 있으려나)
class Category_Youtube(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    youtube = models.ForeignKey(YouTube, on_delete=models.CASCADE)

    class Meta:
        db_table = 'category_youtube'
