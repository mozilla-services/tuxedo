from django import test

from .product_details import LocaleDetails


class LanguageTestCase(test.TestCase):
    """Make sure our language list does what it should."""

    def test_ja_jp_mac(self):
        """ja-JP-mac is not a default language, but we need it."""
        ld = LocaleDetails()
        assert 'ja-JP-mac' in ld.get_locale_codes()
