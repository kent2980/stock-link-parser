import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import field, make_dataclass
from pathlib import Path
from typing import (Any, Dict, List, Optional, Protocol, Type, TypedDict,
                    Union, runtime_checkable)

from src.exception import XbrlListEmptyError
from src.ix_manager import (BaseXbrlManager, CalLinkManager, DefLinkManager,
                            IXBRLManager, LabelManager, PreLinkManager,
                            QualitativeManager, SchemaManager)
from src.ix_manager.base_xbrl_manager import ItemDict
from src.ix_manager.link_manager import LinkHrefMasterManager
from src.ix_tag import FilePath

from .base_xbrl_model import BaseXbrlModel


class XBRLItem(TypedDict):
    """XBRLデータのアイテム型定義"""

    key: str
    item: Dict[str, Union[str, int, float, bool, None]]


@runtime_checkable
class XBRLDataProtocol(Protocol):
    """XBRLデータクラスのプロトコル定義
    IDEの型ヒント支援のために使用
    """

    # すべてのプロパティを明示的に定義（実際のデータに基づく）
    cal_link_arcs: List[Dict[str, Any]]  # cal_link_arcs
    cal_link_locs: List[Dict[str, Any]]  # cal_link_locs
    cal_link_roles: List[Dict[str, Any]]  # cal_link_roles
    cal_source_file: List[Dict[str, Any]]  # cal_source_file
    def_link_arcs: List[Dict[str, Any]]  # def_link_arcs
    def_link_locs: List[Dict[str, Any]]  # def_link_locs
    def_link_roles: List[Dict[str, Any]]  # def_link_roles
    def_source_file: List[Dict[str, Any]]  # def_source_file
    href_master: List[Dict[str, Any]]  # href_master
    ix_context: List[Dict[str, Any]]  # ix_context
    ix_file_path: List[Dict[str, Any]]  # ix_file_path
    ix_head_title: List[Dict[str, Any]]  # ix_head_title
    ix_non_fraction: List[Dict[str, Any]]  # ix_non_fraction
    ix_non_numeric: List[Dict[str, Any]]  # ix_non_numeric
    ix_source_file: List[Dict[str, Any]]  # ix_source_file
    lab_link_arcs: List[Dict[str, Any]]  # lab_link_arcs
    lab_link_locs: List[Dict[str, Any]]  # lab_link_locs
    lab_link_values: List[Dict[str, Any]]  # lab_link_values
    lab_source_file: List[Dict[str, Any]]  # lab_source_file
    pre_link_arcs: List[Dict[str, Any]]  # pre_link_arcs
    pre_link_locs: List[Dict[str, Any]]  # pre_link_locs
    pre_link_roles: List[Dict[str, Any]]  # pre_link_roles
    pre_source_file: List[Dict[str, Any]]  # pre_source_file
    qualitative_info: List[Dict[str, Any]]  # qualitative_info
    qualitative_source_file: List[Dict[str, Any]]  # qualitative_source_file
    sc_elements: List[Dict[str, Any]]  # sc_elements
    sc_import: List[Dict[str, Any]]  # sc_import
    sc_linkbase_ref: List[Dict[str, Any]]  # sc_linkbase_ref
    sc_source_file: List[Dict[str, Any]]  # sc_source_file

    # JSON文字列版のプロパティ（元のプロパティ名に_jsonサフィックス）
    cal_link_arcs_json: str  # cal_link_arcs のJSON文字列版
    cal_link_locs_json: str  # cal_link_locs のJSON文字列版
    cal_link_roles_json: str  # cal_link_roles のJSON文字列版
    cal_source_file_json: str  # cal_source_file のJSON文字列版
    def_link_arcs_json: str  # def_link_arcs のJSON文字列版
    def_link_locs_json: str  # def_link_locs のJSON文字列版
    def_link_roles_json: str  # def_link_roles のJSON文字列版
    def_source_file_json: str  # def_source_file のJSON文字列版
    href_master_json: str  # href_master のJSON文字列版
    ix_context_json: str  # ix_context のJSON文字列版
    ix_file_path_json: str  # ix_file_path のJSON文字列版
    ix_head_title_json: str  # ix_head_title のJSON文字列版
    ix_non_fraction_json: str  # ix_non_fraction のJSON文字列版
    ix_non_numeric_json: str  # ix_non_numeric のJSON文字列版
    ix_source_file_json: str  # ix_source_file のJSON文字列版
    lab_link_arcs_json: str  # lab_link_arcs のJSON文字列版
    lab_link_locs_json: str  # lab_link_locs のJSON文字列版
    lab_link_values_json: str  # lab_link_values のJSON文字列版
    lab_source_file_json: str  # lab_source_file のJSON文字列版
    pre_link_arcs_json: str  # pre_link_arcs のJSON文字列版
    pre_link_locs_json: str  # pre_link_locs のJSON文字列版
    pre_link_roles_json: str  # pre_link_roles のJSON文字列版
    pre_source_file_json: str  # pre_source_file のJSON文字列版
    qualitative_info_json: str  # qualitative_info のJSON文字列版
    qualitative_source_file_json: str  # qualitative_source_file のJSON文字列版
    sc_elements_json: str  # sc_elements のJSON文字列版
    sc_import_json: str  # sc_import のJSON文字列版
    sc_linkbase_ref_json: str  # sc_linkbase_ref のJSON文字列版
    sc_source_file_json: str  # sc_source_file のJSON文字列版

    # メタデータ属性
    __property_hints__: Dict[str, type]
    __available_properties__: List[str]

    def __getattr__(self, name: str) -> Any:
        """動的プロパティアクセス用"""
        ...

    def get_source_file_properties(self) -> List[str]:
        """source_fileで終わるプロパティ名のリストを返す"""
        ...

    def get_all_source_files(self) -> List[Dict[str, Any]]:
        """全てのsource_fileプロパティの値を平坦なリストで返す"""
        ...

    def get_all_source_files_json(self) -> str:
        """全てのsource_fileプロパティの値を平坦なリストのJSON文字列で返す"""
        ...

    def get_json_properties(self) -> List[str]:
        """JSON版プロパティ名のリストを返す"""
        ...

    def get_property_as_json(self, property_name: str) -> str:
        """指定されたプロパティのJSON文字列版を返す"""
        ...


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
        self.__all_items: Optional[List[ItemDict]] = None
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
    def all_items(self) -> List[ItemDict]:
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

    def get_all_items(self) -> List[ItemDict]:
        """<p>XBRLファイルに含まれる全てのデータを取得します。</p>
        <p>取得した辞書のキーはget_all_items_keys()で取得できます</p>
        <p>同じkeyを持つItemDictのitemは集約されます</p>
        """
        # ixbrl_managerの初期化が完了するまで待機
        # self.ixbrl_manager_initialized.wait()
        # マネージャークラスの
        lists: List[ItemDict] = []

        # ファイルパス情報をItemDict形式で追加
        file_path_item = ItemDict()
        file_path_item.id = "file_path"
        file_path_item.key = "ix_file_path"
        file_path_item.item = [self.get_file_path().model_dump()]
        file_path_item.sort_position = 0

        lists.append(file_path_item)

        for _, manager in self.get_all_manager().items():
            for item in manager.items:
                # manager.itemsはすでにItemDictのリスト
                lists.append(item)

        # 同じkeyを持つItemDictのitemを集約
        aggregated_items = self._aggregate_items_by_key(lists)

        self.__all_items = aggregated_items

        return aggregated_items

    def _aggregate_items_by_key(self, items: List[ItemDict]) -> List[ItemDict]:
        """同じkeyを持つItemDictのitemを集約する

        Args:
            items: 集約対象のItemDictのリスト

        Returns:
            集約されたItemDictのリスト
        """
        aggregated_dict: Dict[str, ItemDict] = {}

        for item in items:
            key = item.key

            if key not in aggregated_dict:
                # 新しいキーの場合、そのまま追加
                aggregated_dict[key] = ItemDict()
                aggregated_dict[key].id = item.id
                aggregated_dict[key].key = item.key
                aggregated_dict[key].sort_position = item.sort_position
                aggregated_dict[key].item = (
                    item.item.copy() if isinstance(item.item, list) else [item.item]
                )
            else:
                # 既存のキーの場合、itemを集約
                existing_item = aggregated_dict[key]

                # itemが辞書の場合はリストに変換してから追加
                if isinstance(item.item, dict):
                    if isinstance(existing_item.item, list):
                        existing_item.item.append(item.item)
                    else:
                        existing_item.item = [existing_item.item, item.item]
                elif isinstance(item.item, list):
                    if isinstance(existing_item.item, list):
                        existing_item.item.extend(item.item)
                    else:
                        existing_item.item = [existing_item.item] + item.item
                else:
                    # その他の型の場合
                    if isinstance(existing_item.item, list):
                        existing_item.item.append(item.item)
                    else:
                        existing_item.item = [existing_item.item, item.item]

                # sort_positionは最小値を取る
                if item.sort_position < existing_item.sort_position:
                    existing_item.sort_position = item.sort_position

        # sort_positionでソートして返す
        result = list(aggregated_dict.values())
        result.sort(key=lambda x: x.sort_position)

        return result

    def get_all_items_keys(self) -> List[str]:
        """XBRLファイルに含まれる全てのデータのキーを取得します"""
        keys: List[str] = []
        for item in self.all_items:
            key = item.key if hasattr(item, "key") else item["key"]
            keys.append(key)

        # keysの重複を削除
        keys = list(set(keys))

        return keys

    def get_source_file_items(self) -> List[ItemDict]:
        """source_fileで終わるキーを持つアイテムを全て集約して返します

        Returns:
            source_fileで終わるキーを持つItemDictのリスト
        """
        source_file_items: List[ItemDict] = []

        for item in self.all_items:
            if item.key.endswith("source_file"):
                source_file_items.append(item)

        return source_file_items

    def get_aggregated_source_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """source_fileで終わるキーを持つアイテムを辞書形式で集約して返します

        Returns:
            キー名をキーとし、そのアイテムのリストを値とする辞書
        """
        source_file_items = self.get_source_file_items()
        aggregated_dict: Dict[str, List[Dict[str, Any]]] = {}

        for item in source_file_items:
            key = item.key
            # itemがリストの場合はそのまま、辞書の場合はリストに変換
            if isinstance(item.item, list):
                aggregated_dict[key] = item.item
            elif isinstance(item.item, dict):
                aggregated_dict[key] = [item.item]
            else:
                aggregated_dict[key] = [item.item]

        return aggregated_dict

    def get_all_items_as_dataclass(self) -> XBRLDataProtocol:
        """ItemDict.keyをプロパティとした動的データクラスを作成し、プロパティの値をItemDict.itemにした
        データクラスのインスタンスを返します

        Returns:
            ItemDict.keyをプロパティ名として持つデータクラスのインスタンス
            プロパティ名はIDEで型ヒントとして認識されます
        """
        all_items = self.get_all_items()

        # プロパティ名と値のマッピングを作成
        field_definitions = []

        # 型ヒント用の情報を収集
        property_hints = {}

        for item in all_items:
            key = item.key
            # Pythonの識別子として有効でない文字を置換
            safe_key = self._make_safe_identifier(key)

            # 型ヒント情報を保存（より具体的な型情報）
            if isinstance(item.item, list):
                property_hints[safe_key] = List[Dict[str, Any]]
                item_type = List[Dict[str, Any]]
            elif isinstance(item.item, dict):
                property_hints[safe_key] = Dict[str, Any]
                item_type = Dict[str, Any]
            else:
                property_hints[safe_key] = type(item.item)
                item_type = type(item.item)

            # 可変オブジェクトの場合はdefault_factoryを使用
            if isinstance(item.item, (list, dict, set)):
                # default_factoryを使用（具体的な型情報も付与）
                field_definitions.append(
                    (
                        safe_key,
                        item_type,
                        field(default_factory=self._create_factory(item.item)),
                    )
                )
                # JSON版のプロパティも追加
                json_key = safe_key + "_json"
                json_value = self._convert_to_json(item.item)
                property_hints[json_key] = str
                field_definitions.append((json_key, str, json_value))
            else:
                # イミュータブルオブジェクトはそのまま使用
                field_definitions.append((safe_key, item_type, item.item))
                # JSON版のプロパティも追加
                json_key = safe_key + "_json"
                json_value = self._convert_to_json(item.item)
                property_hints[json_key] = str
                field_definitions.append((json_key, str, json_value))

        # 動的データクラスを作成
        XBRLDataClass = make_dataclass(
            "XBRLData",
            field_definitions,
            frozen=True,  # イミュータブルにする
            namespace={
                "__property_hints__": property_hints,  # 型ヒント情報を保存
                "__available_properties__": [
                    item[0] for item in field_definitions
                ],  # 利用可能なプロパティリスト
                "__annotations__": {
                    item[0]: item[1] for item in field_definitions
                },  # 型注釈を明示的に設定
                "get_source_file_properties": self._create_get_source_file_properties_method(
                    field_definitions
                ),
                "get_all_source_files": self._create_get_all_source_files_method(
                    field_definitions
                ),
                "get_all_source_files_json": self._create_get_all_source_files_json_method(
                    field_definitions
                ),
                "get_json_properties": self._create_get_json_properties_method(
                    field_definitions
                ),
                "get_property_as_json": self._create_get_property_as_json_method(
                    field_definitions
                ),
            },
        )

        # インスタンスを作成
        instance = XBRLDataClass()

        # クラスレベルで型注釈を設定（IDEサポート向上のため）
        for prop_name, prop_type in property_hints.items():
            if hasattr(XBRLDataClass, "__annotations__"):
                XBRLDataClass.__annotations__[prop_name] = prop_type
            else:
                XBRLDataClass.__annotations__ = {prop_name: prop_type}

        # プロトコルとして返すことで型ヒントを提供
        return instance  # type: ignore

    def get_dataclass_property_names(self) -> List[str]:
        """データクラスで利用可能なプロパティ名のリストを返します

        IDEでの開発支援のため、実際に利用可能なプロパティ名を事前に確認できます

        Returns:
            プロパティ名のリスト（安全な識別子に変換済み）
        """
        all_items = self.get_all_items()
        property_names = []

        for item in all_items:
            safe_key = self._make_safe_identifier(item.key)
            property_names.append(safe_key)

        return property_names

    def get_dataclass_property_info(self) -> Dict[str, Dict[str, Any]]:
        """データクラスのプロパティ情報を詳細に返します

        Returns:
            プロパティ名をキーとし、以下の情報を含む辞書:
            - original_key: 元のItemDict.key
            - type: 値の型
            - value_sample: 値のサンプル（最初の数要素）
            - has_json_version: JSON版プロパティが存在するか
            - json_property_name: JSON版プロパティ名
        """
        all_items = self.get_all_items()
        property_info = {}

        for item in all_items:
            safe_key = self._make_safe_identifier(item.key)

            # サンプル値（リストの場合は最初の3要素程度）
            value_sample = item.item
            if isinstance(item.item, list) and len(item.item) > 3:
                value_sample = item.item[:3] + ["...（他の要素も存在）"]

            json_property_name = safe_key + "_json"

            property_info[safe_key] = {
                "original_key": item.key,
                "type": type(item.item).__name__,
                "value_sample": value_sample,
                "length": (
                    len(item.item) if isinstance(item.item, (list, dict, str)) else None
                ),
                "has_json_version": True,
                "json_property_name": json_property_name,
            }

        return property_info

    def _create_factory(self, value: Any):
        """default_factory用のファクトリー関数を作成"""

        def factory():
            if isinstance(value, list):
                return value.copy()
            elif isinstance(value, dict):
                return value.copy()
            elif isinstance(value, set):
                return value.copy()
            else:
                return value

        return factory

    def _convert_to_json(self, value: Any) -> str:
        """データをJSON文字列に変換する"""
        import json

        try:
            return json.dumps(value, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as e:
            # JSON変換できない場合は文字列として返す
            return str(value)

    def _create_get_source_file_properties_method(self, field_definitions):
        """get_source_file_propertiesメソッドを生成する"""

        def get_source_file_properties(self_instance):
            return [
                name for name, _, _ in field_definitions if name.endswith("source_file")
            ]

        return get_source_file_properties

    def _create_get_all_source_files_method(self, field_definitions):
        """get_all_source_filesメソッドを生成する"""

        def get_all_source_files(self_instance):
            source_files = []
            for name, _, _ in field_definitions:
                if name.endswith("source_file"):
                    property_value = getattr(self_instance, name)
                    # プロパティの値がリストの場合はそのまま追加、そうでなければリストにしてから追加
                    if isinstance(property_value, list):
                        source_files.extend(property_value)
                    else:
                        source_files.append(property_value)
            return source_files

        return get_all_source_files

    def _create_get_all_source_files_json_method(self, field_definitions):
        """get_all_source_files_jsonメソッドを生成する"""

        def get_all_source_files_json(self_instance):
            import json

            source_files = []
            for name, _, _ in field_definitions:
                if name.endswith("source_file"):
                    property_value = getattr(self_instance, name)
                    # プロパティの値がリストの場合はそのまま追加、そうでなければリストにしてから追加
                    if isinstance(property_value, list):
                        source_files.extend(property_value)
                    else:
                        source_files.append(property_value)

            # JSON文字列に変換
            try:
                return json.dumps(source_files, ensure_ascii=False, default=str)
            except (TypeError, ValueError) as e:
                # JSON変換できない場合は空リストのJSON文字列を返す
                return "[]"

        return get_all_source_files_json

    def _create_get_json_properties_method(self, field_definitions):
        """get_json_propertiesメソッドを生成する"""

        def get_json_properties(self_instance):
            return [name for name, _, _ in field_definitions if name.endswith("_json")]

        return get_json_properties

    def _create_get_property_as_json_method(self, field_definitions):
        """get_property_as_jsonメソッドを生成する"""

        def get_property_as_json(self_instance, property_name: str):
            json_property_name = property_name + "_json"
            if hasattr(self_instance, json_property_name):
                return getattr(self_instance, json_property_name)
            else:
                # JSON版が存在しない場合は元のプロパティをJSON変換
                if hasattr(self_instance, property_name):
                    import json

                    value = getattr(self_instance, property_name)
                    try:
                        return json.dumps(value, ensure_ascii=False, default=str)
                    except (TypeError, ValueError):
                        return str(value)
                else:
                    raise AttributeError(f"Property '{property_name}' not found")

        return get_property_as_json

    def _make_safe_identifier(self, name: str) -> str:
        """文字列をPythonの有効な識別子に変換する

        Args:
            name: 変換する文字列

        Returns:
            有効な識別子として使用できる文字列
        """
        import re

        # 無効な文字をアンダースコアに置換
        safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name)

        # 数字で始まる場合は先頭にアンダースコアを追加
        if safe_name and safe_name[0].isdigit():
            safe_name = "_" + safe_name

        # 空文字列の場合はデフォルト名を使用
        if not safe_name:
            safe_name = "unknown_field"

        # Pythonの予約語の場合は末尾にアンダースコアを追加
        python_keywords = {
            "False",
            "None",
            "True",
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
        }

        if safe_name in python_keywords:
            safe_name += "_"

        return safe_name

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
