import sys
from os import path
from bs4 import BeautifulSoup
from .request import Request
from .get_stream import GetStream
from tqdm import tqdm


class Error(Exception):
    """Base class for other exceptions"""
    pass


class IncorrectEpisodeNumberException(Error):
    """Raised when incorrect episode number was in input"""
    pass


class EpisodeNumberIsOutOfRange(Error):
    """Raised when episode number is out of range of available episodes"""
    pass


class Download:
    def __init__(self, download_data):
        self.data = download_data
        self.url = download_data['url']
        response = Request().get(self.url)
        self.soup = BeautifulSoup(response.content, 'html.parser')
        self.favs = self.soup.find('input', id='ctrl_favs').get('value')

    def download_season(self, season):
        if season < 1 or season > self.data['seasons_count']:
            # TODO Make new custom exception for incorrect season number and realize it
            return

        episodes_list = self.soup.find(
            'ul', id=f'simple-episodes-list-{season}')
        episodes_count = len(episodes_list.findAll('li'))

        if self.data['translations_list']:
            translator_id = self.__get_translation()
        else:
            translator_id = self.__detect_translation()

        for i in range(1, episodes_count + 1):
            self.download_episode(season, i, translator_id, True)

    def download_episodes(self, season, start, end):
        if season < 1 or season > self.data['seasons_count']:
            # TODO Make new custom exception for incorrect season number and realize it
            return

        episodes_list = self.soup.find(
            'ul', id=f'simple-episodes-list-{season}')
        episodes_count = len(episodes_list.findAll('li'))

        if end > episodes_count or start < 0:
            raise EpisodeNumberIsOutOfRange

        if self.data['translations_list']:
            translator_id = self.__get_translation()
        else:
            translator_id = self.__detect_translation()

        for i in range(start, end + 1):
            self.download_episode(season, i, translator_id, True)

    def download_episode(self, season, episode, translator_id=None, multi_download=False):
        if self.data['type'] == 'movie':
            return
        if season > self.data['seasons_count']:
            return

        if not multi_download:
            if self.data['translations_list']:
                translator_id = self.__get_translation()
            else:
                translator_id = self.__detect_translation()

        if episode < 1 or episode > self.data['seasons_episodes_count'][season]:
            raise IncorrectEpisodeNumberException

        data = {
            'id': self.data['data-id'],
            'translator_id': translator_id,
            'favs': self.favs,
            'season': season,
            'episode': episode,
            'action': 'get_stream'
        }

        stream_url = GetStream().get_series_stream(data)
        file_name = f"{self.data['name']} {season}s{episode}e.mp4"

        download_data = {
            'stream_url': stream_url,
            'file_name': file_name,
        }

        self.__download(download_data)

    def download_movie(self):
        if self.data['type'] == 'series':
            return

        if self.data['translations_list']:
            translator_id = self.__get_translation()
        else:
            translator_id = self.__detect_translation()
        
        data = {
            'id': self.data['data-id'],
            'translator_id': translator_id,
            'favs': self.favs,
            'action': 'get_movie'
        }

        stream_url = GetStream().get_movie_stream(data)
        # file_name = f"{self.data['name']}.mp4"
        # TODO Fix file name bug
        file_name = f"test.mp4"

        download_data = {
            'stream_url': stream_url,
            'file_name': file_name,
        }

        self.__download(download_data)

    @staticmethod
    def __download(download_data):
        if download_data['stream_url']:

            fullpath = path.join(path.curdir, download_data['file_name'])

            with Request().get(download_data['stream_url'], stream=True) as r, open(fullpath, "wb") as f, tqdm(
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    total=int(r.headers.get('content-length', 0)),
                    file=sys.stdout,
                    desc=download_data['file_name']
            ) as progress:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        datasize = f.write(chunk)
                        progress.update(datasize)

    def __get_translation(self) -> int:
        for i, translation in zip(range(1, len(self.data['translations_list'])), self.data['translations_list']):
            print(f'{i} - {translation["name"]}')
        translation_id = self.data['translations_list'][int(
            input("Введите номер озвучки: ")) - 1]['id']
        return translation_id

    def __detect_translation(self):
        if self.data['type'] == 'movie':
            event_type = 'initCDNMoviesEvents'
        else:
            event_type = 'initCDNSeriesEvents'

        tmp = str(self.soup).split(f"sof.tv.{event_type}")[-1].split("{")[0]
        translator_id = tmp.split(",")[1].strip()

        return translator_id
