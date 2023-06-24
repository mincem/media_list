# Generated by Django 2.2.8 on 2019-12-26 00:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('media_list', '0002_auto_20191005_2249'),
    ]

    operations = [
        migrations.CreateModel(
            name='MangaKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='mangaseries',
            name='status',
            field=models.CharField(choices=[('U', 'Unknown Status'), ('N', 'Not Downloaded'), ('D', 'Downloading'),
                                            ('R', 'Downloaded Raw'), ('E', 'Edited Complete'),
                                            ('I', 'Edited Incomplete')], default='U', max_length=1),
        ),
        migrations.CreateModel(
            name='MangaSeriesKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('baka_series',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weighed_keywords',
                                   to='media_list.BakaSeries')),
                ('keyword',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media_list.MangaKeyword')),
            ],
            options={
                'ordering': ['-score'],
            },
        ),
        migrations.AddField(
            model_name='bakaseries',
            name='keywords',
            field=models.ManyToManyField(related_name='series', through='media_list.MangaSeriesKeyword',
                                         to='media_list.MangaKeyword'),
        ),
    ]
