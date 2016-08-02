import basetest
import settings


class SettingsTest(basetest.BaseTest):
    def setUp(self):
        super().setUp()
        settings.synced.AUTH_SDE_TOKEN = ""
        settings.synced.ALCOHOL_MAJORATION = 0
        settings.synced.refresh_cache()

    def tearDown(self):
        self.setUp()

    def test_synced_settings(self):
        """ Testing synced settings
        """
        settings.synced.AUTH_SDE_TOKEN = "test1"
        self.assertEqual(settings.synced.AUTH_SDE_TOKEN, "test1")
        settings.synced.AUTH_SDE_TOKEN = "test2"
        self.assertEqual(settings.synced.AUTH_SDE_TOKEN, "test1")
        settings.CACHED_SETTINGS = {}
        self.assertEqual(settings.synced.AUTH_SDE_TOKEN, "test2")
