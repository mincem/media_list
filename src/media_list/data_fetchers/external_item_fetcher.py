from ..utils import ImageRetriever


class ExternalItemFetcher:
    def __init__(self, item, image_retriever_class=None):
        if not item.external_id:
            raise Exception("Missing external item ID")
        self.item = item
        self.image_retriever_class = image_retriever_class or ImageRetriever

    def fetch(self):
        raise NotImplementedError
