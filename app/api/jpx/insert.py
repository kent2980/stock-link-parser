import json

import requests

from app.api import endpoints as ep
from app.jpx_script.stock_info import StockInfo as si
from app.jpx_script.stock_info import save_path


class Insert:
    """APIにデータを挿入するためのクラス
    <h3>Attributes:</h3>
        output_path: 出力先ディレクトリ
    """

    def __init__(self, api_base_url: str = None):
        self.url = api_base_url + "/api/v1"
        self.data = self.get_stock_info_data()

    def jpx_stock_info(self):
        url = self.url + ep.POST_JPX_STOCK_INFOS
        response = requests.post(url, json={"data": self.data})
        return response

    def get_stock_info_data(self):
        save_path = "output/excel/data_j.xls"
        info = si(save_path)
        return json.loads(info.get_info_to_json())


if __name__ == "__main__":
    api_base_url = "http://172.17.0.1"
    insert = Insert(api_base_url)
    insert.jpx_stock_info()
