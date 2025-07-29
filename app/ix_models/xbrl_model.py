import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

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
from app.ix_manager.link_manager import LinkHrefMasterManager
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
        xbrl_zip_path: Union[str, Path],
        output_path: Union[str, Path],
        is_exist_source_file_id_api_url: Optional[str] = None,
    ) -> None:
        super().__init__(xbrl_zip_path, output_path)
        self.is_exist_source_file_id_api_url: Optional[str] = (
            is_exist_source_file_id_api_url
        )
        self.__all_items: Optional[List[Dict[str, Any]]] = None
        self._ixbrl_manager: Optional[IXBRLManager] = None
        self._label_manager: Optional[LabelManager] = None
        self._cal_link_manager: Optional[CalLinkManager] = None
        self._def_link_manager: Optional[DefLinkManager] = None
        self._pre_link_manager: Optional[PreLinkManager] = None
        self._schema_manager: Optional[SchemaManager] = None
        self._qualitative_manager: Optional[QualitativeManager] = None
        self._link_href_master_manager: Optional[LinkHrefMasterManager] = None

        # イベントオブジェクトを作成
        self.ixbrl_manager_initialized: threading.Event = threading.Event()

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._init_manager, LabelManager): "label_manager",
                executor.submit(self._init_manager, CalLinkManager): "cal_link_manager",
                executor.submit(self._init_manager, DefLinkManager): "def_link_manager",
                executor.submit(self._init_manager, PreLinkManager): "pre_link_manager",
                executor.submit(
                    self._init_manager, LinkHrefMasterManager
                ): "link_href_master_manager",
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
                    print(f"{manager_name}の初期化中にエラーが発生しました: {e}")
                    traceback.print_exc()  # ここでスタックトレースを出力
            # ixbrl_managerの初期化が完了したことを通知
            self.ixbrl_manager_initialized.set()

        # if self.__ixbrl_manager is None:
        #     raise XbrlListEmptyError("XBRLファイルが空です。")

    def _init_manager(
        self, manager_class: Type[BaseXbrlManager]
    ) -> Optional[BaseXbrlManager]:
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
            print(e)
            return None

    @property
    def schema_manager(self) -> Optional[SchemaManager]:
        return self._schema_manager

    @property
    def ixbrl_manager(self) -> Optional[IXBRLManager]:
        return self._ixbrl_manager

    @property
    def label_manager(self) -> Optional[LabelManager]:
        return self._label_manager

    @property
    def cal_link_manager(self) -> Optional[CalLinkManager]:
        return self._cal_link_manager

    @property
    def def_link_manager(self) -> Optional[DefLinkManager]:
        return self._def_link_manager

    @property
    def pre_link_manager(self) -> Optional[PreLinkManager]:
        return self._pre_link_manager

    @property
    def qualitative_manager(self) -> Optional[QualitativeManager]:
        return self._qualitative_manager

    @property
    def all_items(self) -> List[Dict[str, Any]]:
        if self.__all_items is None:
            self.__all_items = self.get_all_items()
        return self.__all_items

    @property
    def link_href_master_manager(self) -> Optional[LinkHrefMasterManager]:
        return self._link_href_master_manager

    def __del__(self) -> None:
        super().__del__()
        self._ixbrl_manager = None
        self._label_manager = None
        self._cal_link_manager = None
        self._def_link_manager = None
        self._pre_link_manager = None
        self._schema_manager = None
        self._qualitative_manager = None
        self._link_href_master_manager = None

    def get_schema(self) -> Optional[SchemaManager]:
        return self.schema_manager

    def get_ixbrl(self) -> Optional[IXBRLManager]:
        return self.ixbrl_manager

    def get_label(self) -> Optional[LabelManager]:
        return self.label_manager

    def get_cal_link(self) -> Optional[CalLinkManager]:
        return self.cal_link_manager

    def get_def_link(self) -> Optional[DefLinkManager]:
        return self.def_link_manager

    def get_pre_link(self) -> Optional[PreLinkManager]:
        return self.pre_link_manager

    def get_qualitative(self) -> Optional[QualitativeManager]:
        return self.qualitative_manager

    def get_link_href_master(self) -> Optional[LinkHrefMasterManager]:
        return self.link_href_master_manager

    def get_all_manager(self) -> Dict[str, Any]:
        """XBRLファイルに含まれる全てのマネージャを取得します"""
        all_data: Dict[str, Any] = {
            # テーブルの外部キー制約に沿ってキーを追加してください。
            # ...
            "ix": self.get_ixbrl(),
            "lab": self.get_label(),
            "cal": self.get_cal_link(),
            "def": self.get_def_link(),
            "pre": self.get_pre_link(),
            "href": self.get_link_href_master(),
            "qualitative": self.get_qualitative(),
            "schema": self.get_schema(),  # チェック機能のために必ず最後に追加してください。
        }
        # all_dataから値がNoneのものを削除
        items: Dict[str, Any] = {k: v for k, v in all_data.items() if v is not None}

        return items

    def ixbrl_roles(self):
        if self.ixbrl_manager:
            for value in self.ixbrl_manager.ixbrl_roles():
                yield value

    def get_all_items(self) -> List[Dict[str, Any]]:
        """<p>XBRLファイルに含まれる全てのデータを取得します。</p>
        <p>取得した辞書のキーはget_all_items_keys()で取得できます</p>
        """
        # ixbrl_managerの初期化が完了するまで待機
        # self.ixbrl_manager_initialized.wait()
        # マネージャークラスの
        lists: List[Dict[str, Any]] = []

        file_path: Dict[str, Any] = {  # ファイルパスを追加
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
        keys: List[str] = []
        for item in self.all_items:
            keys.append(item["key"])

        # keysの重複を削除
        keys = list(set(keys))

        return keys

    def ix_header(self):
        if self.ixbrl_manager:
            return self.ixbrl_manager.ix_header
        return None

    def get_file_path(self) -> FilePath:
        return FilePath(head_item_key=self.head_item_key, path=self.xbrl_zip_path)

    def _init_ixbrl_manager(self) -> IXBRLManager:
        ixbrl_manager = IXBRLManager(
            self.directory_path, head_item_key=self.head_item_key
        )
        return ixbrl_manager

    def __str__(self) -> str:
        # ixbrl_managerの初期化が完了するまで待機
        self.ixbrl_manager_initialized.wait()
        if self.ix_header():
            header = self.ix_header().__dict__
            return f" - {header['reporting_date']} [{header['securities_code']}] {header['company_name']} <{header['document_name']}>"
        return "XBRLModel"
