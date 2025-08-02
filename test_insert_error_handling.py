"""
Insert APIのエラーハンドリングをテストするための簡単なテストスクリプト
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import requests

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.api.ix.insert import Insert
from app.ix_models import XBRLModel


def create_mock_response(status_code=200, json_data=None):
    """モックレスポンスを作成"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    return mock_response


def test_insert_api_push_success():
    """すべてのAPI呼び出しが成功する場合のテスト"""
    print("=== Testing successful API calls ===")

    # モックデータクラスインスタンスを作成
    mock_data = Mock()
    mock_data.ix_file_path_json = '{"test": "data"}'
    mock_data.ix_head_title_json = '{"test": "data"}'
    mock_data.get_all_source_files_json.return_value = '[{"test": "data"}]'
    mock_data.href_master_json = '{"test": "data"}'
    mock_data.lab_link_locs_json = '{"test": "data"}'
    mock_data.lab_link_arcs_json = '{"test": "data"}'
    mock_data.lab_link_values_json = '{"test": "data"}'
    mock_data.cal_link_locs_json = '{"test": "data"}'
    mock_data.pre_link_locs_json = '{"test": "data"}'
    mock_data.def_link_locs_json = '{"test": "data"}'
    mock_data.def_link_arcs_json = '{"test": "data"}'
    mock_data.cal_link_arcs_json = '{"test": "data"}'
    mock_data.pre_link_arcs_json = '{"test": "data"}'
    mock_data.ix_non_numeric_json = '{"test": "data"}'
    mock_data.ix_non_fraction_json = '{"test": "data"}'
    mock_data.qualitative_info_json = '{"test": "data"}'

    insert = Insert("/tmp", "http://test.com")

    # すべてのAPIメソッドが成功レスポンス（200）を返すようにモック
    with patch.object(insert, 'file_path', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_head_titles', return_value=create_mock_response(200)), \
         patch.object(insert, 'sources', return_value=create_mock_response(200)), \
         patch.object(insert, 'loc_href_master', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_values', return_value=create_mock_response(200)), \
         patch.object(insert, 'cal_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'pre_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'def_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'def_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'cal_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'pre_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_non_numerics', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_non_fractions', return_value=create_mock_response(200)), \
         patch.object(insert, 'qualitative', return_value=create_mock_response(200)), \
         patch.object(insert, 'set_head_active', return_value=create_mock_response(200)), \
         patch.object(insert, 'update_head_generate', return_value=create_mock_response(200)):

        result = insert._Insert__insert_api_push(mock_data, "test-key")

    print(f"Result: {result}")
    assert result is True, "Expected True when all API calls succeed"
    print("✅ Success test passed")


def test_insert_api_push_failure():
    """一部のAPI呼び出しが失敗する場合のテスト"""
    print("\n=== Testing failed API calls ===")

    # モックデータクラスインスタンスを作成
    mock_data = Mock()
    mock_data.ix_file_path_json = '{"test": "data"}'
    mock_data.ix_head_title_json = '{"test": "data"}'
    mock_data.get_all_source_files_json.return_value = '[{"test": "data"}]'
    mock_data.href_master_json = '{"test": "data"}'
    mock_data.lab_link_locs_json = '{"test": "data"}'
    mock_data.lab_link_arcs_json = '{"test": "data"}'
    mock_data.lab_link_values_json = '{"test": "data"}'
    mock_data.cal_link_locs_json = '{"test": "data"}'
    mock_data.pre_link_locs_json = '{"test": "data"}'
    mock_data.def_link_locs_json = '{"test": "data"}'
    mock_data.def_link_arcs_json = '{"test": "data"}'
    mock_data.cal_link_arcs_json = '{"test": "data"}'
    mock_data.pre_link_arcs_json = '{"test": "data"}'
    mock_data.ix_non_numeric_json = '{"test": "data"}'
    mock_data.ix_non_fraction_json = '{"test": "data"}'
    mock_data.qualitative_info_json = '{"test": "data"}'

    insert = Insert("/tmp", "http://test.com")

    # 一部のAPIメソッドが失敗レスポンス（500）を返すようにモック
    with patch.object(insert, 'file_path', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_head_titles', return_value=create_mock_response(500)), \
         patch.object(insert, 'sources', return_value=create_mock_response(200)), \
         patch.object(insert, 'loc_href_master', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_locs', return_value=create_mock_response(404)), \
         patch.object(insert, 'label_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_values', return_value=create_mock_response(200)), \
         patch.object(insert, 'cal_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'pre_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'def_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'def_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'cal_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'pre_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_non_numerics', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_non_fractions', return_value=create_mock_response(200)), \
         patch.object(insert, 'qualitative', return_value=create_mock_response(200)), \
         patch.object(insert, 'set_head_active', return_value=create_mock_response(200)), \
         patch.object(insert, 'update_head_generate', return_value=create_mock_response(200)):

        result = insert._Insert__insert_api_push(mock_data, "test-key")

    print(f"Result: {result}")
    assert result is False, "Expected False when some API calls fail"
    print("✅ Failure test passed")


def test_insert_api_push_exception():
    """例外が発生する場合のテスト"""
    print("\n=== Testing exception handling ===")

    # モックデータクラスインスタンスを作成
    mock_data = Mock()
    mock_data.ix_file_path_json = '{"test": "data"}'
    mock_data.ix_head_title_json = '{"test": "data"}'
    mock_data.get_all_source_files_json.return_value = '[{"test": "data"}]'
    mock_data.href_master_json = '{"test": "data"}'
    mock_data.lab_link_locs_json = '{"test": "data"}'
    mock_data.lab_link_arcs_json = '{"test": "data"}'
    mock_data.lab_link_values_json = '{"test": "data"}'
    mock_data.cal_link_locs_json = '{"test": "data"}'
    mock_data.pre_link_locs_json = '{"test": "data"}'
    mock_data.def_link_locs_json = '{"test": "data"}'
    mock_data.def_link_arcs_json = '{"test": "data"}'
    mock_data.cal_link_arcs_json = '{"test": "data"}'
    mock_data.pre_link_arcs_json = '{"test": "data"}'
    mock_data.ix_non_numeric_json = '{"test": "data"}'
    mock_data.ix_non_fraction_json = '{"test": "data"}'
    mock_data.qualitative_info_json = '{"test": "data"}'

    insert = Insert("/tmp", "http://test.com")

    # 一部のAPIメソッドが例外を投げるようにモック
    with patch.object(insert, 'file_path', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_head_titles', side_effect=requests.RequestException("Connection error")), \
         patch.object(insert, 'sources', return_value=create_mock_response(200)), \
         patch.object(insert, 'loc_href_master', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_values', return_value=create_mock_response(200)), \
         patch.object(insert, 'cal_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'pre_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'def_locs', return_value=create_mock_response(200)), \
         patch.object(insert, 'def_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'cal_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'pre_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_non_numerics', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_non_fractions', return_value=create_mock_response(200)), \
         patch.object(insert, 'qualitative', return_value=create_mock_response(200)), \
         patch.object(insert, 'set_head_active', return_value=create_mock_response(200)), \
         patch.object(insert, 'update_head_generate', return_value=create_mock_response(200)):

        result = insert._Insert__insert_api_push(mock_data, "test-key")

    print(f"Result: {result}")
    assert result is False, "Expected False when exceptions occur"
    print("✅ Exception test passed")


if __name__ == "__main__":
    test_insert_api_push_success()
    test_insert_api_push_failure()
    test_insert_api_push_exception()
    print("\n🎉 All tests passed!")
