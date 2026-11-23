from django.db import migrations, models

MODELS = ("MangaSeries", "BakaSeries")


def merge_code_into_id(apps, _schema_editor):
    """Forward: baka_id becomes the single identifier; prefer the alphanumeric code when present."""
    for model_name in MODELS:
        model = apps.get_model("media_list", model_name)
        for item in model.objects.exclude(baka_code__isnull=True).exclude(baka_code=""):
            item.baka_id = item.baka_code
            item.save(update_fields=["baka_id"])


def split_code_from_id(apps, _schema_editor):
    """Reverse: move non-numeric IDs back to baka_code so baka_id can become an integer again."""
    for model_name in MODELS:
        model = apps.get_model("media_list", model_name)
        for item in model.objects.exclude(baka_id__isnull=True).exclude(baka_id=""):
            if not item.baka_id.isdigit():
                item.baka_code = item.baka_id
                item.baka_id = None
                item.save(update_fields=["baka_id", "baka_code"])


class Migration(migrations.Migration):

    dependencies = [
        ('media_list', '0011_alter_mangaurl_options_alter_movieurl_options_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bakaseries',
            name='id_and_code_not_both_null',
        ),
        migrations.AlterField(
            model_name='mangaseries',
            name='baka_id',
            field=models.CharField(blank=True, max_length=63, null=True),
        ),
        migrations.AlterField(
            model_name='bakaseries',
            name='baka_id',
            field=models.CharField(blank=True, max_length=63, null=True),
        ),
        migrations.RunPython(merge_code_into_id, split_code_from_id),
        migrations.RemoveField(
            model_name='mangaseries',
            name='baka_code',
        ),
        migrations.RemoveField(
            model_name='bakaseries',
            name='baka_code',
        ),
        migrations.AlterField(
            model_name='mangaseries',
            name='baka_id',
            field=models.CharField(
                blank=True, max_length=63, null=True,
                help_text='Mangaupdates ID: either an old numeric ID or a new alphanumeric code',
            ),
        ),
        migrations.AlterField(
            model_name='bakaseries',
            name='baka_id',
            field=models.CharField(max_length=63),
        ),
    ]
