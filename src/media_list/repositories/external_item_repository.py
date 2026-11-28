from django.db import models, transaction
from easy_thumbnails.files import get_thumbnailer


class ExternalItemRepository:
    """Stores the info fetched from an external source, mirroring it.

    create() and update() write the same way: every scalar field is overwritten (a missing or empty value blanks
    it) and every relation is replaced. The cover is the exception: it's only replaced when the data has a new one.

    Subclasses set `model` and `scalar_fields`, and implement `save_relations`.
    """
    model = None
    scalar_fields = ()

    def create(self, **data):
        return self.save(self.model(), **data)  # pylint: disable=not-callable  # Set by subclasses

    def update(self, instance, **data):
        return self.save(instance, **data)

    def save(self, instance, image=None, **data):
        for field_name in self.scalar_fields:
            setattr(instance, field_name, empty_value_for(instance, field_name, data.get(field_name)))
        instance.save()
        self.save_relations(instance, data)
        if image is not None:
            replace_image(instance.image, image)
        return instance

    def save_relations(self, instance, data):
        raise NotImplementedError

    @staticmethod
    def delete(instance):
        """Deletes the info and, once the transaction commits, its cover file."""
        old_image = get_thumbnailer(instance.image) if instance.image else None
        instance.delete()
        if old_image is not None:
            delete_image_on_commit(old_image)


def empty_value_for(instance, field_name, value):
    """Blank text fields can't be null, so an empty value is stored as an empty string."""
    field = instance._meta.get_field(field_name)
    if value is None and not field.null and isinstance(field, (models.CharField, models.TextField)):
        return ""
    return value


def replace_image(field_file, image):
    """Saves the new image, then deletes the old file once the transaction commits.

    Saving always creates a new file (the storage renames it if the name is taken), so the old one would be left behind.
    """
    old_image = get_thumbnailer(field_file) if field_file else None
    field_file.save(**image)
    if old_image is not None and old_image.name != field_file.name:
        delete_image_on_commit(old_image)


def delete_image_on_commit(old_image):
    transaction.on_commit(lambda: delete_image(old_image))


def delete_image(old_image):
    """Deletes an image file along with its easy_thumbnails thumbnails and their cache records.

    `old_image` is a ThumbnailerFieldFile taken while the field still pointed at the image. Its own delete() isn't
    used because it also clears the field on the model instance, which by then points at the new image.
    """
    source_cache = old_image.get_source_cache()
    old_image.delete_thumbnails(source_cache)
    old_image.storage.delete(old_image.name)
    if source_cache is not None:
        source_cache.delete()
