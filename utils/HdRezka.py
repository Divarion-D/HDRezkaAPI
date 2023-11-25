from typing import Union
from helper.hd_rezka_api import HdRezkaApi
from helper.hd_rezka_parser import HdRezkaParser


def search_hd(mirror: str, query: str, page: int = 1) -> list:
    search_url = f"{mirror}/search/?do=search&subaction=search&q={query}&page={page}"
    parser = HdRezkaParser(mirror, search_url)
    return parser.get_content_list()


def details_hd(
    mirror: str, url: Union[str, None] = None, film_id: Union[int, None] = None
) -> Union[dict, str]:
    if url and film_id:
        return {"error": "url and id cannot be used together"}
    elif url or film_id:
        api_url = url or HdRezkaParser.get_url_by_id(mirror, film_id)
        if api_url == "error":
            return {"error": "film id not found"}
        return HdRezkaParser.get_concrete_content_info(api_url)
    else:
        return {"error": "url or id is required"}


def translations_hd(
    mirror: str, url: str = None, film_id: int = None
) -> Union[str, dict]:
    if url and film_id:
        return {"error": "url and id cannot be used together"}
    elif url or film_id:
        api_url = url or HdRezkaParser.get_url_by_id(mirror, film_id)
        if api_url == "error":
            return {"error": "film id not found"}
        api = HdRezkaApi(api_url, mirror)
        return api.getTranslations()
    else:
        return {"error": "url or id is required"}
