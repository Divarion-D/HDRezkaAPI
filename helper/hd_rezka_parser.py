import requests
from bs4 import BeautifulSoup as BS
from requests_html import HTMLSession


class HdRezkaParser:
    """Class for parsing HDRezka content"""

    def __init__(self, mirror, url):
        """Initialize the class with the given parameters."""
        self.url = url
        self.mirror = mirror
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        }

    def get_content_list(self):
        """Get a list of content from the given URL"""
        session = HTMLSession()
        resp = session.get(self.url, headers=self.headers)
        html = BS(resp.html.html, "html.parser")
        content_list = html.find_all("div", class_="b-content__inline_item")
        content_list = list(
            map(lambda content: self.get_content_info(self, content), content_list)
        )
        session.close()
        return content_list

    def get_genres(self, types):
        """Get a list of genres from the given type"""
        session = HTMLSession()
        resp = session.get(self.mirror, headers=self.headers)
        html = BS(resp.html.html, "html.parser")
        session.close()
        genres = html.find_all("ul", class_="left")
        genres = list(map(lambda genre: genre.find_all("a"), genres))
        # Search for genres in types
        types_url = f"/{types}/"
        return [
            {
                "name": genre[j].text,
                "name_en": genre[j]
                .attrs["href"]
                .replace(types_url, "")
                .replace("/", ""),
                "url": genre[j].attrs["href"],
            }
            for genre in genres
            for j in range(len(genre))
            if genre[j].attrs["href"].find(types_url) != -1
        ]

    @staticmethod
    def get_content_info(self, content):
        """Get content info from the given content element"""
        content_info = {
            "id": int(content.attrs["data-id"]),
            "type": content.find("i", class_="entity").text,
        }
        content_info["title"] = (
            content.find("div", class_="b-content__inline_item-link").find("a").text
        )
        content_info["mirrorLessUrl"] = content.find("div").find("a").attrs["href"]
        content_info["imageUrl"] = content.find("img").attrs["src"]
        session = HTMLSession()
        resp = session.post(
            f"{self.mirror}/engine/ajax/quick_content.php",
            headers=self.headers,
            params={"id": content_info["id"], "is_touch": 1},
        )
        details_info = BS(resp.html.html, "html.parser")
        session.close()
        details_info_text = details_info.find_all(
            "div", class_="b-content__bubble_text"
        )
        for i in range(len(details_info_text)):
            if (
                details_info_text[i].text != ""
                and content_info.get("description") is None
            ):
                content_info["description"] = details_info_text[i].text.strip()
                continue
            if details_info_text[i].find("span").text == "Возрастное ограничение:":
                content_info["age"] = details_info_text[i].find("b").text
                continue
            if details_info_text[i].find("span").text == "Жанр:":
                genres = details_info_text[i].find_all("a")
                content_info["genres"] = ", ".join(
                    list(map(lambda genre: genre.text, genres))
                )
                continue
        item_link = (
            content.find("div", class_="b-content__inline_item-link")
            .find("div")
            .text.split(",")
        )
        try:
            content_info["year"] = item_link[0].strip()
        except IndexError:
            content_info["year"] = None
        return content_info

    @staticmethod
    def get_url_by_id(mirror, id):
        """Get the URL for the given ID"""
        url = f"{mirror}/engine/ajax/quick_content.php"
        data = {"id": id, "is_touch": 1}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "Accept": "application/json",
        }
        r = requests.get(url, headers=headers, params=data)
        html = BS(r.content, "lxml")
        try:
            return (
                html.find("div", class_="b-content__bubble_title")
                .find("a")
                .attrs["href"]
            )
        except:
            return "error"

    @staticmethod
    def get_concrete_content_info(url):
        # Set headers for request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        }
        # Make request and parse response
        try:
            r = requests.get(url, headers=headers)
            html = BS(r.content, "html5lib")
        except Exception as e:
            print(f"Error making request: {e}")
            return {
                "error": 1,
                "error_code": 401,
                "error_message": f"Error making request: {e}",
            }
        # Initialize content info
        content_info = {"id": int(html.find(id="post_id").attrs["value"])}
        content_info["url"] = url
        content_info["type"] = (
            html.find("meta", property="og:type").attrs["content"].split(".")[-1]
        )
        content_info["title"] = html.find("div", class_="b-post__title").find("h1").text
        content_info["description"] = html.find(
            "div", class_="b-post__description_text"
        ).text.strip()
        content_info["imageUrl"] = (
            html.find("div", class_="b-sidecover").find("a").attrs["href"]
        )
        # Get data from table
        table = html.find("table", class_="b-post__info")
        if table is not None:
            table_body = table.find("tbody")
            rows = table_body.find_all("tr")
            data = {}
            for row in rows[:-1]:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                data[str(DataAtribute(cols[0].replace(":", "")))] = cols[1]
            # Convert time
            time = data.get("time")
            if time is not None and time.find(" мин.") != -1:
                time = time.replace(" мин.", "")
                if time.find(":") != -1:
                    hour, minute = time.split(":")
                    hour = int(hour)
                    minute = int(minute)
                else:
                    hour, minute = divmod(int(time), 60)
                if hour < 10:
                    hour = f"0{str(hour)}"
                if minute < 10:
                    minute = f"0{str(minute)}"
                data["time"] = f"{str(hour)}:{str(minute)}"
            # Get actors
            actors = [
                f"{actor.text} " for actor in rows[-1].find_all("span", class_="item")
            ]
            data["actors"] = "".join(actors).replace(" и другие ", "").strip()
            # Remove unnecessary data
            data.pop("is_series_bad", None)
            data.pop("list_bad", None)
            # Add data to content info
            content_info["data"] = data
        # Get translations
        content_info["translations_id"] = []
        translations = html.find("ul", id="translators-list")
        if translations is not None:
            for translation in translations.find_all("li"):
                content_info["translations_id"].append(
                    {
                        "name": translation.text,
                        "id": translation.attrs["data-translator_id"],
                    }
                )
        # Return content info
        return content_info


class DataAtribute:
    def __init__(self, name):
        """
        Class for mapping data atributes
        Parameters:
            name (str): Name of the data atribute
        """
        array = {
            "Рейтинги": "rating",
            "Слоган": "slogan",
            "Дата выхода": "release",
            "Страна": "country",
            "Режиссер": "director",
            "Жанр": "genre",
            "В качестве": "quality",
            "Возраст": "age",
            "Время": "time",
            "Год": "year",
            "Из серии": "is_series_bad",
            "В переводе": "translation",
            "В ролях актеры": "actors",
            "Входит в списки": "list_bad",
        }
        try:
            self.name = array[name]
        except KeyError:
            print("Error: Invalid name provided")
            self.name = None

    def __str__(self):
        return self.name
