from fastapi import FastAPI, Header
import uvicorn
from typing import Union
from hd_rezka_parser import HdRezkaParser
from hd_rezka_api import HdRezkaApi
import enum
import socket

app = FastAPI()
HDREZKA_URL = "http://rd8j1em1zxge.org/"


@app.get("/content/page/{page}")
async def get_content(page: int, filter: str = "last", type: str = "all"):
    mirror = HDREZKA_URL
    url: str = create_url(page, filter, type, mirror)
    print(url)
    parser: HdRezkaParser = HdRezkaParser(url)
    content_list = parser.get_content_list(mirror)
    return content_list


@app.get("/content/details/")
async def get_concrete(mirror_less_url: str):
    url = HDREZKA_URL + mirror_less_url
    content = HdRezkaParser.get_concrete_content_info(url)
    return content


@app.get("/content/translations/")
async def get_content_translations(url: str = None):
    api: HdRezkaApi = HdRezkaApi(url)
    translations = api.getTranslations()
    return translations


@app.get("/content/movie/videos/")
async def get_movie_videos(url: str = None, translation_id: str = None):
    api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    stream = api.getStream(translation=translation_id)
    return stream.videos


@app.get("/content/tv_series/seasons/")
async def get_tv_series_seasons(url: str, translation_id: str = None):
    api: HdRezkaApi = HdRezkaApi(url)
    seasons = api.getSeasons(translator_id=translation_id)
    return seasons


@app.get("/content/tv_series/videos/")
async def get_tv_series_videos(url: str, translation_id: str, season_id: str, series_id: str):
    api: HdRezkaApi = HdRezkaApi(url)
    stream = api.getStream(translation=translation_id,
                           season=season_id, episode=series_id)
    return stream.videos


@app.get("/content/search/")
async def search(query: str, page: int):
    mirror = HDREZKA_URL
    search_url: str = f"{mirror}search/?do=search&subaction=search&q={query}&page={page}"
    parser: HdRezkaParser = HdRezkaParser(search_url)
    content = parser.get_content_list(mirror)
    return content


@app.get("/content/category/page/{page}")
async def get_content_by_categories(page: int = 1, type: str = "films", genre: str = "any", year: int = None):
    mirror = HDREZKA_URL
    url = create_categories_url(page, type, genre, year, mirror)
    parser: HdRezkaParser = HdRezkaParser(url)
    content = parser.get_content_list(mirror)
    return content


def create_url(page: int, filter: str, type: str, mirror: str):
    genre_index: int = ContentType[f"{type}"].value
    url = mirror
    if(page != 1):
        url += f"/page/{page}/"
    url += f"?filter={filter}"
    if genre_index != 0:
        url = url + f"&genre={genre_index}"
    return url


def create_categories_url(page: int, type: str, genre: str, year: int, mirror: str):
    url = f"{mirror}{type}/best/"
    if genre != "any":
        url += f"{genre}/"
    if year != None:
        url += f"{year}/"
    if page != 1:
        url += f"page/{page}/"
    return url


class ContentType(enum.Enum):
    all = 0
    film = 1
    series = 2
    cartoon = 3
    anime = 82


class ContentGenre(enum.Enum):
    any = 1
    drama = 2
    comedy = 3
    crime = 4
    detective = 5
    action = 6
    adventures = 7
    fantasy = 8
    melodrama = 9
    western = 10
    fiction = 11
    horror = 12
    musical = 13
    military = 14
    documentary = 15
    erotic = 16
    cognitive = 17
    arthouse = 18


if __name__ == "__main__":
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    uvicorn.run(app, host=ip, port=8888)
