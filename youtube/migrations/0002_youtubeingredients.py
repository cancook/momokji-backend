# Generated by Django 4.2.3 on 2023-07-06 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='YouTubeIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('is_valid', models.BooleanField(default=False)),
                ('youtube', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube.youtube')),
            ],
            options={
                'db_table': 'youtube_ingredients',
            },
        ),
    ]