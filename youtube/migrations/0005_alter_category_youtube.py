# Generated by Django 4.2.4 on 2023-08-20 05:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0004_remove_category_youtube_category_youtube'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='youtube',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category', to='youtube.youtube'),
        ),
    ]
