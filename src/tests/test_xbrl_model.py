"""XBRLModelのテスト"""

import json
import tempfile
from pathlib import Path

import pytest

from src.ix_models.xbrl_model import XBRLModel


# テストデータのディレクトリ
TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def sample_zip_file():
    """テスト用のサンプルzipファイルを取得"""
    zip_files = sorted(TEST_DATA_DIR.glob("*.zip"))
    if not zip_files:
        pytest.skip("テストデータが見つかりません")
    return zip_files[0]


@pytest.fixture
def temp_output_dir():
    """一時出力ディレクトリを作成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestXBRLModelInitialization:
    """XBRLModelの初期化テスト"""

    def test_initialization(self, sample_zip_file, temp_output_dir):
        """XBRLModelが正しく初期化されることを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        assert model is not None
        assert model.head_item_key is not None
        assert model.xbrl_category is not None

    def test_directory_path_created(self, sample_zip_file, temp_output_dir):
        """zip解凍後のディレクトリパスが設定されることを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        assert model.directory_path is not None
        assert Path(model.directory_path).exists()

    def test_managers_initialized(self, sample_zip_file, temp_output_dir):
        """各マネージャーが初期化されることを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        # ixbrl_managerが初期化されるまで待機
        model.ixbrl_manager_initialized.wait(timeout=60)

        # 少なくとも一部のマネージャーは初期化されているはず
        managers = model.get_all_manager()
        assert len(managers) > 0


class TestXBRLModelDataRetrieval:
    """XBRLModelのデータ取得テスト"""

    def test_get_all_items(self, sample_zip_file, temp_output_dir):
        """get_all_itemsが正しくデータを返すことを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        items = model.get_all_items()

        assert items is not None
        assert isinstance(items, list)
        assert len(items) > 0

    def test_get_all_items_keys(self, sample_zip_file, temp_output_dir):
        """get_all_items_keysが正しくキーを返すことを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        keys = model.get_all_items_keys()

        assert keys is not None
        assert isinstance(keys, list)
        assert len(keys) > 0

    def test_required_keys_present(self, sample_zip_file, temp_output_dir):
        """必須キーが含まれていることを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        keys = model.get_all_items_keys()

        # 期待されるキーの一部をチェック
        expected_keys = [
            "ix_file_path",
            "ix_context",
            "ix_head_title",
            "ix_non_fraction",
            "ix_non_numeric",
            "ix_source_file",
        ]

        for expected_key in expected_keys:
            assert expected_key in keys, f"{expected_key} が見つかりません"

    def test_get_all_items_as_dataclass(self, sample_zip_file, temp_output_dir):
        """get_all_items_as_dataclassが正しくデータクラスを返すことを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        data_class = model.get_all_items_as_dataclass()

        assert data_class is not None
        assert hasattr(data_class, "__available_properties__")

        # プロパティにアクセスできることを確認
        assert hasattr(data_class, "ix_file_path")

    def test_dataclass_json_properties(self, sample_zip_file, temp_output_dir):
        """データクラスのJSON版プロパティが存在することを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        data_class = model.get_all_items_as_dataclass()

        # JSON版プロパティを取得
        json_properties = data_class.get_json_properties()

        assert json_properties is not None
        assert len(json_properties) > 0
        assert all(prop.endswith("_json") for prop in json_properties)


class TestXBRLModelSourceFiles:
    """XBRLModelのソースファイル関連テスト"""

    def test_get_source_file_items(self, sample_zip_file, temp_output_dir):
        """get_source_file_itemsが正しくデータを返すことを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        source_file_items = model.get_source_file_items()

        assert source_file_items is not None
        assert isinstance(source_file_items, list)

        # 全てのキーがsource_fileで終わることを確認
        for item in source_file_items:
            assert item.key.endswith("source_file")

    def test_get_aggregated_source_files(self, sample_zip_file, temp_output_dir):
        """get_aggregated_source_filesが正しく集約データを返すことを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        aggregated = model.get_aggregated_source_files()

        assert aggregated is not None
        assert isinstance(aggregated, dict)

        # 全てのキーがsource_fileで終わることを確認
        for key in aggregated.keys():
            assert key.endswith("source_file")


class TestXBRLModelFilePath:
    """XBRLModelのファイルパス関連テスト"""

    def test_get_file_path(self, sample_zip_file, temp_output_dir):
        """get_file_pathが正しいデータを返すことを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        file_path = model.get_file_path()

        assert file_path is not None
        assert file_path.head_item_key == model.head_item_key
        assert str(sample_zip_file) in file_path.path


class TestXBRLModelIXBRL:
    """XBRLModelのiXBRL関連テスト"""

    def test_ixbrl_manager(self, sample_zip_file, temp_output_dir):
        """ixbrl_managerが正しく取得できることを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        # ixbrl_managerが初期化されるまで待機
        model.ixbrl_manager_initialized.wait(timeout=60)

        ixbrl_manager = model.ixbrl_manager

        assert ixbrl_manager is not None

    def test_ix_header(self, sample_zip_file, temp_output_dir):
        """ix_headerが取得できることを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        # ixbrl_managerが初期化されるまで待機
        model.ixbrl_manager_initialized.wait(timeout=60)

        header = model.ix_header()

        # ヘッダーが取得できればOK（Noneの場合もある）
        if header is not None:
            assert hasattr(header, "company_name") or hasattr(header, "document_name")


class TestXBRLModelJsonOutput:
    """XBRLModelのJSON出力テスト"""

    def test_json_serialization(self, sample_zip_file, temp_output_dir):
        """データがJSONシリアライズ可能であることを確認"""
        model = XBRLModel(sample_zip_file, temp_output_dir)

        data_class = model.get_all_items_as_dataclass()

        # 全てのプロパティをJSONシリアライズ
        for prop_name in data_class.__available_properties__:
            if not prop_name.endswith("_json"):
                value = getattr(data_class, prop_name)
                try:
                    json.dumps(value, ensure_ascii=False, default=str)
                except (TypeError, ValueError) as e:
                    pytest.fail(f"{prop_name}のJSONシリアライズに失敗: {e}")
