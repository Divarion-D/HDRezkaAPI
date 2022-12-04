from bs4 import BeautifulSoup


class Translations:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.translations = self.soup.select('ul#translators-list > li')

    def get(self):
        if len(self.translations):
            data = []
            for i in self.translations:
                data.append({'name': i.text,
                             'id': i.get('data-translator_id')})
            return data
        else:
            return None
