import uuid
from typing import Optional

from pydantic import Field

from .base import BaseTag


class LinkSchemaImport(BaseTag):
    """
    リンクスキーマのインポートを表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    schema_location: Optional[str] = Field(default=None)
    name_space: Optional[str] = Field(default=None)
    document_type: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.schema_location and self.name_space:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.schema_location}_{self.name_space}_{self.document_type}_{self.xbrl_id}",
                )
            )


class LinkBaseRef(BaseTag):
    """
    リンクベースの参照を表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    xlink_type: Optional[str] = Field(default=None)
    xlink_href: Optional[str] = Field(default=None)
    xlink_role: Optional[str] = Field(default=None)
    xlink_arcrole: Optional[str] = Field(default=None)
    document_type: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_href and self.xlink_role:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_href}_{self.xlink_role}_{self.document_type}_{self.xbrl_id}",
                )
            )


class LinkElement(BaseTag):
    """
    リンク要素を表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None)
    xbrli_balance: Optional[str] = Field(default=None)
    xbrli_period_type: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    nillable: Optional[str] = Field(default=None)
    substitution_group: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    document_type: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.name and self.type:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.name}_{self.type}_{self.document_type}_{self.xbrl_id}",
                )
            )


class LinkRole(BaseTag):
    """
    リンクロールを表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    xlink_type: Optional[str] = Field(default=None)
    xlink_schema: Optional[str] = Field(default=None)
    xlink_href: Optional[str] = Field(default=None)
    role_uri: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.role_uri and self.xlink_schema:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.role_uri}_{self.xlink_schema}_{self.xlink_type}_{self.xlink_href}_{self.xbrl_id}",
                )
            )


class LinkLoc(BaseTag):
    """
    リンクロケーションを表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    attr_value: Optional[str] = Field(default=None)
    xlink_type: Optional[str] = Field(default=None)
    xlink_schema: Optional[str] = Field(default=None)
    xlink_href: Optional[str] = Field(default=None)
    xlink_label: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_label and self.xlink_schema:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_label}_{self.xlink_schema}_{self.xlink_type}_{self.xlink_href}_{self.source_file_id}",
                )
            )


class LinkArc(BaseTag):
    """
    リンクアークを表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    attr_value: Optional[str] = Field(default=None)
    xlink_type: Optional[str] = Field(default=None)
    xlink_from: Optional[str] = Field(default=None)
    xlink_to: Optional[str] = Field(default=None)
    xlink_arcrole: str = Field(default=None)
    xlink_order: Optional[float] = Field(default=None)
    xlink_weight: Optional[float] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_from and self.xlink_to:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_from}_{self.xlink_to}_{self.xlink_type}_{self.xlink_arcrole}_{self.source_file_id}",
                )
            )


class LinkBase(BaseTag):
    """
    リンクベースを表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    xmlns_xlink: Optional[str] = Field(default=None)
    xmlns_xsi: Optional[str] = Field(default=None)
    xmlns_link: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xmlns_xlink and self.xmlns_xsi:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xmlns_xlink}_{self.xmlns_xsi}_{self.xmlns_link}_{self.xbrl_id}",
                )
            )


class LinkTag(BaseTag):
    """
    リンクタグを表すデータクラスです。
    """

    xbrl_id: Optional[str] = Field(default=None)
    xlink_type: Optional[str] = Field(default=None)
    xlink_role: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_type and self.xlink_role:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_type}_{self.xlink_role}_{self.xbrl_id}",
                )
            )
