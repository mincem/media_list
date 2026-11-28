from django.db import models

from ..utils import ColorPicker


class TimestampedModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NamedModel(models.Model):
    class Meta:
        abstract = True
        ordering = ('name',)

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.name)


class PersonManager(models.Manager):
    def from_credit(self, external_id, name):
        """Finds or creates the person behind a credit from an external source.

        A person is found by external ID first. Failing that, a person stored without an ID and with the same name is
        taken as the same person and given the ID, but only if exactly one matches: names aren't unique, so with
        several matches there's no telling which one it is. Otherwise a new person is created.

        A credit without an ID can only be matched by name, so it reuses the first person with that name and no ID.

        The stored name is kept as is: sources may spell one person's name differently across credits.
        """
        id_field = self.model.external_id_field
        if external_id is not None:
            person = self.filter(**{id_field: external_id}).first()
            if person is not None:
                return person
        id_less_namesakes = self.filter(**{id_field: None, "name": name}).order_by("pk")
        if external_id is None:
            person = id_less_namesakes.first()
            return person if person is not None else self.create(name=name)
        matches = list(id_less_namesakes[:2])
        if len(matches) == 1:
            person = matches[0]
            setattr(person, id_field, external_id)
            person.save()
            return person
        return self.create(**{id_field: external_id, "name": name})


class Person(TimestampedModel):
    """A person credited in external info, identified by the source's ID rather than by name.

    Subclasses add a nullable unique ID field and name it in `external_id_field`. People stored before IDs were
    tracked have no ID; they get one when a credit adopts them (see PersonManager.from_credit).
    """

    class Meta:
        abstract = True
        ordering = ('name',)

    external_id_field = None

    name = models.CharField(max_length=255)

    objects = PersonManager()

    def __str__(self):
        return str(self.name)


class MediaItem(TimestampedModel):
    class Meta:
        abstract = True
        ordering = ('title',)

    category = None
    source_class = None
    # Name of the foreign key to the item's external info (see external_info)
    external_info_field = None

    title = models.CharField(max_length=255)
    alternate_title = models.CharField(blank=True, max_length=255)
    interest = models.IntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

    @property
    def external_info(self):
        raise NotImplementedError

    @property
    def interest_color(self):
        return ColorPicker().color_for(self.interest)

    @property
    def get_category(self):
        if not type(self).category:
            return f"Undefined category for model {type(self)}"
        return type(self).category

    def swap_titles(self):
        self.title, self.alternate_title = self.alternate_title, self.title
        self.save()


class MediaSource(NamedModel, TimestampedModel):
    class Meta:
        abstract = True

    icon = models.ImageField(upload_to="source_icons/", blank=True, null=True)
