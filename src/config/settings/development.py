# pylint: disable=wildcard-import
# pylint: disable=undefined-variable

from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db/db_test.sqlite3'),
    }
}
