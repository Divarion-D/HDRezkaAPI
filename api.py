import argparse
import enum
import json
from typing import Union

import uvicorn
from fastapi import FastAPI, Header

from hd_rezka_api import HdRezkaApi
from hd_rezka_parser import HdRezkaParser

app = FastAPI()

HDREZKA_URL = "http://rd8j1em1zxge.org/"


def custom_openapi():
    with open("openapi.json", "r") as openapi:
        return json.load(openapi)


app.openapi = custom_openapi

@app.get("/")
async def root():
    return {"message": "no requests here"}

@app.get("/search")
async def search(query: str, page: int = 1):
    search_url: str = f"{HDREZKA_URL}search/?do=search&subaction=search&q={query}&page={page}"
    parser: HdRezkaParser = HdRezkaParser(search_url)
    return parser.get_content_list()


@app.get("/details")
async def get_concrete(url: Union[str, None] = None, id: Union[int, None] = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        return HdRezkaParser.get_concrete_content_info(url)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        return HdRezkaParser.get_concrete_content_info(url)
    else:
        return {"error": "url and id cannot be used together"}


@app.get("/translations")
async def get_content_translations(url: Union[str, None] = None, id: Union[int, None] = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    else:
        return {"error": "url and id cannot be used together"}

    return api.getTranslations()


@app.get("/movie/videos")
async def get_movie_videos(url: Union[str, None] = None, id: Union[int, None] = None, translation_id: str = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    else:
        return {"error": "url and id cannot be used together"}

    stream = api.getStream(translation=translation_id)
    return stream.videos


@app.get("/tv_series/seasons")
async def get_tv_series_seasons(url: Union[str, None] = None, id: Union[int, None] = None, translation_id: str = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    else:
        return {"error": "url and id cannot be used together"}

    return api.getSeasons(translator_id=translation_id)


@app.get("/tv_series/videos")
async def get_tv_series_videos(season_id: str, episode_id: str, url: Union[str, None] = None, id: Union[int, None] = None, translation_id: str = None):
    api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    stream = api.getStream(translation=translation_id,
                           season=season_id, episode=episode_id)
    return stream.videos


@app.get("/page/{page}")
async def get_content(page: int, filter: str = "last", type: str = "all"):
    url: str = create_url(page, filter, type, HDREZKA_URL)
    parser: HdRezkaParser = HdRezkaParser(url)
    return parser.get_content_list()


@app.get("/genres")
async def get_genres(type: str = "films"):
    parser: HdRezkaParser = HdRezkaParser(HDREZKA_URL)
    return parser.get_genres(type)


@app.get("/category/page/{page}")
async def get_content_by_categories(page: int = 1, type: str = "films", genre: str = "any", year: int = None):
    url = create_categories_url(page, type, genre, year, HDREZKA_URL)
    parser: HdRezkaParser = HdRezkaParser(url)
    return parser.get_content_list()


def create_url(page: int, filter: str, type: str, mirror: str):
    genre_index: int = ContentType[f"{type}"].value
    url = mirror
    if (page != 1):
        url += f"/page/{page}/"
    url += f"?filter={filter}"
    if genre_index != 0:
        url = f"{url}&genre={genre_index}"
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="ip address of the server")
    parser.add_argument("-port", help="port of the server")
    args = parser.parse_args()
    ip = args.ip
    port = args.port

    if ip is None:
        ip = "127.0.1.1"
    if port is None:
        port = "8000"
    uvicorn.run("api:app", host=ip, port=int(port), debug=True, reload=True)
