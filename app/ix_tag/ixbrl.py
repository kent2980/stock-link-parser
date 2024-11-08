import uuid
from typing import Optional

from pydantic import Field

from .base import BaseTag


class IxNonNumeric(BaseTag):
    """非数値タグの情報を格納するクラス"""

    xbrl_id: Optional[str] = Field(default=None)
    context: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    xsi_nil: Optional[bool] = Field(default=None)
    escape: Optional[bool] = Field(default=None)
    format: Optional[str] = Field(default=None)
    value: Optional[str] = Field(default=None)
    report_type: Optional[str] = Field(default=None)
    ixbrl_role: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)
    xbrl_type: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.name and self.context and self.xbrl_id:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.name}_{self.context}_{self.xbrl_id}",
                )
            )


class IxNonFraction(BaseTag):
    """非分数タグの情報を格納するクラス"""

    xbrl_id: Optional[str] = Field(default=None)
    context: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    unit_ref: Optional[str] = Field(default=None)
    xsi_nil: Optional[bool] = Field(default=None)
    decimals: Optional[str] = Field(default=None)
    format: Optional[str] = Field(default=None)
    scale: Optional[str] = Field(default=None)
    numeric: Optional[str] = Field(default=None)
    report_type: Optional[str] = Field(default=None)
    ixbrl_role: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)
    xbrl_type: Optional[str] = Field(default=None)
    sign: Optional[str] = Field(default=None)
    display_numeric: Optional[str] = Field(default=None)
    display_scale: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.name and self.context and self.xbrl_id:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.name}_{self.context}_{self.xbrl_id}",
                )
            )


class IxHeader(BaseTag):
    """iXBRLのヘッダー情報を格納するクラス"""

    xbrl_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if (
            self.company_name
            and self.securities_code
            and self.document_name
        ):
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.company_name}_{self.securities_code}_{self.document_name}_{self.xbrl_id}",
                )
            )


class IxContext(BaseTag):
    """コンテキスト情報を格納するクラス"""

    xbrl_id: Optional[str] = Field(default=None)
    context_id: Optional[str] = Field(default=None)
    period: Optional[dict] = Field(default=None)
    scenario: Optional[list] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.context_id and self.xbrl_id:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.context_id}_{self.xbrl_id}",
                )
            )
