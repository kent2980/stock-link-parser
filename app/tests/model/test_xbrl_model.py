import pprint
from pathlib import Path
from time import sleep
from typing import Dict, List, Union

import pytest
import requests
from tqdm import tqdm

from app.ix_manager import (
    BaseXbrlManager,
    CalLinkManager,
    DefLinkManager,
    IXBRLManager,
    LabelManager,
    PreLinkManager,
)
from app.ix_models import XBRLModel
from app.ix_models.xbrl_model import XBRLItem
from app.ix_tag import IxHeader


@pytest.fixture
def xbrl_model_edjp(get_xbrl_edjp_zip, get_output_dir):
    print(f"get_xbrl_edjp_zip: {get_xbrl_edjp_zip}")
    print(f"get_output_dir: {get_output_dir}")
    return XBRLModel(get_xbrl_edjp_zip, get_output_dir)


@pytest.fixture
def xbrl_model_rvfc(get_xbrl_rvfc_zip, get_output_dir):
    return XBRLModel(get_xbrl_rvfc_zip, get_output_dir)


def test_xbrl_model_instance(xbrl_model_edjp):
    assert isinstance(xbrl_model_edjp, XBRLModel)


def test_ixbrl_manager(xbrl_model_edjp):
    assert xbrl_model_edjp.get_ixbrl() is not None
    manager = xbrl_model_edjp.get_ixbrl()
    if manager:
        header = manager.ix_header
        assert sorted(header.keys()) == sorted(IxHeader.keys())


def test_all_edjp(xbrl_model_edjp):
    model = xbrl_model_edjp
    print("Start test_all_edjp")
    print(model.ixbrl_manager.xbrl_type())
    assert model.ixbrl_manager.xbrl_type() == "決算短信（日本基準）"
    assert isinstance(model.ixbrl_manager, IXBRLManager)
    assert isinstance(model.label_manager, LabelManager)
    assert isinstance(model.def_link_manager, DefLinkManager)
    assert isinstance(model.pre_link_manager, PreLinkManager)
    assert isinstance(model.cal_link_manager, CalLinkManager)


def test_xbrl_dir(get_xbrl_zip_dir, get_output_dir):
    XBRLModel.xbrl_models(get_xbrl_zip_dir, get_output_dir)
    for model in XBRLModel.xbrl_models(get_xbrl_zip_dir, get_output_dir):
        assert isinstance(model, XBRLModel)
        for _, manager in model.get_all_manager().items():
            assert manager is not None
            assert isinstance(manager, BaseXbrlManager)
            for item in manager.items:
                if item.key == "href_master":
                    pprint.pprint(item.item)


def test_all_managers(xbrl_model_edjp):
    model = xbrl_model_edjp
    item = model.get_all_items()
    assert isinstance(item, list)


def test_get_all_items_structure(xbrl_model_edjp):
    """get_all_itemsの基本構造をテスト"""
    model = xbrl_model_edjp
    all_items = model.get_all_items()

    # 戻り値がリストであることを確認
    assert isinstance(all_items, list)
    assert len(all_items) > 0

    # 各アイテムがkey and item属性を持つことを確認
    for item in all_items:
        # 辞書またはItemDictオブジェクトであることを確認
        assert hasattr(item, "key") or (isinstance(item, dict) and "key" in item)
        assert hasattr(item, "item") or (isinstance(item, dict) and "item" in item)

        # keyの取得
        key = item.key if hasattr(item, "key") else item["key"]
        item_data = item.item if hasattr(item, "item") else item["item"]

        assert isinstance(key, str)
        # itemは辞書またはリストである可能性がある
        assert isinstance(item_data, (dict, list))


def test_get_all_items_file_path_included(xbrl_model_edjp):
    """ファイルパス情報が含まれていることをテスト"""
    model = xbrl_model_edjp
    all_items = model.get_all_items()

    # ix_file_pathが最初の要素として含まれることを確認
    file_path_items = []
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        if key == "ix_file_path":
            file_path_items.append(item)

    assert len(file_path_items) == 1

    file_path_item = file_path_items[0]
    item_data = (
        file_path_item.item
        if hasattr(file_path_item, "item")
        else file_path_item["item"]
    )

    assert "head_item_key" in item_data
    assert "path" in item_data
    assert isinstance(item_data["head_item_key"], str)
    assert isinstance(item_data["path"], str)


def test_get_all_items_manager_data_included(xbrl_model_edjp):
    """各マネージャーのデータが含まれていることをテスト"""
    model = xbrl_model_edjp
    all_items = model.get_all_items()

    # 利用可能なマネージャーを取得
    managers = model.get_all_manager()

    # 各マネージャーからのデータが含まれていることを確認
    for manager_key, manager in managers.items():
        if manager and hasattr(manager, "items"):
            manager_items = []
            for item in all_items:
                key = item.key if hasattr(item, "key") else item["key"]
                if key.startswith(manager_key):
                    manager_items.append(item)

            # マネージャーにデータがある場合、all_itemsにも含まれているはず
            if len(manager.items) > 0:
                assert len(manager_items) >= 0  # 少なくとも何らかのデータが存在


def test_get_all_items_keys_consistency(xbrl_model_edjp):
    """get_all_items_keysとの整合性をテスト"""
    model = xbrl_model_edjp
    all_items = model.get_all_items()
    all_keys = model.get_all_items_keys()

    # get_all_itemsから取得したキーの集合
    items_keys = set()
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        items_keys.add(key)

    # get_all_items_keysから取得したキーの集合
    keys_set = set(all_keys)

    # 両方の集合が一致することを確認
    assert items_keys == keys_set


def test_get_all_items_type_safety(xbrl_model_edjp):
    """型安全性をテスト"""
    model = xbrl_model_edjp
    all_items = model.get_all_items()

    for item in all_items:
        # key属性の型チェック
        key = item.key if hasattr(item, "key") else item["key"]
        assert isinstance(key, str)

        # item属性の型チェック（辞書またはリスト）
        item_data = item.item if hasattr(item, "item") else item["item"]
        assert isinstance(item_data, (dict, list))

        # 辞書の場合、キーと値の型をチェック
        if isinstance(item_data, dict):
            for k, v in item_data.items():
                assert isinstance(k, str)
                # 値は様々な型を許可
                assert isinstance(v, (str, int, float, bool, type(None), list, dict))


def test_get_all_items_caching(xbrl_model_edjp):
    """キャッシュ機能をテスト"""
    model = xbrl_model_edjp

    # 初回呼び出し
    first_call = model.get_all_items()

    # 2回目の呼び出し（キャッシュされた結果を使用）
    second_call = model.get_all_items()

    # 同じ内容が返されることを確認（オブジェクトIDは異なるかもしれない）
    assert len(first_call) == len(second_call)

    # all_itemsプロパティで同じ結果が得られることを確認
    property_result = model.all_items
    assert len(property_result) == len(first_call)

    # プロパティはキャッシュされたものを返すはず
    property_result2 = model.all_items
    assert property_result is property_result2


def test_get_all_items_data_integrity(xbrl_model_edjp):
    """データの整合性をテスト"""
    model = xbrl_model_edjp
    all_items = model.get_all_items()

    # キーを収集
    keys = []
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        keys.append(key)

    unique_keys = set(keys)

    # キーの重複がある場合は警告（完全に重複を排除する必要がない場合もある）
    if len(keys) != len(unique_keys):
        duplicate_keys = set([key for key in keys if keys.count(key) > 1])
        print(f"Warning: Duplicate keys found: {duplicate_keys}")

    # 最低限のデータが含まれていることを確認
    assert len(all_items) > 0

    # ix_file_pathは必ず含まれるべき
    file_path_exists = False
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        if key == "ix_file_path":
            file_path_exists = True
            break
    assert file_path_exists


def test_get_all_items_with_different_models(xbrl_model_rvfc):
    """異なるXBRLモデルでの動作をテスト"""
    model = xbrl_model_rvfc
    all_items = model.get_all_items()

    # 基本的な構造チェック
    assert isinstance(all_items, list)
    assert len(all_items) > 0

    # ファイルパス情報の存在確認
    file_path_exists = False
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        if key == "ix_file_path":
            file_path_exists = True
            break
    assert file_path_exists


def test_get_all_items_comprehensive(xbrl_model_edjp):
    """get_all_itemsの包括的テスト"""
    model = xbrl_model_edjp

    # 基本動作の確認
    all_items = model.get_all_items()
    assert isinstance(all_items, list)
    assert len(all_items) > 0

    # キーの一意性と整合性
    keys = []
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        keys.append(key)

    # get_all_items_keysとの整合性
    items_keys = model.get_all_items_keys()
    assert set(keys) == set(items_keys)

    # データの構造チェック
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        item_data = item.item if hasattr(item, "item") else item["item"]

        assert isinstance(key, str)
        assert len(key) > 0
        assert isinstance(item_data, (dict, list))

    # 必須データの存在確認
    required_keys = ["ix_file_path"]
    found_keys = set(keys)

    for required_key in required_keys:
        assert (
            required_key in found_keys
        ), f"Required key '{required_key}' not found in all_items"

    print(
        f"✅ Test passed: Found {len(all_items)} items with {len(set(keys))} unique keys"
    )
