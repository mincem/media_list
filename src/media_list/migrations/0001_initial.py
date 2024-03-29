# Generated by Django 2.2 on 2019-05-19 21:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BakaSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('baka_id', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(blank=True, max_length=255)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('original_publisher', models.CharField(blank=True, max_length=255)),
                ('english_publisher', models.CharField(blank=True, max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='manga_images/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MangaGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MangaPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MangaSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('alternate_title', models.CharField(blank=True, max_length=255)),
                ('volumes', models.IntegerField(blank=True, null=True)),
                ('has_omnibus', models.BooleanField(default=False)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_read', models.BooleanField(default=False)),
                ('interest', models.IntegerField()),
                ('status', models.CharField(
                    choices=[('U', 'Unknown'), ('N', 'Not Downloaded'), ('D', 'Downloading'), ('R', 'Downloaded Raw'),
                             ('E', 'Edited')], default='U', max_length=1)),
                ('notes', models.TextField(blank=True)),
                ('baka_id', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('baka_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                to='media_list.BakaSeries')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='MangaSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='source_icons/')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MangaURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('url', models.URLField()),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls',
                                             to='media_list.MangaSeries')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='mangaseries',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='media_list.MangaSource'),
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
        migrations.AddField(
            model_name='bakaseries',
            name='genres',
            field=models.ManyToManyField(related_name='series', to='media_list.MangaGenre'),
        ),
    ]
