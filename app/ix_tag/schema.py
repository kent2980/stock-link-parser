import uuid
from typing import Optional

from pydantic import Field

from .base import BaseTag


class SchemaImport(BaseTag):
    """Schema Import Dataclass"""

    schema_location: Optional[str] = Field(default=None)
    name_space: Optional[str] = Field(default=None)
    xbrl_type: Optional[str] = Field(default=None)
    xbrl_id: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.schema_location and self.name_space:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.schema_location}_{self.name_space}_{self.xbrl_type}_{self.xbrl_id}",
                )
            )


class SchemaLinkBaseRef(BaseTag):
    """Schema Link Base Ref Dataclass"""

    xlink_type: Optional[str] = Field(default=None)
    xlink_href: Optional[str] = Field(default=None)
    xlink_role: Optional[str] = Field(default=None)
    xlink_arcrole: Optional[str] = Field(default=None)
    xbrl_type: Optional[str] = Field(default=None)
    xbrl_id: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)
    href_source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xlink_href and self.xlink_role:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xlink_href}_{self.xlink_role}_{self.xbrl_type}_{self.xbrl_id}",
                )
            )


class SchemaElement(BaseTag):
    """Schema Element Dataclass"""

    id: Optional[str] = Field(default=None)
    xbrli_balance: Optional[str] = Field(default=None)
    xbrli_period_type: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    nillable: Optional[str] = Field(default=None)
    substitution_group: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    xbrl_type: Optional[str] = Field(default=None)
    xbrl_id: Optional[str] = Field(default=None)
    source_file_id: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.name and self.xbrl_id:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.name}_{self.xbrl_id}",
                )
            )
