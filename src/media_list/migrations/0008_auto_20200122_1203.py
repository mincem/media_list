# Generated by Django 2.2.8 on 2020-01-22 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_list', '0007_movie_imdb_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviecastmember',
            name='role',
            field=models.CharField(max_length=255),
        ),
    ]
