import argparse
import enum
import json
import os
from typing import Union

import uvicorn
from fastapi import FastAPI, Request

from utils.HdRezka import search_hd, details_hd, translations_hd, HdRezkaApi, HdRezkaParser

# Create the FastAPI app
app = FastAPI(title="api")


def home_page(request: Request):
    # get ip
    url = str(request.url)
    return {
        "info": "This is HDRezkaApi",
        "api": url + "api",
        "api_docs": url + "api/docs",
        "api_redoc": url + "api/redoc",
    }


# show home page in open /
app.add_api_route("/", home_page)
# mount the api
app.mount("/api", app)


# Create a custom openapi function
def custom_openapi():
    with open("openapi.json", "r") as openapi:
        return json.load(openapi)


# Create a Settings class to store and manage settings
class Settings:
    def __init__(self):
        # Set default values for ip, port and mirror
        self.ip: str = "0.0.0.0"
        self.port: int = 8000
        self.mirror: str = "https://hdrezka.ag"
        # Create settings file if it does not exist
        if not os.path.exists("settings.json"):
            with open("settings.json", "w") as settings_file:
                json.dump(
                    {"ip": self.ip, "port": self.port, "mirror": self.mirror},
                    settings_file,
                )

    # Set the settings for the object
    def set_settings(self, ip: str, port: int, mirror: str):
        self.ip = ip
        self.port = port
        self.mirror = mirror
        # Write the settings to a JSON file
        with open("settings.json", "w") as settings_file:
            json.dump(
                {"ip": self.ip, "port": self.port, "mirror": self.mirror}, settings_file
            )

    # Retrieve settings from settings.json file
    def get_settings(self, name: str = None):
        with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)
        if name == "ip":
            return settings["ip"]
        elif name == "port":
            return settings["port"]
        elif name == "mirror":
            return settings["mirror"]
        else:
            return settings


# Set the custom openapi function
app.openapi = custom_openapi
# Create an instance of the Settings class
settings = Settings()


# # Create the root route
# @app.get("/")
# async def root():
#     return {"message": "no requests here"}


# Create the search route
@app.get("/search")
async def search(query: str, page: int = 1):
    return search_hd(settings.get_settings("mirror"), query, page)


# Create the details route
@app.get("/details")
async def get_concrete(url: Union[str, None] = None, id: Union[int, None] = None):
    return details_hd(settings.get_settings("mirror"), url, id)


# Create the translations route
@app.get("/translations")
async def get_content_translations(
    url: Union[str, None] = None, id: Union[int, None] = None
):
    return translations_hd(settings.get_settings("mirror"), url, id)


@app.get("/movie/videos")
async def get_movie_videos(
    url: Union[str, None] = None,
    id: Union[int, None] = None,
    translation_id: str = None,
):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, settings.get_settings("mirror"))
    elif url is None:
        url = HdRezkaParser.get_url_by_id(settings.get_settings("mirror"), id)
        if url == "error":
            return {"error": "film id not found"}
        api: HdRezkaApi = HdRezkaApi(url, settings.get_settings("mirror"))
    else:
        return {"error": "url and id cannot be used together"}

    stream = api.getStream(translation=translation_id)

    if type(stream) == dict and stream.get("error"):
        return stream

    return stream.videos


@app.get("/tv_series/seasons")
async def get_tv_series_seasons(
    url: Union[str, None] = None,
    id: Union[int, None] = None,
    translation_id: str = None,
):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, settings.get_settings("mirror"))
    elif url is None:
        url = HdRezkaParser.get_url_by_id(settings.get_settings("mirror"), id)
        query = url.split("/", 3)[3]
        url = f"{settings.get_settings('mirror')}\{query}"

        if url == "error":
            return {"error": "film id not found"}
        api: HdRezkaApi = HdRezkaApi(url, settings.get_settings("mirror"))
    else:
        return {"error": "url and id cannot be used together"}

    return api.getSeasons(translator_id=translation_id)


@app.get("/tv_series/videos")
async def get_tv_series_videos(
    season_id: str,
    episode_id: str,
    url: Union[str, None] = None,
    id: Union[int, None] = None,
    translation_id: str = None,
):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, settings.get_settings("mirror"))
    elif url is None:
        url = HdRezkaParser.get_url_by_id(settings.get_settings("mirror"), id)
        query = url.split("/", 3)[3]
        url = f"{settings.get_settings('mirror')}{query}"

        if url == "error":
            return {"error": "film id not found"}
        api: HdRezkaApi = HdRezkaApi(url, settings.get_settings("mirror"))
    else:
        return {"error": "url and id cannot be used together"}
    stream = api.getStream(
        translation=translation_id, season=season_id, episode=episode_id
    )

    if type(stream) == dict and stream.get("error"):
        return stream

    return stream.videos


@app.get("/page/{page}")
async def get_content(page: int, filter: str = "last", type: str = "all"):
    url: str = create_url(page, filter, type, settings.get_settings("mirror"))
    parser: HdRezkaParser = HdRezkaParser(settings.get_settings("mirror"), url)
    return parser.get_content_list()


@app.get("/genres")
async def get_genres(type: str = "films"):
    parser: HdRezkaParser = HdRezkaParser(settings.get_settings("mirror"), "")
    return parser.get_genres(type)


@app.get("/category/page/{page}")
async def get_content_by_categories(
    page: int = 1, type: str = "films", genre: str = "any", year: int = None
):
    url = create_categories_url(
        page, type, genre, year, settings.get_settings("mirror")
    )
    parser: HdRezkaParser = HdRezkaParser(settings.get_settings("mirror"), url)
    return parser.get_content_list()


def create_url(page: int, filter: str, type: str, mirror: str):
    genre_index: int = ContentType[f"{type}"].value
    url = mirror
    if page != 1:
        url += f"/page/{page}/"
    url += f"?filter={filter}"
    if genre_index != 0:
        url = f"{url}&genre={genre_index}"
    return url


def create_categories_url(page: int, type: str, genre: str, year: int, mirror: str):
    url = f"{mirror}{type}/best/"
    if genre != "any":
        url += f"{genre}/"
    if year is not None:
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
    parser.add_argument("-mirrorUrl", help="url of the mirror hdrezka site")

    args = parser.parse_args()

    if args.ip:
        os.environ["IP"] = args.ip
    if args.port:
        os.environ["PORT"] = args.port
    if args.mirrorUrl:
        os.environ["MIRROR_URL"] = args.mirrorUrl

    ip = os.environ.get("IP", "0.0.0.0")
    port = os.environ.get("PORT", "8000")
    mirror = os.environ.get("MIRROR_URL", "https://hdrezka.ag")

    settings.set_settings(ip, port, mirror)

    uvicorn.run(
        "api:app",
        host=ip,
        port=int(port),
        debug=True,
        reload=True,
    )
