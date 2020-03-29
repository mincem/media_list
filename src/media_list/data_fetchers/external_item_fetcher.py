class ExternalItemFetcher:
    def __init__(self, item):
        self.item = item

    def fetch(self):
        raise NotImplementedError
