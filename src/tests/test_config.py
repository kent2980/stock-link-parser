"""設定モジュールのテスト"""

import os
from pathlib import Path
from unittest import mock

import pytest


class TestAppSettings:
    """AppSettingsのテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されることを確認"""
        # キャッシュをクリアするために新しいインスタンスを作成
        from src.config.settings import AppSettings

        settings = AppSettings()
        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.api_base_url == "https://api.fs-stock.net"
        assert settings.api_timeout == 30
        assert settings.api_retry_count == 3
        assert settings.log_level == "INFO"
        assert settings.log_to_console is True
        assert settings.log_to_file is True
        assert settings.max_workers == 4
        assert settings.batch_size == 100

    def test_env_override(self):
        """環境変数で値を上書きできることを確認"""
        from src.config.settings import AppSettings

        with mock.patch.dict(os.environ, {
            "XBRL_ENVIRONMENT": "production",
            "XBRL_DEBUG": "true",
            "XBRL_API_BASE_URL": "https://test.example.com",
            "XBRL_LOG_LEVEL": "DEBUG",
        }):
            settings = AppSettings()
            assert settings.environment == "production"
            assert settings.debug is True
            assert settings.api_base_url == "https://test.example.com"
            assert settings.log_level == "DEBUG"

    def test_resolved_output_path_default(self):
        """デフォルトの出力パスが正しく解決されることを確認"""
        from src.config.settings import AppSettings

        settings = AppSettings()
        resolved = settings.resolved_output_path
        assert resolved.name == "output"
        assert resolved.parent == settings.project_root

    def test_resolved_output_path_custom(self):
        """カスタム出力パスが正しく解決されることを確認"""
        from src.config.settings import AppSettings

        with mock.patch.dict(os.environ, {
            "XBRL_OUTPUT_PATH": "/custom/output/path",
        }):
            settings = AppSettings()
            assert settings.resolved_output_path == Path("/custom/output/path")

    def test_resolved_log_dir_default(self):
        """デフォルトのログディレクトリが正しく解決されることを確認"""
        from src.config.settings import AppSettings

        settings = AppSettings()
        resolved = settings.resolved_log_dir
        assert resolved.name == "logs"
        assert resolved.parent == settings.project_root

    def test_resolved_lock_file_path_default(self):
        """デフォルトのロックファイルパスが正しく解決されることを確認"""
        from src.config.settings import AppSettings

        settings = AppSettings()
        resolved = settings.resolved_lock_file_path
        assert resolved.name == "script.lock"
        assert resolved.parent == settings.project_root

    def test_tse_stock_list_url_default(self):
        """デフォルトのTSE Stock List URLが正しく設定されることを確認"""
        from src.config.settings import AppSettings

        settings = AppSettings()
        assert settings.tse_stock_list_url is not None
        assert "jpx.co.jp" in settings.tse_stock_list_url
        assert "data_j.xls" in settings.tse_stock_list_url

    def test_tse_stock_list_url_env_override(self):
        """環境変数でTSE Stock List URLを上書きできることを確認"""
        from src.config.settings import AppSettings

        with mock.patch.dict(os.environ, {
            "TSE_STOCK_LIST_URL": "https://custom.example.com/data.xls",
        }):
            # キャッシュをクリア
            from src.config.settings import get_settings
            get_settings.cache_clear()

            settings = AppSettings()
            assert settings.tse_stock_list_url == "https://custom.example.com/data.xls"

    def test_tse_stock_list_url_xbrl_prefix(self):
        """XBRL_プレフィックス付きの環境変数でも設定できることを確認"""
        from src.config.settings import AppSettings

        with mock.patch.dict(os.environ, {
            "XBRL_TSE_STOCK_LIST_URL": "https://xbrl-prefix.example.com/data.xls",
        }):
            # キャッシュをクリア
            from src.config.settings import get_settings
            get_settings.cache_clear()

            settings = AppSettings()
            assert settings.tse_stock_list_url == "https://xbrl-prefix.example.com/data.xls"


class TestDatabaseSettings:
    """DatabaseSettingsのテスト"""

    def test_default_values(self):
        """デフォルト値が正しく設定されることを確認"""
        from src.config.settings import DatabaseSettings

        settings = DatabaseSettings()
        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.database == "xbrl"
        assert settings.username == ""
        assert settings.password == ""

    def test_connection_string(self):
        """接続文字列が正しく生成されることを確認"""
        from src.config.settings import DatabaseSettings

        with mock.patch.dict(os.environ, {
            "XBRL_DB_HOST": "db.example.com",
            "XBRL_DB_PORT": "5433",
            "XBRL_DB_DATABASE": "testdb",
            "XBRL_DB_USERNAME": "user",
            "XBRL_DB_PASSWORD": "pass",
        }):
            settings = DatabaseSettings()
            assert settings.connection_string == "postgresql://user:pass@db.example.com:5433/testdb"


class TestGetSettings:
    """get_settings関数のテスト"""

    def test_get_settings_returns_instance(self):
        """get_settingsがAppSettingsインスタンスを返すことを確認"""
        from src.config.settings import AppSettings, get_settings

        # キャッシュをクリア
        get_settings.cache_clear()

        settings = get_settings()
        assert isinstance(settings, AppSettings)

    def test_get_settings_is_cached(self):
        """get_settingsがキャッシュされることを確認"""
        from src.config.settings import get_settings

        # キャッシュをクリア
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
