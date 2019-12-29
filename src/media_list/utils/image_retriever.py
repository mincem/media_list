import os

import requests
from django.core.files.base import ContentFile


class ImageRetriever:
    def __init__(self, image_url):
        self.image_url = image_url

    def fetch(self):
        response = requests.get(self.image_url)
        response.raise_for_status()
        return {
            "name": os.path.basename(self.image_url),
            "content": ContentFile(response.content),
        }
