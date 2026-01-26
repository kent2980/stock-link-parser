"""アプリケーション設定モジュール

環境変数と.envファイルから設定を読み込み、
アプリケーション全体で使用できる設定を提供します。
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    """プロジェクトルートディレクトリを取得する"""
    current_file = Path(__file__)
    # src/config/settings.py から2階層上がプロジェクトルート
    return current_file.parent.parent.parent


class AppSettings(BaseSettings):
    """アプリケーション全体の設定

    環境変数または.envファイルから設定を読み込みます。
    環境変数名はXBRL_で始まるものを使用します。
    """

    model_config = SettingsConfigDict(
        env_prefix="XBRL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==========================================================================
    # 基本設定
    # ==========================================================================

    # 環境（development, staging, production）
    environment: str = Field(default="development", description="実行環境")

    # デバッグモード
    debug: bool = Field(default=False, description="デバッグモードの有効/無効")

    # ==========================================================================
    # パス設定
    # ==========================================================================

    # プロジェクトルート（自動検出）
    project_root: Path = Field(
        default_factory=get_project_root, description="プロジェクトルートディレクトリ"
    )

    # 出力ディレクトリ
    output_path: Optional[str] = Field(
        default=None, description="XBRL処理結果の出力ディレクトリ"
    )

    # XBRLファイルのディレクトリ
    xbrl_data_path: Optional[str] = Field(
        default=None, description="XBRLファイルが格納されているディレクトリ"
    )

    # ログディレクトリ
    log_dir: Optional[str] = Field(default=None, description="ログファイルの出力ディレクトリ")

    # ロックファイルパス
    lock_file_path: Optional[str] = Field(default=None, description="ロックファイルのパス")

    # ==========================================================================
    # API設定
    # ==========================================================================

    # APIのベースURL
    api_base_url: str = Field(
        default="https://api.fs-stock.net", description="APIのベースURL"
    )

    # APIタイムアウト（秒）
    api_timeout: int = Field(default=30, description="APIリクエストのタイムアウト秒数")

    # APIリトライ回数
    api_retry_count: int = Field(default=3, description="APIリクエストのリトライ回数")

    # ==========================================================================
    # ログ設定
    # ==========================================================================

    # ログレベル
    log_level: str = Field(default="INFO", description="ログレベル")

    # コンソールへのログ出力
    log_to_console: bool = Field(default=True, description="コンソールへのログ出力")

    # ファイルへのログ出力
    log_to_file: bool = Field(default=True, description="ファイルへのログ出力")

    # ==========================================================================
    # 処理設定
    # ==========================================================================

    # 並列処理のワーカー数
    max_workers: int = Field(default=4, description="並列処理の最大ワーカー数")

    # バッチサイズ
    batch_size: int = Field(default=100, description="バッチ処理のサイズ")

    # ==========================================================================
    # JPX（日本取引所グループ）設定
    # ==========================================================================

    # 東証上場銘柄一覧のExcelファイルURL
    # 環境変数名は TSE_STOCK_LIST_URL または XBRL_TSE_STOCK_LIST_URL の両方に対応
    tse_stock_list_url: str = Field(
        default="https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls",
        description="東証上場銘柄一覧のExcelファイルURL",
        validation_alias=AliasChoices("TSE_STOCK_LIST_URL", "XBRL_TSE_STOCK_LIST_URL"),
    )

    # ==========================================================================
    # 計算プロパティ
    # ==========================================================================

    @property
    def resolved_output_path(self) -> Path:
        """出力パスを解決する"""
        if self.output_path:
            return Path(self.output_path)
        return self.project_root / "output"

    @property
    def resolved_log_dir(self) -> Path:
        """ログディレクトリを解決する"""
        if self.log_dir:
            return Path(self.log_dir)
        return self.project_root / "logs"

    @property
    def resolved_lock_file_path(self) -> Path:
        """ロックファイルパスを解決する"""
        if self.lock_file_path:
            return Path(self.lock_file_path)
        return self.project_root / "script.lock"

    def ensure_directories(self) -> None:
        """必要なディレクトリを作成する"""
        self.resolved_output_path.mkdir(parents=True, exist_ok=True)
        self.resolved_log_dir.mkdir(parents=True, exist_ok=True)


class DatabaseSettings(BaseSettings):
    """データベース設定"""

    model_config = SettingsConfigDict(
        env_prefix="XBRL_DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # データベースホスト
    host: str = Field(default="localhost", description="データベースホスト")

    # データベースポート
    port: int = Field(default=5432, description="データベースポート")

    # データベース名
    database: str = Field(default="xbrl", description="データベース名")

    # ユーザー名
    username: str = Field(default="", description="データベースユーザー名")

    # パスワード
    password: str = Field(default="", description="データベースパスワード")

    @property
    def connection_string(self) -> str:
        """接続文字列を生成する"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@lru_cache()
def get_settings() -> AppSettings:
    """アプリケーション設定を取得する（キャッシュ付き）

    Returns:
        AppSettings インスタンス
    """
    return AppSettings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """データベース設定を取得する（キャッシュ付き）

    Returns:
        DatabaseSettings インスタンス
    """
    return DatabaseSettings()


# 便利なエイリアス
settings = get_settings()
db_settings = get_database_settings()
