from pathlib import Path
from typing import Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

import pandas as pd
from pandas import DataFrame

from app.exception import XbrlDirectoryNotFoundError, XbrlListEmptyError
from app.ix_parser import BaseXBRLParser, SchemaParser
from app.ix_tag.base import BaseTag
from app.utils import Utils

T = TypeVar("T", bound=BaseXBRLParser)

# XBRLアイテムの値として許可される型
XBRLValue = Union[
    str,
    int,
    float,
    bool,
    None,
    List[str],
    Dict[str, Union[str, int, float, bool, None]],
]


class ItemDict:
    id: str
    key: str
    item: List[Dict[str, XBRLValue]]
    sort_position: int


class BaseXbrlManager(Generic[T]):
    """XBRLディレクトリの解析を行う基底クラス"""

    def __init__(
        self, directory_path: str, head_item_key: Optional[str] = None
    ) -> None:
        self.__directory_path = Path(directory_path)
        self.__files = self._to_filelist()
        self.__related_files: Optional[DataFrame] = None
        self.__items: List[ItemDict] = []
        self.__head_item_key = head_item_key if head_item_key else str(uuid4())
        self.__parsers = None
        self.__source_file_id_list = None
        self.__xbrl_type = None

    @property
    def files(self) -> List[str]:
        return self.__files

    @property
    def related_files(self) -> Optional[DataFrame]:
        return self.__related_files

    @related_files.setter
    def related_files(self, related_files: DataFrame) -> None:
        self.__related_files = related_files

    @property
    def items(self) -> List[ItemDict]:
        """アイテムのリストを取得します。"""
        return self.__items

    @property
    def head_item_key(self) -> str:
        return self.__head_item_key

    @head_item_key.setter
    def head_item_key(self, head_item_key: str) -> None:
        self.__head_item_key = head_item_key

    @property
    def parsers(self) -> Optional[List[T]]:
        """パーサーのリストを取得します。"""
        return self.__parsers

    @parsers.setter
    def parsers(self, parsers: List[T]) -> None:
        self.__parsers = parsers

    @property
    def xbrl_type(self) -> Optional[str]:
        """XBRLの種類を取得します。"""
        if self.__xbrl_type is None:
            self.__xbrl_type = self._get_xbrl_type()
        return self.__xbrl_type

    def _set_items(
        self,
        id: str,
        key: str,
        items: List[Union[Dict[str, XBRLValue], BaseTag]],
        sort_position: int = 999,
    ) -> None:
        """アイテムを設定する"""

        # itemsをList[dict]型に変換する
        items_dicts: List[Dict[str, XBRLValue]] = []
        for item in items:
            if isinstance(item, dict):
                items_dicts.append(item)
            elif isinstance(item, BaseTag):
                items_dict = item.__dict__
                items_dicts.append(items_dict)
            else:
                raise TypeError(f"Unsupported item type: {type(item)}")

        # itemを辞書型に変換する
        item_dict = ItemDict()
        item_dict.id = id
        item_dict.key = key
        item_dict.item = items_dicts
        item_dict.sort_position = sort_position

        # itemsにデータを追加する
        self.__items.append(item_dict)

    @property
    def directory_path(self) -> Path:
        return self.__directory_path

    @directory_path.setter
    def directory_path(self, directory_path: str) -> None:
        directory_path_obj = Path(directory_path)
        if not directory_path_obj.exists():
            raise XbrlDirectoryNotFoundError(f"無効なパス[{directory_path_obj}]")
        self.__directory_path = directory_path_obj

    @property
    def source_file_id_list(self) -> Optional[List[str]]:
        return self.__source_file_id_list

    def _to_filelist(self) -> List[str]:
        """ディレクトリ内のファイル一覧を取得する"""
        return [
            file.as_posix()
            for file in self.directory_path.glob("**/*")
            if file.is_file() and not file.name.startswith(".")
        ]

    def _get_xbrl_type(self) -> Optional[str]:
        """書類品種を取得します"""
        files = self.files
        for file_str in files:
            file = Path(file_str)
            if file.suffix == ".xsd" and "fr" not in file.name:
                type_str = file.name.split("-")[1]
                code = type_str[:4] if len(type_str) == 4 else type_str[2:6]
                type_dict = Utils.read_const_json()["report"]
                if code in type_dict:
                    type_value = type_dict[code]
                    if isinstance(type_value, str):
                        return type_value
                    else:
                        raise ValueError(
                            f"Invalid type: {type_value} in file {file_str}"
                        )
        return None

    def _set_linkbase_files(
        self, xlink_role: Optional[str] = None
    ) -> "BaseXbrlManager":
        """関係ファイルのリストを取得する"""
        files = self.files
        xsd_files = [file for file in files if Path(file).suffix == ".xsd"]

        data_frames = [
            SchemaParser(file).link_base_refs().to_DataFrame() for file in xsd_files
        ]

        df = pd.concat(data_frames, ignore_index=True)

        href_map = {
            row["xlink_href"]: file
            for file in files
            for index, row in df.iterrows()
            if not row["xlink_href"].startswith("http") and row["xlink_href"] in file
        }

        df["xlink_href"] = (
            df["xlink_href"].astype(str).apply(lambda href: href_map.get(href, href))
        )

        # dfのxlink_roleカラムを整形
        df["xlink_role"] = df["xlink_role"].apply(
            lambda role: (role.split("/")[-1] if isinstance(role, str) else role)
        )
        # dfのxlink_arcroleカラムを整形
        df["xlink_arcrole"] = df["xlink_arcrole"].apply(
            lambda arcrole: (
                arcrole.split("/")[-1] if isinstance(arcrole, str) else arcrole
            )
        )

        if xlink_role:
            query = f"xlink_role == '{xlink_role}'"
            df = df.query(query)

        # ファイルが見つからない場合はエラーを発生させる
        if len(df) == 0 and xlink_role:
            raise XbrlListEmptyError(f"{xlink_role}ファイルが見つかりません。")

        self.related_files = df
        return self

    def _set_htmlbase_files(
        self, xlink_role: Optional[str] = None
    ) -> "BaseXbrlManager":
        """HTMLベースのファイルリストを取得する"""
        lists: List[Dict[str, str]] = []
        files = self.files
        for file_str in files:
            file = Path(file_str)
            if file.suffix == ".htm" or file.suffix == ".html":
                document_type = (
                    file.name.split("-")[1][2:4] if "fr" in file.name else "sm"
                )

                href = file.as_posix()
                role = file.name.split("-")[-1].split(".")[0]

                lists.append(
                    {
                        "xlink_type": "simple",
                        "xlink_href": href,
                        "xlink_role": role,
                        "xlink_arcrole": "htmlbase",
                        "document_type": document_type,
                    }
                )

        df = pd.DataFrame(lists)

        if xlink_role:
            query = f"xlink_role == '{xlink_role}'"
            df = df.query(query)

        # ファイルが見つからない場合はエラーを発生させる
        if len(df) == 0 and xlink_role:
            raise XbrlListEmptyError(f"{xlink_role}ファイルが見つかりません。")

        self.related_files = df

        return self

    def set_source_file(
        self,
        parsers: List[BaseXBRLParser],
        class_name: Optional[str] = None,
    ) -> None:
        """ソースファイルを設定する"""
        for parser in parsers:
            id = parser.source_file_id
            sources = parser.source_file
            self._set_items(
                id=id,
                key=f"{class_name}_source_file",
                items=[sources],
                sort_position=1,
            )

    def _set_source_file_ids(self) -> None:
        """ソースファイルIDのリストを取得する"""

        # parsersがNoneの場合はエラーを発生させる
        if self.parsers is None:
            raise Exception("parserが初期化されていません。")

        sf_ids = [parser.source_file_id for parser in self.parsers]

        self.__source_file_id_list = sf_ids
