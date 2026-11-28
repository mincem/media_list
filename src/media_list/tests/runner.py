import shutil
import tempfile

from django.test.runner import DiscoverRunner
from django.test.utils import override_settings


class TempMediaTestRunner(DiscoverRunner):
    """Runs the tests with MEDIA_ROOT in a temporary folder, deleted afterwards, so they never write to the real one."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_root = None
        self.media_override = None

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self.media_root = tempfile.mkdtemp(prefix="media_list_test_media_")
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()

    def teardown_test_environment(self, **kwargs):
        self.media_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)
        super().teardown_test_environment(**kwargs)
