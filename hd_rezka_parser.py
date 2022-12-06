from bs4 import BeautifulSoup as BS
import requests
from requests_html import HTMLSession


class HdRezkaParser:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

    def get_content_list(self, mirror):
        session = HTMLSession()
        resp = session.get(self.url, headers=self.headers)
        html = BS(resp.html.html, "html.parser")
        session.close()
        content_list = html.find(
            "div", class_="b-content__inline_items").find_all("div", class_="b-content__inline_item")

        content_list = list(
            map(lambda content: self.get_content_info(content, mirror), content_list))

        return content_list

    @staticmethod
    def get_content_info(content, mirror):
        content_info = {}
        content_info["id"] = int(content.attrs["data-id"])
        content_info["type"] = content.find("i", class_="entity").text
        content_info["title"] = content.find(
            "div", class_="b-content__inline_item-link").find("a").text
        content_info["mirrorLessUrl"] = content.find("div").find(
            "a").attrs["href"]
        content_info["imageUrl"] = content.find("img").attrs["src"]
        content_info["year"] = content.find(
            "div", class_="b-content__inline_item-link").find("div").text.split(',')[0]
        content_info["country"] = content.find(
            "div", class_="b-content__inline_item-link").find("div").text.split(',')[1].strip()
        content_info["genre"] = content.find(
            "div", class_="b-content__inline_item-link").find("div").text.split(',')[2].strip()

        status = content.find("span", class_="info")
        content_info["status"] = None if status is None else status.text
        return content_info

    @staticmethod
    def get_concrete_content_info(url):
        headers = headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
        r = requests.get(url, headers=headers)
        html = BS(r.content, "html5lib")

        content_info = {}
        content_info["id"] = int(html.find(id="post_id").attrs['value'])
        content_info["url"] = url
        content_info["affilation"] = html.find(
            'meta', property="og:type").attrs['content'].split(".")[-1]
        content_info["title"] = html.find(
            'div', class_="b-post__title").find("h1").text
        content_info["description"] = html.find(
            'div', class_="b-post__description_text").text
        content_info["imageUrl"] = html.find(
            'div', class_="b-sidecover").find("a").attrs['href']

        table = html.find("table", class_="b-post__info")
        table_body = table.find("tbody")
        rows = table_body.find_all('tr')
        rows = table_body.find_all('tr')
        data = []
        for row in rows[:-1]:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        actors = [
            f"{actor.text} " for actor in rows[-1].find_all("span", class_="item")]
        data.append(
            [rows[-1].find("span", class_="l inline").text, "".join(actors)])
        content_info["data"] = [{obj[0]: obj[1]} for obj in data]

        content_info["translations"] = []
        translations = html.find("ul", id="translators-list").find_all("li")
        for translation in translations:
            content_info["translations"].append(
                {"name": translation.text, "id": translation.attrs["data-translator_id"]})

        return content_info
