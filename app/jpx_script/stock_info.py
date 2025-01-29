import os
from time import sleep

import jaconv
import pandas as pd
import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()


class StockInfo:
    """東証上場銘柄一覧を取得するクラス"""

    def __init__(self, save_path):
        self.save_path = save_path
        self.url = os.getenv("TSE_STOCK_LIST_URL")
        self.info = self.get_info()

    def get_info(self):
        """東証上場銘柄一覧を取得する"""
        sleep(3)  # 3秒待機
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
        """東証上場銘柄一覧をデータフレームに変換する"""
        # self.save_pathからエクセルファイルを読み込んで処理する処理
        df = pd.read_excel(self.save_path)
        df = self.__convert_full_to_half(df)
        df.columns = [
            "input_date",
            "code",
            "name",
            "market_or_type",
            "industry_33_code",
            "industry_33_name",
            "industry_17_code",
            "industry_17_name",
            "scale_code",
            "scale_name",
        ]
        # dfの全ての要素に対して、"-"をNoneに変換
        df = df.replace("-", None)
        # 特定のカラムを文字列に変換
        df["input_date"] = df["input_date"].astype(str)
        df["code"] = df["code"].astype(str)
        return df

    def __convert_full_to_half(self, df):
        """データフレームの全角文字を半角に変換する"""

        def full_to_half(text):
            if isinstance(text, str):
                return jaconv.z2h(text, kana=False, ascii=True, digit=True)
            return text

        # 各列に対してmapを適用
        for col in df.columns:
            df[col] = df[col].map(full_to_half)
        return df

    def get_info_to_json(self):
        """東証上場銘柄一覧をJSON形式に変換する"""
        df = self.get_info_to_df()
        return df.to_json(orient="records", force_ascii=False)

    def convert_to_csv(self, save_path):
        """データフレームをCSV形式で保存する"""
        df = self.get_info_to_df()
        df.to_csv(save_path, index=False)
        print(f"CSVファイルを保存しました: {save_path}")


# 使用例
save_path = "output/excel/data_j.xls"
stock_info = StockInfo(save_path)
stock_info.get_info_to_df()
json_data = stock_info.get_info_to_json()
save_path = "output/excel/data_j.csv"
stock_info.convert_to_csv(save_path)
