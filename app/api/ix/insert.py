import gc
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests
from tqdm import tqdm

from app.api import endpoints as ep
from app.exception.xbrl_model_exception import NotXbrlDirectoryException
from app.ix_models import XBRLModel
from app.ix_models.xbrl_model import XBRLDataProtocol
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

        # ログファイルの設定（プロジェクトルートディレクトリに出力）
        # プロジェクトルートディレクトリを取得
        current_file = Path(__file__)
        project_root = (
            current_file.parent.parent.parent.parent
        )  # app/api/ix/insert.py から4階層上がプロジェクトルート
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_filename = f"api_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file = log_dir / log_filename

        # ロガーの設定
        self.logger = logging.getLogger(f"Insert_{id(self)}")
        self.logger.setLevel(logging.INFO)

        # ハンドラーが既に存在する場合は削除
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # ファイルハンドラーの追加
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # フォーマッターの設定
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        self.logger.info(
            f"Insert instance initialized. Output path: {output_path}, API URL: {api_base_url}"
        )

    def ix_head_titles(self, data):
        url = self.url + ep.POST_HEAD_TITLES
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def ix_non_numerics(self, data):
        url = self.url + ep.POST_NON_NUMERICS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def ix_non_fractions(self, data):
        url = self.url + ep.POST_NON_FRACTIONS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def label_locs(self, data):
        url = self.url + ep.POST_LABEL_LOCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def label_arcs(self, data):
        url = self.url + ep.POST_LABEL_ARCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def label_values(self, data):
        url = self.url + ep.POST_LABEL_VALUES
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def cal_locs(self, data):
        url = self.url + ep.POST_CAL_LOCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def cal_arcs(self, data):
        url = self.url + ep.POST_CAL_ARCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def pre_locs(self, data):
        url = self.url + ep.POST_PRE_LOCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def pre_arcs(self, data):
        url = self.url + ep.POST_PRE_ARCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def def_locs(self, data):
        url = self.url + ep.POST_DEF_LOCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def def_arcs(self, data):
        url = self.url + ep.POST_DEF_ARCS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def loc_href_master(self, data):
        url = self.url + ep.POST_LOC_HREF_MASTER
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def sources(self, data):
        url = self.url + ep.POST_SOURCES
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def schemas(self, data):
        url = self.url + ep.POST_SCHEMAS
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def file_path(self, data):
        url = self.url + ep.POST_FILE_PATH
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def qualitative(self, data):
        url = self.url + ep.POST_QUALITATIVE
        response = requests.post(url, json={"data": data})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def set_head_active(self, head_item_key):
        url = self.url + ep.UPDATE_HEAD_ACTIVE
        response = requests.patch(url, params={"head_item_key": head_item_key})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    def is_active_head(self, head_item_key):
        url = self.url + ep.IS_ACTIVE_HEAD
        response = requests.get(url, params={"head_item_key": head_item_key})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response.json()

    def update_head_generate(self, head_item_key):
        url = self.url + ep.UPDATE_HEAD_GENERATE
        response = requests.patch(url, params={"head_item_key": head_item_key})
        # レスポンスエラーをログに記録
        self.__response_error_logging(response)
        return response

    # レスポンスエラーをログに記録するためのメソッド
    def __response_error_logging(self, response):
        if response.status_code != 200:
            error_msg = f"API Error - Status: {response.status_code}, Response: {response.text[:200]}"
            self.logger.error(error_msg)
            self.logger.error(f"Request headers: {dict(response.request.headers)}")

            try:
                if response.text.strip():
                    error_data = response.json()
                    self.logger.error(f"Error data: {error_data}")
                else:
                    error_empty = f"エラーが発生しました。(locHrefMaster):空のレスポンス - ステータス{response.status_code}"
                    self.logger.error(error_empty)
            except requests.exceptions.JSONDecodeError:
                error_json = f"エラーが発生しました。(locHrefMaster):JSONでないレスポンス - ステータス{response.status_code}, 内容: {response.text[:100]}"
                self.logger.error(error_json)

    def insert_xbrl_zip(self, zip_path):
        """
        <p>XBRLファイルを解析し、APIにデータを挿入します。</p>
        <p>このメソッドは単体のXBRLファイルを解析する際に使用します。</p>
        <h3>Attributes:</h3>
            zip_path (str): XBRLファイルのzipファイルのパス
        """
        # head_item_keyを生成
        head_item_key = Utils.string_to_uuid(Path(zip_path).name)
        # XBRLModelのインスタンスを作成
        model = XBRLModel(zip_path, self.output_path)
        # XBRLファイルから全てのアイテムを取得
        items = model.get_all_items_as_dataclass()

        # APIにデータを挿入
        is_success = self.__insert_api_push(items, head_item_key)
        if is_success:
            # サマリーの挿入
            if not self.generate_summary(head_item_key):
                print(f"サマリーの生成に失敗しました: {model}")
        else:
            print(model)
            print("API挿入でエラーが発生しました。")

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
                        items = model.get_all_items_as_dataclass()
                        # APIへの挿入処理
                        is_push = self.__insert_api_push(items, head_item_key)
                        # サマリーの生成
                        # if self.generate_summary(head_item_key):
                        #     pbar.write(f"サマリーを生成しました: {model}")
                        # else:
                        #     pbar.write(f"サマリーの生成に失敗しました: {model}")
                        # 挿入結果をリストに追加
                        all_push_results.append(is_push)  # 結果をリストに追加
                        if is_push:
                            pbar.write(f"Success: {model}")
                        else:
                            pbar.write(f"Error: {model}")
                    except AttributeError as attr_err:
                        error_msg = (
                            f"AttributeError処理中のファイル: {zip_path} - {attr_err}"
                        )
                        self.logger.error(error_msg)
                        pbar.write(error_msg)
                        all_push_results.append(False)
                    except NotXbrlDirectoryException:
                        pbar.write(f"無効なXBRLファイル: {zip_path}")
                    except Exception as e:
                        error_msg = (
                            f"予期しないエラー処理中のファイル: {zip_path} - {e}"
                        )
                        self.logger.error(error_msg)
                        pbar.write(error_msg)
                        all_push_results.append(False)
                    pbar.update(1)
                    gc.collect()

        # 全てのis_pushがFalseの場合、例外を発生させる
        if not any(all_push_results):
            raise ApiInsertionException("全てのAPI挿入が失敗しました。")

    def __insert_api_push(
        self, data_instance: XBRLDataProtocol, head_item_key: str
    ) -> bool:

        # API呼び出しの成功を追跡するフラグ
        all_success = True

        # 他テーブルから外部参照されているテーブルから優先的に処理
        try:
            self.file_path(data_instance.ix_file_path)
            self.ix_head_titles(data_instance.ix_head_title)
            self.sources(data_instance.get_all_source_files())
            self.schemas(data_instance.sc_linkbase_ref)
            self.loc_href_master(data_instance.href_master)

            # lab_link_locsプロパティの存在を確認してからアクセス
            if hasattr(data_instance, "lab_link_locs"):
                self.label_locs(data_instance.lab_link_locs)
            else:
                self.logger.error(
                    f"lab_link_locsプロパティが存在しません。利用可能なプロパティ: {[prop for prop in dir(data_instance) if not prop.startswith('_')]}"
                )
                all_success = False

            self.label_arcs(data_instance.lab_link_arcs)
            self.label_values(data_instance.lab_link_values)
            self.cal_locs(data_instance.cal_link_locs)
            self.pre_locs(data_instance.pre_link_locs)
            self.def_locs(data_instance.def_link_locs)

        except AttributeError as attr_err:
            error_msg = f"AttributeError in API push: {attr_err}"
            self.logger.error(error_msg)
            print(error_msg)
            all_success = False

        # 並列処理用のAPIエンドポイントリスト
        parallel_apis = [
            ("def_arcs", data_instance.def_link_arcs),
            ("cal_arcs", data_instance.cal_link_arcs),
            ("pre_arcs", data_instance.pre_link_arcs),
            ("ix_non_numerics", data_instance.ix_non_numeric),
            ("ix_non_fractions", data_instance.ix_non_fraction),
            ("qualitative", data_instance.qualitative_info),
        ]

        # 並列処理
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(getattr(self, api_name), data): api_name
                for api_name, data in parallel_apis
            }

            for future in as_completed(futures):
                api_name = futures[future]
                try:
                    response = future.result()  # 実行結果を取得
                    if response.status_code != 200:
                        print(
                            f"API呼び出しが失敗しました ({api_name}): ステータスコード {response.status_code}"
                        )
                        all_success = False
                    else:
                        print(f"Successfully processed {api_name}")
                except Exception as e:
                    print(f"Error processing {api_name}: {e}")
                    all_success = False

        # 最後に送信するAPIエンドポイント
        final_responses = []
        final_responses.append(self.set_head_active(head_item_key))
        final_responses.append(self.update_head_generate(head_item_key))

        # 最終処理のレスポンスをチェック
        for response in final_responses:
            if response.status_code != 200:
                print(
                    f"最終API呼び出しが失敗しました。ステータスコード: {response.status_code}"
                )
                all_success = False

        # すべての処理が成功した場合のみTrueを返す
        return all_success

    def generate_summary(self, head_item_key: str) -> bool:
        """
        <p>IX_TITLE_SUMMARYを生成する</p>
        <h3>Attributes:</h3>
            head_item_key (str): IX_HEAD_TITLEのキー
        """

        response = requests.post(
            self.url + ep.POST_TITLE_SUMMARY + f"?head_item_key={head_item_key}",
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            return False
        elif response.status_code == 200:
            return True
