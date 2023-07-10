from django.db import models
from youtube.models import BaseModel, YouTube


class Ingredients(models.Model):
    name = models.CharField(unique=True, max_length=32)
    youtube = models.ManyToManyField(YouTube, related_name="youtube", through="Ingredients_Youtube")
    is_valid = models.BooleanField(default=False)

    class Meta:
        db_table = "search_ingredients"

    def __str__(self):
        return f"{self.name}"
    

class Ingredients_Youtube(models.Model):
    ingredients = models.ForeignKey(Ingredients, on_delete=models.PROTECT)
    youtube = models.ForeignKey(YouTube, on_delete=models.PROTECT)