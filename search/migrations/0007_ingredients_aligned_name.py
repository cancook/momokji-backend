# Generated by Django 4.2.4 on 2023-08-17 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0006_alter_ingredients_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredients',
            name='aligned_name',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]