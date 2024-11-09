import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseTag(BaseModel):
    """Base class for tags"""

    item_key: str = Field(
        default=None, min_length=36, max_length=36
    )  # uuidを設定

    @classmethod
    def keys(cls):
        return list(cls().__dict__.keys())

    @classmethod
    def is_valid(cls, data: dict):
        # インスタンス化
        try:
            cls(**data)
            return True
        except TypeError:
            return False

    def __eq__(self, value: object) -> bool:
        return self.__dict__ == value.__dict__

    model_config = ConfigDict(coerce_numbers_to_str=True)


class SourceFile(BaseTag):
    """ソースファイル情報を格納するクラス"""

    id: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    head_item_key: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)

    def __str__(self) -> str:
        return f"{self.name},{self.type},{self.head_item_key},{self.url}"

    def __init__(self, **data):
        super().__init__(**data)
        key = None
        if self.head_item_key:
            key = self.head_item_key
        elif self.url:
            key = self.url
        if key:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.name}_{key}",
                )
            )


class FilePath(BaseTag):
    """ファイルパス情報を格納するクラス"""

    head_item_key: Optional[str] = Field(
        default=None, max_length=36, min_length=36
    )
    path: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.head_item_key and self.path:
            self.item_key = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.head_item_key}_{self.path}",
                )
            )
