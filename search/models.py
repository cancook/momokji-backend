from django.db import models
from youtube.models import BaseModel, YouTube


class CategoryIngredients(models.Model):
    name = models.CharField(max_length=32)
    sequence = models.IntegerField(default=0)

    class Meta:
        db_table = "search_category_ingredients"

    def __str__(self):
        return f"{self.name}"


class Ingredients(models.Model):
    name = models.CharField(unique=True, max_length=255)
    aligned_name = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(CategoryIngredients, related_name="category_ingredients", null=True, default=None, on_delete=models.SET_NULL)
    youtube = models.ManyToManyField(YouTube, related_name="ingredients", through="Ingredients_Youtube")
    is_valid = models.BooleanField(default=False)
    is_not_connected = models.BooleanField(default=False)

    class Meta:
        db_table = "search_ingredients"

    def __str__(self):
        return f"{self.name}"
    

class Ingredients_Youtube(models.Model):
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    youtube = models.ForeignKey(YouTube, on_delete=models.CASCADE)