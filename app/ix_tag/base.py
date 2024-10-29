import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseTag(BaseModel):
    """Base class for tags"""

    id: str = Field(
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

    name: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    xbrl_id: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)

    def __str__(self) -> str:
        return f"{self.name},{self.type},{self.xbrl_id},{self.url}"


class FilePath(BaseTag):
    """ファイルパス情報を格納するクラス"""

    xbrl_id: Optional[str] = Field(
        default=None, max_length=36, min_length=36
    )
    path: Optional[str] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        if self.xbrl_id and self.path:
            self.id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{self.xbrl_id}_{self.path}",
                )
            )
