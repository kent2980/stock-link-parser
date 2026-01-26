"""例外クラスのエクスポート

新しい基底例外クラスと、レガシー互換の例外クラスを提供します。
新規コードでは base_exception モジュールのクラスを使用してください。
"""

# 新しい統一例外クラス（推奨）
from .base_exception import (
    APIConnectionError,
    APIInsertionError,
    APIResponseError,
    ConfigError,
    DataProcessingError,
    DirectoryNotFoundError,
    DocumentNameNotFoundError,
    ErrorCode,
    InvalidFileFormatError,
    LanguageSettingError,
    ManagerInitError,
    OutputPathNotFoundError,
    ParserInitError,
    SourceFileExistsError,
    TagNotFoundError,
    XBRLBaseException,
    XBRLListEmptyError,
    XBRLParseError,
    XBRLTypeInvalidError,
)

# レガシー互換クラス（既存コードとの互換性のため維持）
from .xbrl_manager_exception import (
    OutputPathNotFoundError as LegacyOutputPathNotFoundError,
)
from .xbrl_manager_exception import SetLanguageNotError
from .xbrl_manager_exception import (
    XbrlDirectoryNotFoundError,
    XbrlListEmptyError,
)
from .xbrl_model_exception import NotXbrlDirectoryException, NotXbrlTypeException
from .xbrl_parser_exception import AlreadyExistSourceFileIdError
from .xbrl_parser_exception import (
    DocumentNameTagNotFoundError,
    TagNotFoundError as LegacyTagNotFoundError,
)
from .xbrl_parser_exception import TypeOfXBRLIsDifferent

__all__ = [
    # 新しい統一例外クラス（推奨）
    "XBRLBaseException",
    "ErrorCode",
    "DirectoryNotFoundError",
    "OutputPathNotFoundError",
    "InvalidFileFormatError",
    "XBRLListEmptyError",
    "XBRLTypeInvalidError",
    "XBRLParseError",
    "TagNotFoundError",
    "DocumentNameNotFoundError",
    "ManagerInitError",
    "ParserInitError",
    "DataProcessingError",
    "APIConnectionError",
    "APIResponseError",
    "APIInsertionError",
    "SourceFileExistsError",
    "LanguageSettingError",
    "ConfigError",
    # レガシー互換クラス
    "XbrlListEmptyError",
    "XbrlDirectoryNotFoundError",
    "LegacyOutputPathNotFoundError",
    "SetLanguageNotError",
    "NotXbrlDirectoryException",
    "NotXbrlTypeException",
    "LegacyTagNotFoundError",
    "TypeOfXBRLIsDifferent",
    "DocumentNameTagNotFoundError",
    "AlreadyExistSourceFileIdError",
]
