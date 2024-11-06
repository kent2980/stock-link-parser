import pprint
from pathlib import Path
from typing import Dict, List

import requests

from app.api import endpoints as ep
from app.api.settings import Settings
from app.ix_models import XBRLModel
from app.utils.utils import Utils

settings = Settings()
import gc

from tqdm import tqdm

from app.exception.xbrl_model_exception import NotXbrlDirectoryException


class Insert:
    """APIにデータを挿入するためのクラス
    <h3>Attributes:</h3>
        output_path: 出力先ディレクトリ
    """

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.url = settings.API_URL + "/api/v1"

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

        zip_paths = list(Path(dir_path).rglob("*.zip"))

        with tqdm(total=len(zip_paths)) as pbar:
            for zip_path in zip_paths:
                xbrl_id = Utils.string_to_uuid(Path(zip_path).name)
                response = requests.get(
                    self.url + ep.IS_CHECK_MODEL,
                    params={"xbrl_id": xbrl_id},
                )
                if response.status_code == 200:
                    if response.json():
                        pbar.write(f"Already exists: {zip_path}")
                        pbar.update(1)
                        continue
                else:
                    try:
                        model = XBRLModel(
                            zip_path.as_posix(), self.output_path
                        )
                        items = model.get_all_items()
                        is_push = self.__insert_api_push(items)
                        if is_push:
                            pbar.write(f"Success: {model}")
                        else:
                            pbar.write(f"Error: {model}")
                    except NotXbrlDirectoryException:
                        pbar.write(f"無効なXBRLファイル: {zip_path}")
                    pbar.update(1)
                    gc.collect()

    def __insert_api_push(self, items: List[Dict[str, any]]) -> bool:
        for item in items:
            response = None
            if item:
                data = item["item"]
                if item["key"] == "ix_file_path":
                    response = self.file_path(data)
                elif item["key"] == "ix_head_title":
                    response = self.ix_head_titles(data)
                elif item["key"].endswith("source_file"):
                    response = self.sources(data)
                elif item["key"] == "sc_linkbase_ref":
                    response = self.schemas(data)
                elif item["key"] == "ix_non_numeric":
                    response = self.ix_non_numerics(data)
                elif item["key"] == "ix_non_fraction":
                    response = self.ix_non_fractions(data)
                elif item["key"] == "lab_link_locs":
                    response = self.label_locs(data)
                elif item["key"] == "lab_link_arcs":
                    response = self.label_arcs(data)
                elif item["key"] == "lab_link_values":
                    response = self.label_values(data)
                elif item["key"] == "cal_link_locs":
                    response = self.cal_locs(data)
                elif item["key"] == "cal_link_arcs":
                    response = self.cal_arcs(data)
                elif item["key"] == "pre_link_locs":
                    response = self.pre_locs(data)
                elif item["key"] == "pre_link_arcs":
                    response = self.pre_arcs(data)
                elif item["key"] == "def_link_locs":
                    response = self.def_locs(data)
                elif item["key"] == "def_link_arcs":
                    response = self.def_arcs(data)
                elif item["key"] == "qualitative_info":
                    response = self.qualitative(data)

                if response:
                    if response.status_code != 200:
                        return False

        return True
