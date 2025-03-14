from time import sleep

import requests

from app.api import endpoints as ep
from app.stock_info_api.wiki_reader import NotDataFoundError, WikiReader


class Insert:
    """APIにデータを挿入するためのクラス
    <h3>Attributes:</h3>
        output_path: 出力先ディレクトリ
    """

    def __init__(self, api_base_url: str = None):
        self.url = api_base_url + "/api/v1"
        self.data = self.jpx_stock_info()

    def jpx_stock_info(self):
        url = self.url + ep.GET_JPX_STOCK_INFO_LIST
        response = requests.get(url)
        return response.json().get("data")

    def load_wiki(self):
        wiki = WikiReader()
        for item in self.data:
            code, name, description, url = None, None, None, None
            try:
                code, name = item.get("code"), item.get("name")
                wiki.word = f"{name} {code} 市場情報"
                description = wiki.get_description()
                wiki_url = wiki.get_url()
                data = {
                    "code": code,
                    "name": name,
                    "description": description,
                    "url": wiki_url,
                }
            except NotDataFoundError as e:
                code, name = item.get("code"), item.get("name")
                data = {
                    "code": code,
                    "name": name,
                    "description": None,
                    "url": None,
                }
            url = self.url + ep.POST_WIKI
            response = requests.post(url, json=data)
            try:
                response_json = response.json()
                print(response_json)
            except requests.exceptions.JSONDecodeError:
                print("JSONDecodeError: Invalid JSON response")
                print(response.text)
            # 1秒待機
            sleep(3)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value


if __name__ == "__main__":
    api_base_url = "http://localhost:8000"
    insert = Insert(api_base_url)
    insert.load_wiki()
