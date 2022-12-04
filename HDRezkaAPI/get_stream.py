import base64

from bs4 import BeautifulSoup
from itertools import product
from time import time
from .request import Request
from binascii import Error as BinasciiError


class GetStream:
    def get_series_stream(self, data):
        t = time() * 1000
        params = {
            't': str(t)
        }

        request_url = f'http://rd8j1em1zxge.org/ajax/get_cdn_series/?t={t}'

        stream_url = ''
        decoded = False
        while not decoded:
            try:
                response = Request().post(request_url, data=data, params=params)
                r = response.json()
                if r['success'] and not r['url']:
                    print('К сожалению, этот материал не доступен в вашем регионе! '
                          'Попробуйте скачать используя VPN!')
                    exit(0)
                arr = self.decode_url(r['url'], separator="//_//").split(",")
                # TODO Make quality select
                stream_url = arr[-1][arr[-1].find("or") + 3:]
                decoded = True
            except (UnicodeDecodeError, BinasciiError):
                print('Decoding error, trying again!')

        return stream_url

    def get_movie_stream(self, data):
        t = time() * 1000
        params = {
            't': str(t)
        }

        request_url = f'http://rd8j1em1zxge.org/ajax/get_cdn_series/?t={t}'

        stream_url = ''
        decoded = False
        while not decoded:
            try:
                response = Request().post(request_url, data=data, params=params)
                r = response.json()
                if r['success'] and not r['url']:
                    print('К сожалению, этот материал не доступен в вашем регионе! '
                          'Попробуйте скачать используя VPN!')
                    exit(0)
                arr = self.decode_url(r['url'], separator="//_//").split(",")
                # TODO Make quality select
                stream_url = arr[-1][arr[-1].find("or") + 3:]
                decoded = True
            except (UnicodeDecodeError, BinasciiError):
                print('Decoding error, trying again!')

        return stream_url

    @staticmethod
    def decode_url(data, separator):
        trash_list = ["@", "#", "!", "^", "$"]
        trash_codes_set = []
        for i in range(2, 4):
            startchar = ''
            for chars in product(trash_list, repeat=i):
                data_bytes = startchar.join(chars).encode("utf-8")
                trashcombo = base64.b64encode(data_bytes)
                trash_codes_set.append(trashcombo)

        arr = data.replace("#h", "").split(separator)
        trash_string = ''.join(arr)

        for i in trash_codes_set:
            temp = i.decode("utf-8")
            trash_string = trash_string.replace(temp, '')

        final_string = base64.b64decode(f"{trash_string}==")
        return final_string.decode("utf-8")
