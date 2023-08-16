import sys
import os
import requests
from tqdm import tqdm

import utils.HdRezka as HdRezka
from helper.hd_rezka_api import HdRezkaApi

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/103.0.0.0 Safari/537.36 "
}

MIRROR_URL = "https://hdrezka.ag"


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
    def __init__(self):
        search_title = input("Введите название: ")

        search_request = HdRezka.search(MIRROR_URL, search_title, 1)

        for i in range(len(search_request)):
            print(
                f"{i} - {search_request[i]['title']} ({search_request[i]['year']}) ({search_request[i]['mirrorLessUrl']})"
            )

        series_id = int(input("Введите номер: "))

        self.url = search_request[series_id]["mirrorLessUrl"]
        self.title = search_request[series_id]["title"]

        detail_info_request = HdRezka.details(MIRROR_URL, self.url, None)

        if detail_info_request["translations_id"] != []:
            for i in range(len(detail_info_request["translations_id"])):
                print(f"{i} - {detail_info_request['translations_id'][i]['name']}")
            translation_id = int(input("Введите номер: "))
            translation_id = detail_info_request["translations_id"][translation_id]["id"]
        else:
            translation_id = None

        print("1: Скачать сезон")
        print("2: Скачать серию")
        print("3: Скачать фильм")
        var_download = input("Выберите действие: ")
        if var_download == "1":
            season_id = input("Введите номер сезона: ")
            self.Download_Season(season_id, translation_id)
        elif var_download == "2":
            season_id = input("Введите номер сезона: ")
            episode_id = input("Введите номер серии: ")
            self.Download_Episode(season_id, episode_id, translation_id)

    def Download_Season(self, season_id, translation_id):
        # get series list
        if (translation_id is None):
            series_list = HdRezkaApi(self.url, MIRROR_URL).getSeasons()
            series_list = series_list[list(series_list.keys())[0]]
        else:
            series_list = HdRezkaApi(self.url, MIRROR_URL).getSeasons(translator_id=translation_id)

        for i in range(1, len(series_list["episodes"][str(season_id)]) + 1):
            episode_source = HdRezkaApi(self.url, MIRROR_URL).getStream(translation=translation_id, season=season_id, episode=i).videos

            file_name = f"{self.title} - {season_id}s{i}e.mp4"

            # remove symbols from file_name
            sym_arr = ["!", " /", "?"]
            for sym in sym_arr:
                file_name = file_name.replace(sym, "")
                self.title = self.title.replace(sym, "")

            # remove spaces first and last
            file_name = file_name.strip()

            download_data = {
                "stream_url": episode_source["360p"],
                "file_name": file_name.strip(),
                "title": self.title,
            }

            self.__download(download_data)

    def Download_Episode(self, season_id, episode_id, translation_id):
        episode_source = HdRezkaApi(self.url, MIRROR_URL).getStream(translation=translation_id, season=season_id, episode=episode_id).videos

        file_name = f"{self.title} - {season_id}s{episode_id}e.mp4"

        # remove symbols from file_name
        sym_arr = ["!", " /", "?"]
        for sym in sym_arr:
            file_name = file_name.replace(sym, "")
            self.title = self.title.replace(sym, "")

        # remove spaces first and last
        file_name = file_name.strip()

        download_data = {
            "stream_url": episode_source["360p"],
            "file_name": file_name.strip(),
            "title": self.title,
        }

        self.__download(download_data)

    @staticmethod
    def __download(download_data):
        if not download_data["stream_url"]:
            return
        fullpath = os.path.join(
            os.path.curdir, "temp", download_data["title"], download_data["file_name"]
        )
        # remove symbols from fullpath
        fullpath = fullpath.replace(":", "")

        if not os.path.exists(os.path.dirname(fullpath)):
            os.makedirs(os.path.dirname(fullpath))

        # check if file exists
        if (os.path.exists(fullpath)):
            print(f"File {download_data['file_name']} downloaded")
            return

        with requests.get(
            url=download_data["stream_url"], stream=True, headers=HEADERS
        ) as r, open(fullpath, "wb") as f, tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(r.headers.get("content-length", 0)),
            file=sys.stdout,
            desc=download_data["file_name"],
        ) as progress:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    datasize = f.write(chunk)
                    progress.update(datasize)


if __name__ == "__main__":
    Download()
