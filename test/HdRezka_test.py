import unittest
from unittest.mock import patch
from typing import Union
import utils.HdRezka as HdRezka


class TestTranslations(unittest.TestCase):
    @patch('Helper.HdRezka.translations')
    def test_translations_with_url(self, mock_getTranslations):
        mock_getTranslations.return_value = {"English": "true"}
        url = "http://example.com"
        mirror = "http://example_mirror.com"
        self.assertEqual(HdRezka.translations(mirror, url), {"English": "true"})

    @patch('hd_rezka_parser.HdRezkaParser.get_url_by_id')
    @patch('Helper.HdRezka.translations')
    def test_translations_with_film_id(self, mock_getTranslations, mock_get_url_by_id):
        mock_get_url_by_id.return_value = "http://example.com"
        mock_getTranslations.return_value = {"Spanish": "true"}
        mirror = "http://example_mirror.com"
        film_id = 1234
        self.assertEqual(HdRezka.translations(mirror, film_id=film_id), {"Spanish": "true"})

    def test_translations_without_url_and_film_id(self):
        mirror = "http://example_mirror.com"
        self.assertEqual(HdRezka.translations(mirror), {"error": "url or id is required"})

    @patch('hd_rezka_parser.HdRezkaParser.get_url_by_id')
    def test_translations_with_invalid_film_id(self, mock_get_url_by_id):
        mock_get_url_by_id.return_value = "error"
        mirror = "http://example_mirror.com"
        film_id = 1234
        self.assertEqual(HdRezka.translations(mirror, film_id=film_id), {"error": "film id not found"})

    def test_translations_with_url_and_film_id(self):
        mirror = "http://example_mirror.com"
        url = "http://example.com"
        film_id = 1234
        self.assertEqual(HdRezka.translations(mirror, url, film_id), {"error": "url and id cannot be used together"})


if __name__ == '__main__':
    unittest.main()
