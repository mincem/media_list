# Generated by Django 2.2 on 2019-05-04 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_list', '0013_auto_20190501_1907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bakaseries',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='bakaseries',
            name='author',
        ),
        migrations.AddField(
            model_name='bakaseries',
            name='artists',
            field=models.ManyToManyField(related_name='series_as_artist', to='media_list.MangaPerson'),
        ),
        migrations.AddField(
            model_name='bakaseries',
            name='authors',
            field=models.ManyToManyField(related_name='series_as_author', to='media_list.MangaPerson'),
        ),
    ]
