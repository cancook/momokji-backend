from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Creator(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.CharField(max_length=64)

    class Meta:
        db_table = 'youtube_creator'


class YouTube(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    url_pk = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField()
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    published = models.DateTimeField(auto_now_add=True)
    # Format: 24:60:60
    play_time = models.CharField(max_length=10)
    # 어떤 해상도를 저장할지 테스트 해보기
    thumbnail_default_url = models.CharField(max_length=64)
    thumbnail_midium_url = models.CharField(max_length=64)
    thumbnail_high_url = models.CharField(max_length=64)

    class Meta:
        db_table = 'youtube_content'

    def __init__(self, *args, **kwargs):
        return f"{self.url_pk}의 {self.title}"


# Category_Youtube 중간 테이블(중간에 따로 넣어야 할 데이터가 필요하면 생성... 뭐가 있으려나)
class Category_Youtube(models.Model):
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    Youtube = models.ForeignKey(YouTube, on_delete=models.CASCADE)

    class Meta:
        db_table = 'category_youtube'


class Category(BaseModel):
    category_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    youtube = models.ManyToManyField(YouTube, through=Category_Youtube)

    class Meta:
        db_table = 'youtube_recommended_category'

    def __init__(self, *args, **kwargs):
        return f"{self.category_id}의 {self.title}"
