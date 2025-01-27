import json

import jaconv
import pandas as pd
import requests


class StockInfo:
    def __init__(self, save_path):
        self.save_path = save_path
        self.url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
        self.info = self.get_info()

    def get_info(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            with open(self.save_path, "wb") as file:
                file.write(response.content)
            print(f"ファイルが保存されました: {self.save_path}")
        else:
            print(
                f"ファイルのダウンロードに失敗しました。ステータスコード: {response.status_code}"
            )
        return response.content

    def get_info_to_df(self):
        # self.save_pathからエクセルファイルを読み込んで処理する処理
        df = pd.read_excel(self.save_path)
        df = self.convert_full_to_half(df)
        return df

    def convert_full_to_half(self, df):
        def full_to_half(text):
            if isinstance(text, str):
                return jaconv.z2h(text, kana=False, ascii=True, digit=True)
            return text

        return df.applymap(full_to_half)

    def get_info_to_json(self):
        df = self.get_info_df()
        return df.to_json(orient="records", force_ascii=False)


# 使用例
save_path = "/Users/user/Vscode/XBRL_Parse_Project/stock-link-parser/output/excel/data_j.xls"
stock_info = StockInfo(save_path)
stock_info.get_info_to_df()
json_data = stock_info.get_info_to_json()
