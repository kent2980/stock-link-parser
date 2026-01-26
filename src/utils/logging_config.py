"""統一されたログ設定モジュール

プロジェクト全体で一貫したロギング設定を提供します。
"""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# ログレベルの定義
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# デフォルト設定
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5


class LoggerFactory:
    """統一されたロガーファクトリー

    プロジェクト全体で一貫したロギング設定を提供します。
    """

    _initialized = False
    _log_dir: Optional[Path] = None
    _log_level = DEFAULT_LOG_LEVEL

    @classmethod
    def initialize(
        cls,
        log_dir: Optional[str] = None,
        log_level: str = "INFO",
        log_to_console: bool = True,
        log_to_file: bool = True,
    ) -> None:
        """ロギングシステムを初期化する

        Args:
            log_dir: ログファイルの出力ディレクトリ
            log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
            log_to_console: コンソールへの出力を有効にするか
            log_to_file: ファイルへの出力を有効にするか
        """
        if cls._initialized:
            return

        cls._log_level = LOG_LEVELS.get(log_level.upper(), DEFAULT_LOG_LEVEL)

        # ログディレクトリの設定
        if log_dir:
            cls._log_dir = Path(log_dir)
        else:
            # デフォルトはプロジェクトルートのlogsディレクトリ
            cls._log_dir = Path(__file__).parent.parent.parent / "logs"

        cls._log_dir.mkdir(exist_ok=True)

        # ルートロガーの設定
        root_logger = logging.getLogger()
        root_logger.setLevel(cls._log_level)

        # 既存のハンドラーをクリア
        root_logger.handlers.clear()

        # フォーマッターの作成
        formatter = logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT,
        )

        # コンソールハンドラーの追加
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(cls._log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # ファイルハンドラーの追加
        if log_to_file and cls._log_dir:
            # 日付ベースのログファイル
            log_filename = f"xbrl_{datetime.now().strftime('%Y%m%d')}.log"
            log_file = cls._log_dir / log_filename

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=DEFAULT_MAX_BYTES,
                backupCount=DEFAULT_BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(cls._log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            # エラー専用のログファイル
            error_log_filename = f"xbrl_errors_{datetime.now().strftime('%Y%m%d')}.log"
            error_log_file = cls._log_dir / error_log_filename

            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=DEFAULT_MAX_BYTES,
                backupCount=DEFAULT_BACKUP_COUNT,
                encoding="utf-8",
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """名前付きロガーを取得する

        Args:
            name: ロガー名（通常は __name__ を使用）

        Returns:
            設定済みのロガーインスタンス
        """
        # まだ初期化されていない場合はデフォルト設定で初期化
        if not cls._initialized:
            cls.initialize(log_to_file=False)

        return logging.getLogger(name)

    @classmethod
    def set_level(cls, level: str) -> None:
        """ログレベルを動的に変更する

        Args:
            level: 新しいログレベル
        """
        new_level = LOG_LEVELS.get(level.upper(), DEFAULT_LOG_LEVEL)
        cls._log_level = new_level

        root_logger = logging.getLogger()
        root_logger.setLevel(new_level)

        for handler in root_logger.handlers:
            if not isinstance(handler, RotatingFileHandler) or handler.level != logging.ERROR:
                handler.setLevel(new_level)

    @classmethod
    def get_log_dir(cls) -> Optional[Path]:
        """ログディレクトリのパスを取得する"""
        return cls._log_dir


def get_logger(name: str) -> logging.Logger:
    """簡易的なロガー取得関数

    Args:
        name: ロガー名（通常は __name__ を使用）

    Returns:
        設定済みのロガーインスタンス
    """
    return LoggerFactory.get_logger(name)


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = True,
) -> None:
    """ロギングシステムをセットアップする

    Args:
        log_dir: ログファイルの出力ディレクトリ
        log_level: ログレベル
        log_to_console: コンソール出力を有効にするか
        log_to_file: ファイル出力を有効にするか
    """
    LoggerFactory.initialize(
        log_dir=log_dir,
        log_level=log_level,
        log_to_console=log_to_console,
        log_to_file=log_to_file,
    )


class LogMixin:
    """ログ機能を提供するMixinクラス

    クラスにログ機能を追加するために使用します。

    Usage:
        class MyClass(LogMixin):
            def my_method(self):
                self.logger.info("処理を開始します")
    """

    @property
    def logger(self) -> logging.Logger:
        """クラス用のロガーを取得する"""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__module__)
        return self._logger


# 使いやすさのためのエイリアス
debug = lambda msg, *args, **kwargs: get_logger(__name__).debug(msg, *args, **kwargs)
info = lambda msg, *args, **kwargs: get_logger(__name__).info(msg, *args, **kwargs)
warning = lambda msg, *args, **kwargs: get_logger(__name__).warning(msg, *args, **kwargs)
error = lambda msg, *args, **kwargs: get_logger(__name__).error(msg, *args, **kwargs)
critical = lambda msg, *args, **kwargs: get_logger(__name__).critical(msg, *args, **kwargs)
