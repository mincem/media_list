from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

APP = "media_list"
BEFORE = [(APP, "0011_alter_mangaurl_options_alter_movieurl_options_and_more")]
AFTER = [(APP, "0012_unify_baka_id")]


class UnifyBakaIdMigrationTests(TransactionTestCase):
    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def tearDown(self):
        self.migrate(executor_leaf_nodes())

    def test_forward_and_backward(self):
        old_apps = self.migrate(BEFORE)
        old_manga = old_apps.get_model(APP, "MangaSeries")
        old_baka = old_apps.get_model(APP, "BakaSeries")
        old_manga.objects.create(title="numeric", interest=50, baka_id=12345)
        old_manga.objects.create(title="code", interest=50, baka_code="a1b2c3d4")
        old_manga.objects.create(title="none", interest=50)
        old_baka.objects.create(title="numeric", baka_id=12345)
        old_baka.objects.create(title="code", baka_code="a1b2c3d4")
        old_baka.objects.create(title="both", baka_id=777, baka_code="zz99")

        new_apps = self.migrate(AFTER)
        new_manga = new_apps.get_model(APP, "MangaSeries")
        new_baka = new_apps.get_model(APP, "BakaSeries")
        self.assertEqual(
            {"numeric": "12345", "code": "a1b2c3d4", "none": None},
            dict(new_manga.objects.values_list("title", "baka_id")),
        )
        self.assertEqual(
            {"numeric": "12345", "code": "a1b2c3d4", "both": "zz99"},
            dict(new_baka.objects.values_list("title", "baka_id")),
        )

        reverted_apps = self.migrate(BEFORE)
        reverted_manga = reverted_apps.get_model(APP, "MangaSeries")
        self.assertEqual(
            {"numeric": (12345, None), "code": (None, "a1b2c3d4"), "none": (None, None)},
            {title: (baka_id, code) for title, baka_id, code
             in reverted_manga.objects.values_list("title", "baka_id", "baka_code")},
        )


def executor_leaf_nodes():
    return MigrationExecutor(connection).loader.graph.leaf_nodes()
