# pylint: disable=wildcard-import

import os

from .base import *
from .base import BASE_DIR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db/db.sqlite3'),
    }
}
