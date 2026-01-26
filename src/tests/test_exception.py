"""例外クラスのテスト"""

import pytest

from src.exception.base_exception import (
    APIConnectionError,
    APIInsertionError,
    DataProcessingError,
    DirectoryNotFoundError,
    ErrorCode,
    ManagerInitError,
    ParserInitError,
    TagNotFoundError,
    XBRLBaseException,
    XBRLListEmptyError,
    XBRLParseError,
)


class TestErrorCode:
    """ErrorCodeのテスト"""

    def test_error_code_values(self):
        """エラーコードの値が正しく定義されていることを確認"""
        assert ErrorCode.UNKNOWN_ERROR.value == 1000
        assert ErrorCode.DIRECTORY_NOT_FOUND.value == 2001
        assert ErrorCode.XBRL_LIST_EMPTY.value == 3001
        assert ErrorCode.MANAGER_INIT_ERROR.value == 4001
        assert ErrorCode.API_CONNECTION_ERROR.value == 5001


class TestXBRLBaseException:
    """XBRLBaseExceptionのテスト"""

    def test_default_message(self):
        """デフォルトメッセージが設定されることを確認"""
        exc = XBRLBaseException(log_error=False)
        assert "不明なエラー" in str(exc)

    def test_custom_message(self):
        """カスタムメッセージが設定されることを確認"""
        exc = XBRLBaseException(message="テストエラー", log_error=False)
        assert "テストエラー" in str(exc)

    def test_error_code(self):
        """エラーコードが含まれることを確認"""
        exc = XBRLBaseException(log_error=False)
        assert "UNKNOWN_ERROR" in str(exc)
        assert "1000" in str(exc)

    def test_details(self):
        """詳細情報が含まれることを確認"""
        exc = XBRLBaseException(
            message="テスト",
            details={"file": "test.xml"},
            log_error=False,
        )
        assert "file=test.xml" in str(exc)

    def test_cause(self):
        """原因例外が含まれることを確認"""
        original = ValueError("元のエラー")
        exc = XBRLBaseException(
            message="ラップエラー",
            cause=original,
            log_error=False,
        )
        assert "ValueError" in str(exc)
        assert "元のエラー" in str(exc)

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        exc = XBRLBaseException(
            message="テスト",
            details={"key": "value"},
            log_error=False,
        )
        result = exc.to_dict()
        assert result["error_code"] == 1000
        assert result["error_name"] == "UNKNOWN_ERROR"
        assert result["message"] == "テスト"
        assert result["details"] == {"key": "value"}


class TestSpecificExceptions:
    """特定の例外クラスのテスト"""

    def test_directory_not_found_error(self):
        """DirectoryNotFoundErrorのテスト"""
        exc = DirectoryNotFoundError(message="/path/to/dir", log_error=False)
        assert "DIRECTORY_NOT_FOUND" in str(exc)
        assert "2001" in str(exc)

    def test_xbrl_list_empty_error(self):
        """XBRLListEmptyErrorのテスト"""
        exc = XBRLListEmptyError(message="ファイルが見つかりません", log_error=False)
        assert "XBRL_LIST_EMPTY" in str(exc)
        assert "3001" in str(exc)

    def test_xbrl_parse_error(self):
        """XBRLParseErrorのテスト"""
        exc = XBRLParseError(message="解析エラー", log_error=False)
        assert "XBRL_PARSE_ERROR" in str(exc)
        assert "3003" in str(exc)

    def test_tag_not_found_error(self):
        """TagNotFoundErrorのテスト"""
        exc = TagNotFoundError(message="タグが見つかりません", log_error=False)
        assert "TAG_NOT_FOUND" in str(exc)
        assert "3004" in str(exc)

    def test_manager_init_error(self):
        """ManagerInitErrorのテスト"""
        exc = ManagerInitError(message="初期化失敗", log_error=False)
        assert "MANAGER_INIT_ERROR" in str(exc)
        assert "4001" in str(exc)

    def test_parser_init_error(self):
        """ParserInitErrorのテスト"""
        exc = ParserInitError(message="パーサー初期化失敗", log_error=False)
        assert "PARSER_INIT_ERROR" in str(exc)
        assert "4002" in str(exc)

    def test_data_processing_error(self):
        """DataProcessingErrorのテスト"""
        exc = DataProcessingError(message="処理エラー", log_error=False)
        assert "DATA_PROCESSING_ERROR" in str(exc)
        assert "4003" in str(exc)

    def test_api_connection_error(self):
        """APIConnectionErrorのテスト"""
        exc = APIConnectionError(message="接続エラー", log_error=False)
        assert "API_CONNECTION_ERROR" in str(exc)
        assert "5001" in str(exc)

    def test_api_insertion_error(self):
        """APIInsertionErrorのテスト"""
        exc = APIInsertionError(message="挿入エラー", log_error=False)
        assert "API_INSERTION_ERROR" in str(exc)
        assert "5003" in str(exc)


class TestExceptionChaining:
    """例外チェインのテスト"""

    def test_exception_chaining(self):
        """例外チェインが正しく動作することを確認"""
        try:
            try:
                raise ValueError("元のエラー")
            except ValueError as e:
                raise XBRLParseError(
                    message="解析中にエラー",
                    cause=e,
                    log_error=False,
                ) from e
        except XBRLParseError as exc:
            assert exc.cause is not None
            assert isinstance(exc.cause, ValueError)
            assert exc.__cause__ is not None
