import requests


class Request:
    def __init__(self):
        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/103.0.0.0 Safari/537.36 '
        }

    def get(self, url, params=None, stream=False):
        return requests.get(url=url, params=params, stream=stream, headers=self.HEADERS)

    def post(self, url, data=None, params=None):
        return requests.post(url=url, data=data, params=params, headers=self.HEADERS)
