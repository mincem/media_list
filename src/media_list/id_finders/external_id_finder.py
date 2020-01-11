class ExternalIDFinder:
    def __init__(self, series_title):
        self.series_title = series_title

    def get_id(self):
        raise NotImplementedError
