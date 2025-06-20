import uuid
from typing import List, Optional

from pydantic import Field

from .base import BaseTag


class IxNonNumeric(BaseTag):
    """非数値タグの情報を格納するクラス"""

    head_item_key: Optional[str] = Field(default=None)
    context: Optional[List[str]] = Field(default=None)
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
        if self.name and self.context and self.head_item_key:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.name}_{self.context}_{self.head_item_key}_{self.value}_{self.xbrl_type}_{self.ixbrl_role}_{self.source_file_id}",
                )
            )


class IxNonFraction(BaseTag):
    """非分数タグの情報を格納するクラス"""

    head_item_key: Optional[str] = Field(default=None)
    context: Optional[List[str]] = Field(default=None)
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
        if self.name and self.context and self.head_item_key:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.name}_{self.context}_{self.head_item_key}_{self.numeric}_{self.xbrl_type}_{self.ixbrl_role}_{self.source_file_id}",
                )
            )


class IxHeader(BaseTag):
    """iXBRLのヘッダー情報を格納するクラス"""

    item_key: Optional[str] = Field(default=None)
    company_name: Optional[str] = Field(default=None)
    securities_code: Optional[str] = Field(default=None)
    document_name: Optional[str] = Field(default=None)
    reporting_date: Optional[str] = Field(default=None)
    current_period: Optional[str] = Field(default=None)
    report_type: Optional[str] = Field(default=None)
    listed_market: Optional[str] = Field(default=None)
    market_section: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    is_bs: Optional[bool] = Field(default=None)
    is_pl: Optional[bool] = Field(default=None)
    is_cf: Optional[bool] = Field(default=None)
    is_ci: Optional[bool] = Field(default=None)
    is_sce: Optional[bool] = Field(default=None)
    is_sfp: Optional[bool] = Field(default=None)
    fy_year_end: Optional[str] = Field(default=None)
    tel: Optional[str] = Field(default=None)
    specific_business: Optional[bool] = Field(default=None)


class IxContext(BaseTag):
    """コンテキスト情報を格納するクラス"""

    head_item_key: Optional[str] = Field(default=None)
    context_id: Optional[str] = Field(default=None)
    period: Optional[dict] = Field(default=None)
    scenario: Optional[list] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.context_id and self.head_item_key:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.context_id}_{self.head_item_key}",
                )
            )
