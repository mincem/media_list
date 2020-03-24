class ExternalIDFinder:
    def __init__(self, title):
        self.title = title

    def get_id(self):
        raise NotImplementedError
