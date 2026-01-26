"""基底例外クラスの定義

すべてのカスタム例外クラスの基底となるクラスを定義します。
統一されたエラーハンドリングとロギングをサポートします。
"""

import logging
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    """エラーコードの定義"""

    # 一般エラー (1000番台)
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001

    # ファイル/ディレクトリエラー (2000番台)
    DIRECTORY_NOT_FOUND = 2001
    FILE_NOT_FOUND = 2002
    OUTPUT_PATH_NOT_FOUND = 2003
    INVALID_FILE_FORMAT = 2004

    # XBRLパースエラー (3000番台)
    XBRL_LIST_EMPTY = 3001
    XBRL_TYPE_INVALID = 3002
    XBRL_PARSE_ERROR = 3003
    TAG_NOT_FOUND = 3004
    DOCUMENT_NAME_NOT_FOUND = 3005

    # マネージャーエラー (4000番台)
    MANAGER_INIT_ERROR = 4001
    PARSER_INIT_ERROR = 4002
    DATA_PROCESSING_ERROR = 4003

    # APIエラー (5000番台)
    API_CONNECTION_ERROR = 5001
    API_RESPONSE_ERROR = 5002
    API_INSERTION_ERROR = 5003
    SOURCE_FILE_EXISTS = 5004

    # 設定エラー (6000番台)
    LANGUAGE_SETTING_ERROR = 6001
    CONFIG_ERROR = 6002


class XBRLBaseException(Exception):
    """XBRLプロジェクトの基底例外クラス

    すべてのカスタム例外はこのクラスを継承します。
    統一されたエラーメッセージ形式とロギング機能を提供します。
    """

    default_error_code = ErrorCode.UNKNOWN_ERROR
    default_message = "不明なエラーが発生しました"

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        log_error: bool = True,
    ):
        """
        Args:
            message: エラーメッセージ
            error_code: エラーコード
            details: 追加の詳細情報（デバッグ用）
            cause: 原因となった例外
            log_error: 自動的にログに記録するかどうか
        """
        self.message = message or self.default_message
        self.error_code = error_code or self.default_error_code
        self.details = details or {}
        self.cause = cause

        # 完全なエラーメッセージを構築
        full_message = self._build_message()
        super().__init__(full_message)

        # 自動ロギング
        if log_error:
            self._log_error()

    def _build_message(self) -> str:
        """エラーメッセージを構築する"""
        parts = [
            f"[{self.error_code.name}:{self.error_code.value}]",
            self.message,
        ]

        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            parts.append(f"[詳細: {details_str}]")

        if self.cause:
            parts.append(f"[原因: {type(self.cause).__name__}: {self.cause}]")

        return " ".join(parts)

    def _log_error(self) -> None:
        """エラーをログに記録する"""
        logger = logging.getLogger(self.__class__.__module__)
        logger.error(str(self), exc_info=self.cause is not None)

    def to_dict(self) -> Dict[str, Any]:
        """エラー情報を辞書形式で返す"""
        return {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        return self._build_message()


# =============================================================================
# ファイル/ディレクトリ関連の例外
# =============================================================================


class DirectoryNotFoundError(XBRLBaseException):
    """ディレクトリが見つからない場合の例外"""

    default_error_code = ErrorCode.DIRECTORY_NOT_FOUND
    default_message = "ディレクトリが見つかりません"


class FileNotFoundError(XBRLBaseException):
    """ファイルが見つからない場合の例外"""

    default_error_code = ErrorCode.FILE_NOT_FOUND
    default_message = "ファイルが見つかりません"


class OutputPathNotFoundError(XBRLBaseException):
    """出力先パスが見つからない場合の例外"""

    default_error_code = ErrorCode.OUTPUT_PATH_NOT_FOUND
    default_message = "出力先のパスが見つかりません"


class InvalidFileFormatError(XBRLBaseException):
    """ファイル形式が不正な場合の例外"""

    default_error_code = ErrorCode.INVALID_FILE_FORMAT
    default_message = "ファイル形式が不正です"


# =============================================================================
# XBRL解析関連の例外
# =============================================================================


class XBRLListEmptyError(XBRLBaseException):
    """XBRLリストが空の場合の例外"""

    default_error_code = ErrorCode.XBRL_LIST_EMPTY
    default_message = "XBRLのリストが空です"


class XBRLTypeInvalidError(XBRLBaseException):
    """XBRLの種類が不正な場合の例外"""

    default_error_code = ErrorCode.XBRL_TYPE_INVALID
    default_message = "XBRLファイルの種類が不正です"


class XBRLParseError(XBRLBaseException):
    """XBRL解析エラー"""

    default_error_code = ErrorCode.XBRL_PARSE_ERROR
    default_message = "XBRLの解析に失敗しました"


class TagNotFoundError(XBRLBaseException):
    """タグが見つからない場合の例外"""

    default_error_code = ErrorCode.TAG_NOT_FOUND
    default_message = "タグが見つかりません"


class DocumentNameNotFoundError(XBRLBaseException):
    """書類名タグが見つからない場合の例外"""

    default_error_code = ErrorCode.DOCUMENT_NAME_NOT_FOUND
    default_message = "書類名タグが見つかりません"


# =============================================================================
# マネージャー関連の例外
# =============================================================================


class ManagerInitError(XBRLBaseException):
    """マネージャー初期化エラー"""

    default_error_code = ErrorCode.MANAGER_INIT_ERROR
    default_message = "マネージャーの初期化に失敗しました"


class ParserInitError(XBRLBaseException):
    """パーサー初期化エラー"""

    default_error_code = ErrorCode.PARSER_INIT_ERROR
    default_message = "パーサーの初期化に失敗しました"


class DataProcessingError(XBRLBaseException):
    """データ処理エラー"""

    default_error_code = ErrorCode.DATA_PROCESSING_ERROR
    default_message = "データの処理に失敗しました"


# =============================================================================
# API関連の例外
# =============================================================================


class APIConnectionError(XBRLBaseException):
    """API接続エラー"""

    default_error_code = ErrorCode.API_CONNECTION_ERROR
    default_message = "APIへの接続に失敗しました"


class APIResponseError(XBRLBaseException):
    """APIレスポンスエラー"""

    default_error_code = ErrorCode.API_RESPONSE_ERROR
    default_message = "APIからのレスポンスが不正です"


class APIInsertionError(XBRLBaseException):
    """APIデータ挿入エラー"""

    default_error_code = ErrorCode.API_INSERTION_ERROR
    default_message = "APIへのデータ挿入に失敗しました"


class SourceFileExistsError(XBRLBaseException):
    """既存ソースファイルエラー"""

    default_error_code = ErrorCode.SOURCE_FILE_EXISTS
    default_message = "既に存在するsource_file_idがあります"


# =============================================================================
# 設定関連の例外
# =============================================================================


class LanguageSettingError(XBRLBaseException):
    """言語設定エラー"""

    default_error_code = ErrorCode.LANGUAGE_SETTING_ERROR
    default_message = "言語の設定が不正です"


class ConfigError(XBRLBaseException):
    """設定エラー"""

    default_error_code = ErrorCode.CONFIG_ERROR
    default_message = "設定が不正です"
