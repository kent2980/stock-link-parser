"""
より詳細なエラーハンドリングテストとログ出力の確認
"""
import sys
import logging
from pathlib import Path
from unittest.mock import Mock, patch
import requests

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.api.ix.insert import Insert


def create_mock_response(status_code=200, json_data=None):
    """モックレスポンスを作成"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    return mock_response


def test_parallel_processing_with_errors():
    """並列処理でエラーが発生する場合のテスト"""
    print("=== Testing parallel processing with mixed results ===")

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

    # 混合結果：成功、失敗、例外を含む
    with patch.object(insert, 'file_path', return_value=create_mock_response(200)), \
         patch.object(insert, 'ix_head_titles', return_value=create_mock_response(500)), \
         patch.object(insert, 'sources', side_effect=requests.Timeout("Timeout error")), \
         patch.object(insert, 'loc_href_master', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_locs', return_value=create_mock_response(404)), \
         patch.object(insert, 'label_arcs', return_value=create_mock_response(200)), \
         patch.object(insert, 'label_values', side_effect=Exception("Generic error")), \
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
    print("Expected: False (due to multiple failures)")
    assert result is False, "Expected False when multiple API calls fail"
    print("✅ Parallel processing error test passed")


def test_all_api_types():
    """すべてのAPIタイプで異なるエラーケースをテスト"""
    print("\n=== Testing different error types for each API ===")

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

    # 各APIで異なるタイプのエラーを発生
    with patch.object(insert, 'file_path', return_value=create_mock_response(400)), \
         patch.object(insert, 'ix_head_titles', return_value=create_mock_response(401)), \
         patch.object(insert, 'sources', return_value=create_mock_response(403)), \
         patch.object(insert, 'loc_href_master', return_value=create_mock_response(404)), \
         patch.object(insert, 'label_locs', return_value=create_mock_response(500)), \
         patch.object(insert, 'label_arcs', return_value=create_mock_response(502)), \
         patch.object(insert, 'label_values', return_value=create_mock_response(503)), \
         patch.object(insert, 'cal_locs', side_effect=requests.ConnectionError("Connection failed")), \
         patch.object(insert, 'pre_locs', side_effect=requests.Timeout("Request timeout")), \
         patch.object(insert, 'def_locs', side_effect=ValueError("Invalid data")), \
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
    print("Expected: False (due to multiple different error types)")
    assert result is False, "Expected False when various error types occur"
    print("✅ Different error types test passed")


if __name__ == "__main__":
    test_parallel_processing_with_errors()
    test_all_api_types()
    print("\n🎉 All detailed tests passed!")
