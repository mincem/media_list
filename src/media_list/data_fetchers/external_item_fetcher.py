from ..utils import ImageRetriever


class ExternalItemFetcher:
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

    def fetch(self):
        raise NotImplementedError
