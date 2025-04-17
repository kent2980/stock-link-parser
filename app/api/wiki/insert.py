from time import sleep

import requests

from app.api import endpoints as ep
from app.stock_info_api.wiki_reader import NotDataFoundError, WikiReader

extract_urls = [
    "https://ja.wikipedia.org/wiki/TOKYO_PRO_Market",
    "https://ja.wikipedia.org/wiki/日経平均株価",
    "https://ja.wikipedia.org/wiki/ダウ平均株価",
    "https://ja.wikipedia.org/wiki/JPX日経中小型株指数",
    "https://ja.wikipedia.org/wiki/MSCI",
    "https://ja.wikipedia.org/wiki/東京証券取引所",
    "https://ja.wikipedia.org/wiki/東京証券取引所スタンダード市場上場企業一覧",
    "https://ja.wikipedia.org/wiki/東京証券取引所グロース市場上場企業一覧",
    "https://ja.wikipedia.org/wiki/世界金融危機_(2007年-2010年)",
    "https://ja.wikipedia.org/wiki/ヘラクレス_(有価証券市場)",
]


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
        i = 0
        for item in self.data:
            i += 1
            description, url = None, None
            code, name, industry_code = (
                item.get("code"),
                item.get("name"),
                item.get("industry_33_code"),
            )
            if industry_code is None:
                print(
                    f"対象外のデータです。: {code}, {name}",
                    end="\n\n",
                )
                continue
            # wikiテーブルにデータが存在する場合はスキップ
            url = self.url + ep.GET_WIKI_FROM_CODE + code
            response = requests.get(url)
            if response.status_code == 200:
                print(
                    f"データが既に存在しています: {code}, {name}",
                    end="\n\n",
                )
                continue

            # wikiテーブルにデータを追加
            try:
                wiki.word = f"{name}"
                description = wiki.get_description()
                wiki_url = wiki.get_url()
                if wiki_url in extract_urls:
                    print("対象外のURLです", end="\n\n")
                    continue
                data = {
                    "code": code,
                    "name": name,
                    "description": description,
                    "url": wiki_url,
                }
                print(data)
                url = self.url + ep.POST_WIKI
                response = requests.post(url, json=data)
                if (
                    response.status_code == 201
                    or response.status_code == 200
                ):
                    print(f"データを追加しました: {data}", end="\n\n")
                elif response.status_code == 400:
                    print(
                        f"データが既に存在しています: {data}", end="\n\n"
                    )
                else:
                    print(
                        f"データの追加に失敗しました: {data}", end="\n\n"
                    )
            except NotDataFoundError:
                print(
                    f"データが見つかりませんでした: {code}, {name}",
                    end="\n\n",
                )
                continue
            finally:
                sleep(1)

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
