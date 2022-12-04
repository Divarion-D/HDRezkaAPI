from bs4 import BeautifulSoup


class Translations:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.translations = self.soup.select('ul#translators-list > li')

    def get(self):
        if len(self.translations):
            return [
                {'name': i.text, 'id': i.get('data-translator_id')}
                for i in self.translations
            ]

        else:
            return None
