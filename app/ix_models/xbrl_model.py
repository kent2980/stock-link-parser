import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from app.exception import XbrlListEmptyError
from app.ix_manager import (
    BaseXbrlManager,
    CalLinkManager,
    DefLinkManager,
    IXBRLManager,
    LabelManager,
    PreLinkManager,
    QualitativeManager,
    SchemaManager,
)
from app.ix_tag import FilePath

from .base_xbrl_model import BaseXbrlModel


class XBRLModel(BaseXbrlModel):
    """XBRLファイルを扱うためのクラス
    <h3>Attributes:</h3>
        <p>xbrl_zip_path (str): XBRLファイルのzipファイルのパス</p>
        <p>output_path (str): スキーマでURLリンクされている、関係XMLファイルの出力先パス</p>
    """

    def __init__(
        self,
        xbrl_zip_path,
        output_path,
        is_exist_source_file_id_api_url: Optional[str] = None,
    ) -> None:
        super().__init__(xbrl_zip_path, output_path)
        self.is_exist_source_file_id_api_url = (
            is_exist_source_file_id_api_url
        )
        self.__all_items = None
        self._ixbrl_manager = None
        self._label_manager = None
        self._cal_link_manager = None
        self._def_link_manager = None
        self._pre_link_manager = None
        self._schema_manager = None
        self._qualitative_manager = None

        # イベントオブジェクトを作成
        self.ixbrl_manager_initialized = threading.Event()

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    self._init_manager, LabelManager
                ): "label_manager",
                executor.submit(
                    self._init_manager, CalLinkManager
                ): "cal_link_manager",
                executor.submit(
                    self._init_manager, DefLinkManager
                ): "def_link_manager",
                executor.submit(
                    self._init_manager, PreLinkManager
                ): "pre_link_manager",
                executor.submit(
                    SchemaManager,
                    self.directory_path,
                    head_item_key=self.head_item_key,
                ): "schema_manager",
                executor.submit(
                    QualitativeManager,
                    self.directory_path,
                    head_item_key=self.head_item_key,
                ): "qualitative_manager",
                executor.submit(self._init_ixbrl_manager): "ixbrl_manager",
            }

            for future in as_completed(futures):
                manager_name = futures[future]
                try:
                    result = future.result()
                    setattr(self, f"_{manager_name}", result)
                except Exception as e:
                    print(
                        f"{manager_name}の初期化中にエラーが発生しました: {e}"
                    )
            # ixbrl_managerの初期化が完了したことを通知
            self.ixbrl_manager_initialized.set()

        # if self.__ixbrl_manager is None:
        #     raise XbrlListEmptyError("XBRLファイルが空です。")

    def _init_manager(self, manager_class: BaseXbrlManager):
        try:
            if manager_class.__name__ == "LabelManager":
                return manager_class(
                    self.directory_path,
                    self.output_path,
                    head_item_key=self.head_item_key,
                    is_exist_source_file_id_api_url=self.is_exist_source_file_id_api_url,
                )
            else:
                return manager_class(
                    self.directory_path,
                    self.output_path,
                    head_item_key=self.head_item_key,
                )
        except XbrlListEmptyError as e:
            # print(e)
            pass

    @property
    def schema_manager(self):
        return self._schema_manager

    @property
    def ixbrl_manager(self):
        return self._ixbrl_manager

    @property
    def label_manager(self):
        return self._label_manager

    @property
    def cal_link_manager(self):
        return self._cal_link_manager

    @property
    def def_link_manager(self):
        return self._def_link_manager

    @property
    def pre_link_manager(self):
        return self._pre_link_manager

    @property
    def qualitative_manager(self):
        return self._qualitative_manager

    @property
    def all_items(self):
        if self.__all_items is None:
            self.__all_items = self.get_all_items()
        return self.__all_items

    def __del__(self):
        super().__del__()
        self._ixbrl_manager = None
        self._label_manager = None
        self._cal_link_manager = None
        self._def_link_manager = None
        self._pre_link_manager = None
        self._schema_manager = None
        self._qualitative_manager = None

    def get_schema(self):
        return self.schema_manager

    def get_ixbrl(self):
        return self.ixbrl_manager

    def get_label(self):
        return self.label_manager

    def get_cal_link(self):
        return self.cal_link_manager

    def get_def_link(self):
        return self.def_link_manager

    def get_pre_link(self):
        return self.pre_link_manager

    def get_qualitative(self):
        return self.qualitative_manager

    def get_all_manager(self):
        """XBRLファイルに含まれる全てのマネージャを取得します"""
        all_data = {
            # テーブルの外部キー制約に沿ってキーを追加してください。
            # ...
            "ix": self.get_ixbrl(),
            "lab": self.get_label(),
            "cal": self.get_cal_link(),
            "def": self.get_def_link(),
            "pre": self.get_pre_link(),
            "qualitative": self.get_qualitative(),
            "schema": self.get_schema(),  # チェック機能のために必ず最後に追加してください。
        }
        # all_dataから値がNoneのものを削除
        items = {k: v for k, v in all_data.items() if v is not None}

        return items

    def ixbrl_roles(self):
        for value in self.ixbrl_manager.ixbrl_roles():
            yield value

    def get_all_items(self) -> List[Dict[str, any]]:
        """<p>XBRLファイルに含まれる全てのデータを取得します。</p>
        <p>取得した辞書のキーはget_all_items_keys()で取得できます</p>
        """
        # ixbrl_managerの初期化が完了するまで待機
        # self.ixbrl_manager_initialized.wait()
        # マネージャークラスの
        lists = []

        file_path = {  # ファイルパスを追加
            "key": "ix_file_path",
            "item": self.get_file_path().model_dump(),
        }

        lists.append(file_path)

        for _, manager in self.get_all_manager().items():
            for item in manager.items:
                # listsとitemsを結合
                lists.append(item)

        self.__all_items = lists

        return lists

    def get_all_items_keys(self) -> List[str]:
        """XBRLファイルに含まれる全てのデータのキーを取得します"""
        keys = []
        for item in self.all_items:
            keys.append(item["key"])

        # keysの重複を削除
        keys = list(set(keys))

        return keys

    def ix_header(self):
        return self.ixbrl_manager.ix_header

    def get_file_path(self):
        return FilePath(
            head_item_key=self.head_item_key, path=self.xbrl_zip_path
        )

    def _init_ixbrl_manager(self):
        self.__ixbrl_manager = IXBRLManager(
            self.directory_path, head_item_key=self.head_item_key
        )
        return self.__ixbrl_manager

    def __str__(self):
        # ixbrl_managerの初期化が完了するまで待機
        self.ixbrl_manager_initialized.wait()
        header = self.ix_header().__dict__
        return f" - {header['reporting_date']} [{header['securities_code']}] {header['company_name']} <{header['document_name']}>"
