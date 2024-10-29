import uuid
from typing import Optional

from pydantic import Field

from .base import BaseTag


class LabelValue(BaseTag):
    """ラベル情報を格納するクラス"""

    xlink_type: Optional[str] = Field(default=None)
    xlink_label: Optional[str] = Field(default=None)
    xlink_role: Optional[str] = Field(default=None)
    xml_lang: Optional[str] = Field(default=None)
    label: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_label and self.xlink_role:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_label}_{self.xlink_role}_{self.source_file_id}_{self.xlink_type}_{self.xml_lang}",
                )
            )


class LabelLoc(BaseTag):
    """loc要素情報を格納するクラス"""

    xlink_type: Optional[str] = Field(default=None)
    xlink_label: Optional[str] = Field(default=None)
    xlink_schema: Optional[str] = Field(default=None)
    xlink_href: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_label and self.xlink_schema:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_label}_{self.xlink_schema}_{self.source_file_id}_{self.xlink_type}_{self.xlink_href}",
                )
            )


class LabelArc(BaseTag):
    """arc要素情報を格納するクラス"""

    xlink_type: Optional[str] = Field(default=None)
    xlink_from: Optional[str] = Field(default=None)
    xlink_to: Optional[str] = Field(default=None)
    xlink_arcrole: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_from and self.xlink_to:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_from}_{self.xlink_to}_{self.source_file_id}_{self.xlink_type}_{self.xlink_arcrole}",
                )
            )


class LabelRoleRefs(BaseTag):
    """roleRef要素情報を格納するクラス"""

    role_uri: Optional[str] = Field(default=None)
    xlink_type: Optional[str] = Field(default=None)
    xlink_schema: Optional[str] = Field(default=None)
    xlink_href: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.role_uri and self.xlink_schema:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.role_uri}_{self.xlink_schema}_{self.xlink_type}_{self.xlink_href}",
                )
            )
