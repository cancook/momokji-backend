from django.db import models
from youtube.models import BaseModel, YouTube


class Ingredients(models.Model):
    name = models.CharField(unique=True, max_length=32)
    # youtube = models.ManyToManyField(YouTube, through="Ingredients_Youtube")
    youtube = models.ManyToManyField(YouTube, related_name="youtube")
    is_valid = models.BooleanField(default=False)

    class Meta:
        db_table = "search_ingredients"

    def __str__(self):
        return f"{self.name}"
    

# class Ingredients_Youtube(BaseModel): #! m2m 중간 역할
#     ingredients = models.ForeignKey(Ingredients)
#     youtube = models.ForeignKey(YouTube)