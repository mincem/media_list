class ExternalIDFinder:
    def __init__(self, title):
        self.title = title

    @classmethod
    def for_item(cls, item):
        subclass_for_item = next(iter([subclass for subclass in cls.__subclasses__() if subclass.accepts(item)]))
        return subclass_for_item(item.title)

    @classmethod
    def accepts(cls, item):
        raise NotImplementedError

    def get_id(self):
        raise NotImplementedError
