from . import base_models


class VideoSource(base_models.MediaSource):
    pass


class VideoGenre(base_models.NamedModel):
    pass


class VideoKeyword(base_models.NamedModel):
    pass


class VideoPerson(base_models.NamedModel, base_models.TimestampedModel):
    pass


class VideoCountry(base_models.NamedModel):
    pass
