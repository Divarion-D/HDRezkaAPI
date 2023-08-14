import base64
from itertools import product

import requests
from bs4 import BeautifulSoup


class HdRezkaStreamSubtitles:
    def __init__(self, data, codes):
        self.subtitles = {}
        self.keys = []
        if data:
            arr = data.split(",")
            for i in arr:
                temp = i.split("[")[1].split("]")
                lang = temp[0]
                link = temp[1]
                code = codes[lang]
                self.subtitles[code] = {"title": lang, "link": link}
            self.keys = list(self.subtitles.keys())

    def __str__(self):
        return str(self.keys)

    def __call__(self, id=None):
        if not self.subtitles:
            return
        if not id:
            return None
        if id in self.subtitles.keys():
            return self.subtitles[id]["link"]
        for key, value in self.subtitles.items():
            if value["title"] == id:
                return self.subtitles[key]["link"]
        if str(id).isnumeric:
            code = list(self.subtitles.keys())[id]
            return self.subtitles[code]["link"]
        raise ValueError(f'Subtitles "{id}" is not defined')


class HdRezkaStream:
    def __init__(self, season, episode, subtitles={}):
        """Initialize HdRezkaStream object
        Arguments:
        season {int} -- Season number
        episode {int} -- Episode number
        subtitles {dict} -- Subtitles (default: {None})
        """
        self.videos = {}
        self.season = season
        self.episode = episode
        self.subtitles = HdRezkaStreamSubtitles(**subtitles)

    def append(self, resolution, link):
        """Append video to the list of videos
        Arguments:
        resolution {str} -- Resolution of the video
        link {str} -- Link to the video
        """
        self.videos[resolution] = link

    def __str__(self):
        resolutions = iter(self.videos.keys())
        if self.subtitles.subtitles:
            return f"<HdRezkaStream> : {resolutions}, subtitles={self.subtitles}"
        return f"<HdRezkaStream> : {resolutions}"

    def __repr__(self):
        return f"<HdRezkaStream(season:{self.season}, episode:{self.episode})>"

    def __call__(self, resolution):
        """Get video link by resolution
        Arguments:
        resolution {str} -- Resolution of the video
        Raises:
        ValueError: If resolution is not defined
        Returns:
        str -- Link to the video
        """
        if coincidences := {res: link for res, link in self.videos.items() if str(resolution) in res}:
            return coincidences[list(coincidences.keys())[0]]
        raise ValueError(f'Resolution "{resolution}" is not defined')


class HdRezkaApi:
    __version__ = 4.0

    def __init__(self, url, mirror):
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        }
        self.url = url.split(".html")[0] + ".html"
        self.mirror = mirror
        self.page = self.getPage()
        self.soup = self.getSoup()
        self.id = self.extractId()
        self.name = self.getName()
        self.type = self.getType()

        # other
        self.translators = None
        self.seriesInfo = None

    def getPage(self):
        for _ in range(3):
            try:
                response = requests.get(self.url, headers=self.HEADERS)
                if response.status_code == 200:
                    return response
                else:
                    print("Error occurred while getting page: ", response.status_code)
            except Exception as e:
                print("Error occurred while getting page: ", e)
        return None

    def getSoup(self):
        return BeautifulSoup(self.page.content, "html.parser")

    def extractId(self):
        # return self.soup.find(id="post_id").attrs["value"]
        return self.soup.find(id="send-video-issue").attrs["data-id"]

    def getName(self):
        return self.soup.find(class_="b-post__title").get_text().strip()

    def getType(self):
        return self.soup.find("meta", property="og:type").attrs["content"]

    @staticmethod
    def clearTrash(data):
        # Create a list of characters to be removed from the data
        trashList = ["@", "#", "!", "^", "$"]
        # Create an empty list to store the generated codes
        trashCodesSet = []
        # Generate codes with 2 and 3 characters from the trashList
        for i in range(2, 4):
            startchar = ""
            for chars in product(trashList, repeat=i):
                data_bytes = startchar.join(chars).encode("utf-8")
                trashcombo = base64.b64encode(data_bytes)
                trashCodesSet.append(trashcombo)
        # Split the data into an array and join it back as a string
        arr = data.replace("#h", "").split("//_//")
        trashString = "".join(arr)
        # Replace the generated codes in the string with empty strings
        for i in trashCodesSet:
            temp = i.decode("utf-8")
            trashString = trashString.replace(temp, "")
        # Decode the string using base64
        finalString = base64.b64decode(f"{trashString}==")
        # Try to decode the string using utf-8, if it fails use cp1251
        try:
            return finalString.decode("utf-8")
        except UnicodeDecodeError:
            return finalString.decode("cp1251")

    def getTranslations(self):
        arr = {}
        translators = self.soup.find(id="translators-list")
        if translators:
            children = translators.findChildren(recursive=False)
            for child in children:
                if child.text:
                    arr[child.text] = child.attrs["data-translator_id"]
        else:
            # auto-detect
            def getTranslationName(s):
                table = s.find(class_="b-post__info")
                for i in table.findAll("tr"):
                    tmp = i.get_text()
                    if tmp.find("переводе") > 0:
                        return tmp.split("В переводе:")[-1].strip()

            def getTranslationID(s):
                initCDNEvents = {
                    "video.tv_series": "initCDNSeriesEvents",
                    "video.movie": "initCDNMoviesEvents",
                }
                tmp = s.text.split(f"sof.tv.{initCDNEvents[self.type]}")[-1].split("{")[0]
                return tmp.split(",")[1].strip()
            arr[getTranslationName(self.soup)] = getTranslationID(self.page)
        self.translators = arr
        return arr

    def getOtherParts(self):
        parts = self.soup.find(class_="b-post__partcontent")
        other = []
        if parts:
            for i in parts.findAll(class_="b-post__partcontent_item"):
                if "current" in i.attrs["class"]:
                    other.append({i.find(class_="title").text: self.url})
                else:
                    other.append({i.find(class_="title").text: i.attrs["data-url"]})
        return other

    @staticmethod
    def getEpisodes(s, e):
        seasons = BeautifulSoup(s, "html.parser")
        episodes = BeautifulSoup(e, "html.parser")

        seasons_ = {
            season.attrs["data-tab_id"]: season.text
            for season in seasons.findAll(class_="b-simple_season__item")
        }
        episods = {}
        for episode in episodes.findAll(class_="b-simple_episode__item"):
            if episode.attrs["data-season_id"] in episods:
                episods[episode.attrs["data-season_id"]][
                    episode.attrs["data-episode_id"]
                ] = episode.text
            else:
                episods[episode.attrs["data-season_id"]] = {
                    episode.attrs["data-episode_id"]: episode.text
                }

        return seasons_, episods

    def getSeasons(self, translator_id=None):
        if translator_id:
            js = {
                "id": self.id,
                "translator_id": translator_id,
                "action": "get_episodes",
            }
            r = requests.post(
                f"{self.mirror}/ajax/get_cdn_series/",
                data=js,
                headers=self.HEADERS,
            )
            response = r.json()
            seasons, episodes = self.getEpisodes(
                response["seasons"], response["episodes"]
            )
            return {
                "translator_id": translator_id,
                "seasons": seasons,
                "episodes": episodes,
            }

        if not self.translators:
            self.translators = self.getTranslations()

        arr = {}
        for i in self.translators:
            js = {
                "id": self.id,
                "translator_id": self.translators[i],
                "action": "get_episodes",
            }
            r = requests.post(
                f"{self.mirror}/ajax/get_cdn_series/",
                data=js,
                headers=self.HEADERS,
            )
            response = r.json()
            if response["success"]:
                seasons, episodes = self.getEpisodes(
                    response["seasons"], response["episodes"]
                )
                arr[i] = {
                    "translator_id": self.translators[i],
                    "seasons": seasons,
                    "episodes": episodes,
                }

        self.seriesInfo = arr
        return arr

    def getStream(self, season=None, episode=None, translation=None, index=0):
        def makeRequest(data):
            r = requests.post(
                f"{self.mirror}/ajax/get_cdn_series/",
                data=data,
                headers=self.HEADERS,
            )
            r = r.json()
            if r["success"]:
                if r["url"] is False:
                    return {
                        "error": "no_video",
                        "message": "Видео не найдено или заблокировано в вашем регионе",
                    }
                arr = self.clearTrash(r["url"]).split(",")
                stream = HdRezkaStream(
                    season,
                    episode,
                    subtitles={"data": r["subtitle"], "codes": r["subtitle_lns"]},
                )
                for i in arr:
                    res = i.split("[")[1].split("]")[0]
                    video = i.split("[")[1].split("]")[1].split(" or ")[1]
                    stream.append(res, video)
                return stream

        def getStreamSeries(self, season, episode, translation_id):
            if not season or not episode:
                raise TypeError(
                    "getStream() missing required arguments (season and episode)"
                )

            season = str(season)
            episode = str(episode)

            if not self.seriesInfo:
                self.getSeasons()
            seasons = self.seriesInfo

            tr_str = list(self.translators.keys())[
                list(self.translators.values()).index(translation_id)
            ]

            if season not in list(seasons[tr_str]["episodes"]):
                raise ValueError(f'Season "{season}" is not defined')

            if episode not in list(seasons[tr_str]["episodes"][season]):
                raise ValueError(f'Episode "{episode}" is not defined')

            return makeRequest(
                {
                    "id": self.id,
                    "translator_id": translation_id,
                    "season": season,
                    "episode": episode,
                    "action": "get_stream",
                }
            )

        def getStreamMovie(self, translation_id):
            return makeRequest(
                {"id": self.id, "translator_id": translation_id, "action": "get_movie"}
            )

        if not self.translators:
            self.translators = self.getTranslations()

        if translation:
            if translation.isnumeric():
                if translation in self.translators.values():
                    tr_id = translation
                else:
                    raise ValueError(
                        f'Translation with code "{translation}" is not defined'
                    )

            elif translation in self.translators:
                tr_id = self.translators[translation]
            else:
                raise ValueError(f'Translation "{translation}" is not defined')

        else:
            tr_id = list(self.translators.values())[index]

        if self.type == "video.tv_series":
            return getStreamSeries(self, season, episode, tr_id)
        elif self.type == "video.movie":
            return getStreamMovie(self, tr_id)
        else:
            raise TypeError("Undefined content type")

    def getSeasonStreams(
        self, season, translation=None, index=0, ignore=False, progress=None
    ):
        season = str(season)

        if not self.translators:
            self.translators = self.getTranslations()
        trs = self.translators

        if translation:
            if translation.isnumeric():
                if translation in trs.values():
                    tr_id = translation
                else:
                    raise ValueError(
                        f'Translation with code "{translation}" is not defined'
                    )

            elif translation in trs:
                tr_id = trs[translation]
            else:
                raise ValueError(f'Translation "{translation}" is not defined')

        else:
            tr_id = list(trs.values())[index]

        tr_str = list(trs.keys())[list(trs.values()).index(tr_id)]

        if not self.seriesInfo:
            self.getSeasons()
        seasons = self.seriesInfo

        if season not in list(seasons[tr_str]["episodes"]):
            raise ValueError(f'Season "{season}" is not defined')

        series = seasons[tr_str]["episodes"][season]
        streams = {}

        series_length = len(series)

        for episode_id in series:

            def make_call():
                stream = self.getStream(season, episode_id, tr_str)
                streams[episode_id] = stream
                if progress:
                    progress(episode_id, series_length)
                else:
                    print(f"> {episode_id}", end="\r")

            if ignore:
                try:
                    make_call()
                except Exception as e:
                    print(e)
            else:
                make_call()
        return streams
