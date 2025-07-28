from typing import List, Optional

from app.ix_manager import BaseXbrlManager
from app.ix_parser import BaseLinkParser, CalLinkParser, DefLinkParser, PreLinkParser
from app.ix_tag.link import LinkArc, LinkHrefMaster, LinkLoc, LinkRole


class BaseLinkManager(BaseXbrlManager[BaseLinkParser]):
    """labelLinkbaseデータの解析を行うクラス"""

    def __init__(
        self,
        directory_path,
        output_path,
        document_type=None,
        head_item_key: Optional[str] = None,
        class_name: Optional[str] = None,
    ):
        super().__init__(directory_path, head_item_key=head_item_key)

        # プロパティの初期化
        self.__output_path = output_path
        self.__document_type = document_type
        self.__role = None
        self.__link_roles = None
        self.__link_locs = None
        self.__link_arcs = None
        self.__class_name = class_name
        self.__href_master = None

    @property
    def document_type(self):
        return self.__document_type

    @property
    def output_path(self):
        return self.__output_path

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, role):
        self.__role = role

    @property
    def link_roles(self) -> List[List[LinkRole]] | None:
        return self.__link_roles

    @property
    def link_locs(self) -> List[List[LinkLoc]] | None:
        return self.__link_locs

    @property
    def link_arcs(self) -> List[List[LinkArc]] | None:
        return self.__link_arcs

    @property
    def class_name(self):
        return self.__class_name

    @property
    def href_master(self) -> List[LinkHrefMaster] | None:
        return self.__href_master

    def _init_parser(self):
        """パーサーを設定します。"""
        parsers: List[BaseLinkParser] = []
        for _, row in self.related_files.iterrows():
            parser = self.parser(
                row["xlink_href"],
                self.output_path,
                head_item_key=self.head_item_key,
            )
            parsers.append(parser)

        self.parsers = parsers

    def _init_manager(self):
        self.set_source_file(self.parsers, class_name=self.class_name)
        self.__set_link_roles()
        self.__set_link_locs()
        self.__set_link_arcs()
        self.__set_href_master()

    def __set_link_roles(self):
        """link_rolesを設定します。"""
        if self.__link_roles:
            return self.__link_roles

        rows = []

        files = self.related_files
        if self.document_type is not None:
            files = files.query(f"document_type == '{self.document_type}'")
        for parser in self.parsers:

            id = parser.source_file_id

            parser = parser.link_roles()

            data = parser.data

            rows.append(data)

            self._set_items(id=id, key=f"{self.class_name}_link_roles", items=data)

        self.__link_roles = rows

    def __set_link_locs(self):
        """link_locsを設定します。"""

        if self.__link_locs:
            return self.__link_locs

        rows = []

        files = self.related_files
        if self.document_type is not None:
            files = files.query(f"document_type == '{self.document_type}'")
        for parser in self.parsers:

            id = parser.source_file_id

            parser = parser.link_locs()

            data = parser.data

            rows.append(data)

            self._set_items(id=id, key=f"{self.class_name}_link_locs", items=data)

        self.__link_locs = rows

    def __set_link_arcs(self):
        """link_arcsを設定します。"""
        if self.__link_arcs:
            return self.__link_arcs

        rows = []

        files = self.related_files
        if self.document_type is not None:
            files = files.query(f"document_type == '{self.document_type}'")
        for parser in self.parsers:

            id = parser.source_file_id

            parser = parser.link_arcs()

            data = parser.data

            rows.append(data)

            self._set_items(id=id, key=f"{self.class_name}_link_arcs", items=data)

        self.__link_arcs = rows

    def __set_href_master(self):
        """href_masterを設定します。"""

        # 既にhref_masterが設定されている場合は何もしない
        if self.__href_master:
            return self.__href_master

        link_locs = self.link_locs

        rows = []
        for items in link_locs:
            for item in items:
                is_calc = False
                is_def = False
                is_pre = False
                if self.class_name == "cal":
                    is_calc = True
                elif self.class_name == "def":
                    is_def = True
                elif self.class_name == "pre":
                    is_pre = True
                rows.append(
                    LinkHrefMaster(
                        head_item_key=self.head_item_key,
                        xlink_href=item.xlink_href,
                        attr_value=item.attr_value,
                        source_file_id=item.source_file_id,
                        is_calc=is_calc,
                        is_def=is_def,
                        is_pre=is_pre,
                    )
                )

        self.__href_master = rows


class CalLinkManager(BaseLinkManager):
    """calculationLinkbaseデータの解析を行うクラス

    raise   - NotImplementedError: [description]
            - XbrlListEmptyError: [description]
    """

    def __init__(
        self,
        directory_path,
        output_path,
        document_type=None,
        head_item_key: Optional[str] = None,
    ):
        super().__init__(
            directory_path,
            output_path,
            document_type,
            head_item_key=head_item_key,
            class_name="cal",
        )
        self.role = "calculationLinkbaseRef"
        self.parser = CalLinkParser

        # 初期化メソッドを実行
        self._set_linkbase_files(self.role)
        self._init_parser()
        self._init_manager()
        self._set_source_file_ids()


class DefLinkManager(BaseLinkManager):
    """definitionLinkbaseデータの解析を行うクラス

    raise   - NotImplementedError: [description]
            - XbrlListEmptyError: [description]
    """

    def __init__(
        self,
        directory_path,
        output_path,
        document_type=None,
        head_item_key: Optional[str] = None,
    ):
        super().__init__(
            directory_path,
            output_path,
            document_type,
            head_item_key=head_item_key,
            class_name="def",
        )
        self.role = "definitionLinkbaseRef"
        self.parser = DefLinkParser

        # 初期化メソッドを実行
        self._set_linkbase_files(self.role)
        self._init_parser()
        self._init_manager()
        self._set_source_file_ids()


class PreLinkManager(BaseLinkManager):
    """presentationLinkbaseデータの解析を行うクラス

    raise   - NotImplementedError: [description]
            - XbrlListEmptyError: [description]
    """

    def __init__(
        self,
        directory_path,
        output_path,
        document_type=None,
        head_item_key: Optional[str] = None,
    ):
        super().__init__(
            directory_path,
            output_path,
            document_type,
            head_item_key=head_item_key,
            class_name="pre",
        )
        self.role = "presentationLinkbaseRef"
        self.parser = PreLinkParser

        # 初期化メソッドを実行
        self._set_linkbase_files(self.role)
        self._init_parser()
        self._init_manager()
        self._set_source_file_ids()
