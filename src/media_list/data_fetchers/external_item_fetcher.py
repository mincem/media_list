from django.db import transaction

from ..utils import ImageRetriever


class ExternalItemFetcher:
    """Fetches an item's info from an external source and stores it on the item.

    Subclasses set `repository_class` (an ExternalItemRepository) and implement `fetch_data`.
    """
    repository_class = None

    def __init__(self, item, image_retriever_class=None):
        if not item.external_id:
            raise Exception("Missing external item ID")
        self.item = item
        self.image_retriever_class = image_retriever_class or ImageRetriever

    @classmethod
    def for_item(cls, item):
        subclass_for_item = next(iter([subclass for subclass in cls.__subclasses__() if subclass.accepts(item)]))
        return subclass_for_item(item)

    @classmethod
    def accepts(cls, item):
        raise NotImplementedError

    def fetch_data(self):
        """Makes every request to the source (data and cover) and returns the data to store.

        May update the item's external ID (but not save it), e.g. when the source upgraded an old ID.
        """
        raise NotImplementedError

    def fetch(self):
        """Fetches the item's info, stores it, points the item at it and saves the item.

        If the item's info is for the item's current external ID, it's updated in place. Otherwise (the ID was changed),
        new info is created and the old info is deleted, unless another item uses it.
        Everything is fetched before anything is written, and the writes are made in one transaction.
        """
        current_info = self.item.external_info
        is_refresh = current_info is not None and str(current_info.external_id) == str(self.item.external_id)
        data = self.fetch_data()
        repository = self.repository_class()  # pylint: disable=not-callable  # Set by subclasses
        with transaction.atomic():
            if is_refresh:
                info = repository.update(current_info, **data)
            else:
                info = repository.create(**data)
            self.item.external_info = info
            self.item.save()
            if current_info is not None and not is_refresh and not self.is_info_used(current_info):
                repository.delete(current_info)
        return info

    def is_info_used(self, info):
        return type(self.item).objects.filter(**{type(self.item).external_info_field: info}).exists()
