"""統一されたエラーハンドリングユーティリティ

各モジュールで使用できるエラーハンドリング関数とデコレーターを提供します。
"""

import functools
import logging
import traceback
from typing import Any, Callable, Optional, Type, TypeVar, Union

from .base_exception import (
    DataProcessingError,
    ErrorCode,
    ManagerInitError,
    ParserInitError,
    XBRLBaseException,
    XBRLParseError,
)

T = TypeVar("T")


def get_logger(name: str) -> logging.Logger:
    """統一されたロガーを取得する

    Args:
        name: ロガー名（通常は __name__ を使用）

    Returns:
        設定済みのロガーインスタンス
    """
    # logging_configからインポートを試みる（循環インポートを避けるため遅延インポート）
    try:
        from src.utils.logging_config import get_logger as _get_logger
        return _get_logger(name)
    except ImportError:
        # フォールバック: 基本的なロガー設定
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger


def handle_exception(
    exception: Exception,
    error_class: Type[XBRLBaseException] = XBRLParseError,
    message: Optional[str] = None,
    details: Optional[dict] = None,
    reraise: bool = True,
    logger: Optional[logging.Logger] = None,
) -> Optional[XBRLBaseException]:
    """例外を統一された形式で処理する

    Args:
        exception: 発生した例外
        error_class: 変換先の例外クラス
        message: カスタムエラーメッセージ
        details: 追加の詳細情報
        reraise: 例外を再スローするかどうか
        logger: 使用するロガー

    Returns:
        reraise=Falseの場合は変換された例外、それ以外はNone

    Raises:
        error_class: reraise=Trueの場合
    """
    if logger is None:
        logger = get_logger(__name__)

    # 詳細情報を構築
    error_details = details or {}
    error_details["original_exception"] = type(exception).__name__
    error_details["traceback"] = traceback.format_exc()

    # 新しい例外を作成
    new_exception = error_class(
        message=message or str(exception),
        details=error_details,
        cause=exception,
        log_error=True,
    )

    if reraise:
        raise new_exception from exception
    return new_exception


def safe_execute(
    func: Callable[..., T],
    *args,
    default: Optional[T] = None,
    error_class: Type[XBRLBaseException] = DataProcessingError,
    message: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    **kwargs,
) -> Optional[T]:
    """関数を安全に実行し、エラー時はデフォルト値を返す

    Args:
        func: 実行する関数
        *args: 関数の位置引数
        default: エラー時のデフォルト値
        error_class: エラー時に使用する例外クラス
        message: カスタムエラーメッセージ
        logger: 使用するロガー
        **kwargs: 関数のキーワード引数

    Returns:
        関数の戻り値、またはエラー時はdefault
    """
    if logger is None:
        logger = get_logger(__name__)

    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_details = {
            "function": func.__name__,
            "args": str(args)[:100],
            "kwargs": str(kwargs)[:100],
        }
        handle_exception(
            e,
            error_class=error_class,
            message=message or f"関数 {func.__name__} の実行に失敗しました",
            details=error_details,
            reraise=False,
            logger=logger,
        )
        return default


def error_handler(
    error_class: Type[XBRLBaseException] = XBRLParseError,
    message: Optional[str] = None,
    reraise: bool = True,
    default: Any = None,
):
    """エラーハンドリングデコレーター

    関数やメソッドに統一されたエラーハンドリングを適用します。

    Args:
        error_class: 変換先の例外クラス
        message: カスタムエラーメッセージ
        reraise: 例外を再スローするかどうか
        default: reraise=Falseの場合のデフォルト戻り値

    Returns:
        デコレートされた関数
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_logger(func.__module__)
            try:
                return func(*args, **kwargs)
            except XBRLBaseException:
                # 既にXBRLBaseExceptionの場合はそのまま再スロー
                if reraise:
                    raise
                return default
            except Exception as e:
                error_details = {
                    "function": func.__name__,
                    "module": func.__module__,
                }

                custom_message = message or f"{func.__name__} の実行中にエラーが発生しました"

                if reraise:
                    handle_exception(
                        e,
                        error_class=error_class,
                        message=custom_message,
                        details=error_details,
                        reraise=True,
                        logger=logger,
                    )
                else:
                    handle_exception(
                        e,
                        error_class=error_class,
                        message=custom_message,
                        details=error_details,
                        reraise=False,
                        logger=logger,
                    )
                    return default

        return wrapper

    return decorator


def manager_error_handler(
    manager_name: str,
    reraise: bool = False,
    default: Any = None,
):
    """マネージャー初期化用のエラーハンドリングデコレーター

    Args:
        manager_name: マネージャー名
        reraise: 例外を再スローするかどうか
        default: デフォルト戻り値

    Returns:
        デコレートされた関数
    """
    return error_handler(
        error_class=ManagerInitError,
        message=f"{manager_name}の初期化に失敗しました",
        reraise=reraise,
        default=default,
    )


def parser_error_handler(
    parser_name: str,
    reraise: bool = False,
    default: Any = None,
):
    """パーサー処理用のエラーハンドリングデコレーター

    Args:
        parser_name: パーサー名
        reraise: 例外を再スローするかどうか
        default: デフォルト戻り値

    Returns:
        デコレートされた関数
    """
    return error_handler(
        error_class=ParserInitError,
        message=f"{parser_name}の処理に失敗しました",
        reraise=reraise,
        default=default,
    )


class ErrorContext:
    """コンテキストマネージャーによるエラーハンドリング

    Usage:
        with ErrorContext("データ処理", DataProcessingError) as ctx:
            # 処理
            pass

        if ctx.error:
            print(f"エラー発生: {ctx.error}")
    """

    def __init__(
        self,
        operation_name: str,
        error_class: Type[XBRLBaseException] = XBRLParseError,
        reraise: bool = False,
        logger: Optional[logging.Logger] = None,
    ):
        self.operation_name = operation_name
        self.error_class = error_class
        self.reraise = reraise
        self.logger = logger or get_logger(__name__)
        self.error: Optional[XBRLBaseException] = None
        self.original_error: Optional[Exception] = None

    def __enter__(self) -> "ErrorContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_val is not None:
            self.original_error = exc_val
            self.error = handle_exception(
                exc_val,
                error_class=self.error_class,
                message=f"{self.operation_name}中にエラーが発生しました",
                details={"operation": self.operation_name},
                reraise=self.reraise,
                logger=self.logger,
            )
            # reraiseがFalseの場合は例外を抑制
            return not self.reraise
        return False

    @property
    def success(self) -> bool:
        """処理が成功したかどうか"""
        return self.error is None
