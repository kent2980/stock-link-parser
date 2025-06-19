import gc
import pprint
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List

import requests
from tqdm import tqdm

from app.api import endpoints as ep
from app.exception.xbrl_model_exception import NotXbrlDirectoryException
from app.ix_models import XBRLModel
from app.utils.utils import Utils

from .exceptions import ApiInsertionException


class Insert:
    """APIにデータを挿入するためのクラス
    <h3>Attributes:</h3>
        output_path: 出力先ディレクトリ
    """

    def __init__(self, output_path: str, api_base_url: str = None):
        self.output_path = output_path
        self.url = api_base_url + "/api/v1"

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
        if response.status_code != 200:
            print(f"エラーが発生しました。(defLocs):{response.json()}")
        return response

    def def_arcs(self, data):
        url = self.url + ep.POST_DEF_ARCS
        response = requests.post(url, json={"data": data})
        if response.status_code != 200:
            print(f"エラーが発生しました。(defArcs){response.json()}")
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

    def set_head_active(self, head_item_key):
        url = self.url + ep.UPDATE_HEAD_ACTIVE
        response = requests.patch(
            url, params={"head_item_key": head_item_key}
        )
        return response

    def is_active_head(self, head_item_key):
        url = self.url + ep.IS_ACTIVE_HEAD
        response = requests.get(
            url, params={"head_item_key": head_item_key}
        )
        if response.status_code == 200:
            return response.json()
        return False

    def update_head_generate(self, head_item_key):
        url = self.url + ep.UPDATE_HEAD_GENERATE
        response = requests.patch(
            url, params={"head_item_key": head_item_key}
        )
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
        <h3>Raises:</h3>
            ApiInsertionException: 全てのAPI挿入が失敗した場合
        """

        zip_paths = list(Path(dir_path).rglob("*.zip"))

        is_source_file_id_api_url = self.url + ep.IS_EXITS_SOURCE_FILE_ID

        all_push_results = []  # 全てのis_push結果を格納するリスト

        with tqdm(total=len(zip_paths)) as pbar:
            for zip_path in zip_paths:
                head_item_key = Utils.string_to_uuid(Path(zip_path).name)
                if self.is_active_head(head_item_key):
                    pbar.write(f"Already exists: {zip_path}")
                    pbar.update(1)
                    continue
                else:
                    try:
                        model = XBRLModel(
                            zip_path.as_posix(),
                            self.output_path,
                            is_exist_source_file_id_api_url=is_source_file_id_api_url,
                        )
                        items = model.get_all_items()
                        is_push = self.__insert_api_push(
                            items, head_item_key
                        )
                        all_push_results.append(
                            is_push
                        )  # 結果をリストに追加
                        if is_push:
                            pbar.write(f"Success: {model}")
                        else:
                            pbar.write(f"Error: {model}")
                    except NotXbrlDirectoryException:
                        pbar.write(f"無効なXBRLファイル: {zip_path}")
                    pbar.update(1)
                    gc.collect()

        # 全てのis_pushがFalseの場合、例外を発生させる
        if not any(all_push_results):
            raise ApiInsertionException("全てのAPI挿入が失敗しました。")

    def __insert_api_push(
        self, items: List[Dict[str, any]], head_item_key: str
    ) -> bool:
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

        def send_request(item):
            data = item["item"]
            if item["key"] == "sc_linkbase_ref":
                return self.schemas(data)
            elif item["key"] == "ix_non_numeric":
                return self.ix_non_numerics(data)
            elif item["key"] == "ix_non_fraction":
                return self.ix_non_fractions(data)
            elif item["key"] == "lab_link_locs":
                return self.label_locs(data)
            elif item["key"] == "lab_link_arcs":
                return self.label_arcs(data)
            elif item["key"] == "lab_link_values":
                return self.label_values(data)
            elif item["key"] == "cal_link_locs":
                return self.cal_locs(data)
            elif item["key"] == "cal_link_arcs":
                return self.cal_arcs(data)
            elif item["key"] == "pre_link_locs":
                return self.pre_locs(data)
            elif item["key"] == "pre_link_arcs":
                return self.pre_arcs(data)
            elif item["key"] == "def_link_locs":
                return self.def_locs(data)
            elif item["key"] == "def_link_arcs":
                return self.def_arcs(data)
            elif item["key"] == "qualitative_info":
                return self.qualitative(data)
            return None

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(send_request, item): item for item in items
            }

            for future in as_completed(futures):
                item = futures[future]
                try:
                    response = future.result()
                    if response and response.status_code != 200:
                        print(
                            f"エンドポイント({response.url})にデータを追加できませんでした。ステータスコード: {response.status_code}"
                        )
                        return False
                except Exception as e:
                    print(f"リクエスト中にエラーが発生しました: {e}")
                    return False

        response = self.set_head_active(head_item_key)
        response = self.update_head_generate(head_item_key)

        requests.post(
            self.url + ep.POST_TITLE_SUMMARY,
            json={"head_item_key": head_item_key},
        )
        if response.status_code != 200:
            print(
                f"サマリー生成に失敗しました。ステータスコード: {response.status_code}"
            )
        elif response.status_code == 200:
            print(f"サマリーを生成しました: {head_item_key}")

        return True
