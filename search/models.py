from django.db import models
from youtube.models import BaseModel


class Ingredients(BaseModel):
    name = models.CharField(unique=True, max_length=32)
    is_valid = models.BooleanField(default=False)

    class Meta:
        db_table = "search_ingredients"