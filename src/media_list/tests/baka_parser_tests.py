from django.test import TestCase

from ..utils import BakaParser, MockBakaRetriever


class BakaParserTests(TestCase):
    def test_pending(self):
        parser = BakaParser(MockBakaRetriever())
        print(parser.display_parsed_data(913))  # Full Metal Panic Sigma (check sigma char)
        self.assertTrue(False)
