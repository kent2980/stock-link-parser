import pprint
from pathlib import Path
from typing import Dict, List

import requests

from app.api import endpoints as ep
from app.api.settings import Settings
from app.ix_models import XBRLModel

settings = Settings()
from tqdm import tqdm


class Insert:
    """APIにデータを挿入するためのクラス
    <h3>Attributes:</h3>
        output_path: 出力先ディレクトリ
    """

    def __init__(self, output_path):
        self.output_path = output_path
        self.url = settings.API_URL

    def ix_head_titles(self, data):
        url = self.url + ep.POST_HEAD_TITLES
        response = requests.post(url, json={"data": data})
        return response

    def ix_non_numerics(self, data):
        url = self.url + ep.POST_NON_NUMERICS
        response = requests.post(url, json={"data": data})
        return response

    def ix_non_fractions(self, data):
        url = self.url + ep.POST_NON_FRACTIONS
        response = requests.post(url, json={"data": data})
        return response

    def label_locs(self, data):
        url = self.url + ep.POST_LABEL_LOCS
        response = requests.post(url, json={"data": data})
        return response

    def label_arcs(self, data):
        url = self.url + ep.POST_LABEL_ARCS
        response = requests.post(url, json={"data": data})
        return response

    def label_values(self, data):
        url = self.url + ep.POST_LABEL_VALUES
        response = requests.post(url, json={"data": data})
        return response

    def cal_locs(self, data):
        url = self.url + ep.POST_CAL_LOCS
        response = requests.post(url, json={"data": data})
        return response

    def cal_arcs(self, data):
        url = self.url + ep.POST_CAL_ARCS
        response = requests.post(url, json={"data": data})
        return response

    def pre_locs(self, data):
        url = self.url + ep.POST_PRE_LOCS
        response = requests.post(url, json={"data": data})
        return response

    def pre_arcs(self, data):
        url = self.url + ep.POST_PRE_ARCS
        response = requests.post(url, json={"data": data})
        return response

    def def_locs(self, data):
        url = self.url + ep.POST_DEF_LOCS
        response = requests.post(url, json={"data": data})
        return response

    def def_arcs(self, data):
        url = self.url + ep.POST_DEF_ARCS
        response = requests.post(url, json={"data": data})
        return response

    def sources(self, data):
        url = self.url + ep.POST_SOURCES
        response = requests.post(url, json={"data": data})
        return response

    def schemas(self, data):
        url = self.url + ep.POST_SCHEMAS
        response = requests.post(url, json={"data": data})
        return response

    def file_path(self, data):
        url = self.url + ep.POST_FILE_PATH
        response = requests.post(url, json=data)
        return response

    def qualitative(self, data):
        url = self.url + ep.POST_QUALITATIVE
        response = requests.post(url, json={"data": data})
        return response

    def insert_xbrl_zip(self, zip_path):
        """
        <p>XBRLファイルを解析し、APIにデータを挿入します。</p>
        <p>このメソッドは単体のXBRLファイルを解析する際に使用します。</p>
        <h3>Attributes:</h3>
            zip_path (str): XBRLファイルのzipファイルのパス
        """
        model = XBRLModel(zip_path, self.output_path)
        items = model.get_all_items()
        err_endpoints = self.__insert_api_push(items)
        if len(err_endpoints) > 0:
            print(model)
            print(f"下記のエンドポイントでエラーが発生しました。")
            pprint.pprint(err_endpoints)
        else:
            print(f"Success: {model}")

    def insert_xbrl_dir(self, dir_path):
        """
        <p>XBRLファイルを解析し、APIにデータを挿入します。</p>
        <p>このメソッドは複数のXBRLファイルを解析する際に使用します。</p>
        <h3>Attributes:</h3>
            dir_path (str): XBRLファイルのディレクトリのパス
        """

        models_length = len(list(Path(dir_path).rglob("*.zip")))
        count = 0

        with tqdm(total=models_length) as pbar:
            for model in XBRLModel.xbrl_models(dir_path, self.output_path):
                if model is None:
                    pbar.update(1)
                    continue
                items = model.get_all_items()
                err_endpoints = self.__insert_api_push(items)
                if len(err_endpoints) > 0:
                    pbar.write(
                        f"Felled: {model} すでにデータが登録されております。"
                    )
                else:
                    pbar.write(f"Success: {model}")
                    count += 1

                pbar.update(1)

    def __insert_api_push(self, items: List[Dict[str, any]]):
        err_endpoints = []
        for item in items:
            if item:
                data = item["item"]
                if item["key"] == "ix_file_path":
                    response = self.file_path(data)
                    if response.status_code != 200:
                        err_endpoints.append("ix_file_path")
                        break
                elif item["key"] == "ix_head_title":
                    response = self.ix_head_titles(data)
                    if response.status_code != 200:
                        err_endpoints.append("ix_head_title")
                elif item["key"].endswith("source_file"):
                    response = self.sources(data)
                    if response.status_code != 200:
                        err_endpoints.append("source_file")
                elif item["key"] == "sc_linkbase_ref":
                    response = self.schemas(data)
                    if response.status_code != 200:
                        err_endpoints.append("sc_linkbase_ref")
                elif item["key"] == "ix_non_numeric":
                    response = self.ix_non_numerics(data)
                    if response.status_code != 200:
                        err_endpoints.append("ix_non_numeric")
                elif item["key"] == "ix_non_fraction":
                    response = self.ix_non_fractions(data)
                    if response.status_code != 200:
                        err_endpoints.append("ix_non_fraction")
                elif item["key"] == "lab_link_locs":
                    response = self.label_locs(data)
                    if response.status_code != 200:
                        err_endpoints.append("lab_link_locs")
                elif item["key"] == "lab_link_arcs":
                    response = self.label_arcs(data)
                    if response.status_code != 200:
                        err_endpoints.append("lab_link_arcs")
                elif item["key"] == "lab_link_values":
                    response = self.label_values(data)
                    if response.status_code != 200:
                        err_endpoints.append("lab_link_values")
                elif item["key"] == "cal_link_locs":
                    response = self.cal_locs(data)
                    if response.status_code != 200:
                        err_endpoints.append("cal_link_locs")
                elif item["key"] == "cal_link_arcs":
                    response = self.cal_arcs(data)
                    if response.status_code != 200:
                        err_endpoints.append("cal_link_arcs")
                elif item["key"] == "pre_link_locs":
                    response = self.pre_locs(data)
                    if response.status_code != 200:
                        err_endpoints.append("pre_link_locs")
                elif item["key"] == "pre_link_arcs":
                    response = self.pre_arcs(data)
                    if response.status_code != 200:
                        err_endpoints.append("pre_link_arcs")
                elif item["key"] == "def_link_locs":
                    response = self.def_locs(data)
                    if response.status_code != 200:
                        err_endpoints.append("def_link_locs")
                elif item["key"] == "def_link_arcs":
                    response = self.def_arcs(data)
                    if response.status_code != 200:
                        err_endpoints.append("def_link_arcs")
                elif item["key"] == "qualitative_info":
                    response = self.qualitative(data)
                    if response.status_code != 200:
                        err_endpoints.append("qualitative_info")
                else:
                    continue

        return err_endpoints
