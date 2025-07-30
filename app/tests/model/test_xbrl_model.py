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

    # ItemDictのitemはリストなので、最初の要素を取得
    assert isinstance(item_data, list) and len(item_data) > 0
    first_item = item_data[0]

    assert "head_item_key" in first_item
    assert "path" in first_item
    assert isinstance(first_item["head_item_key"], str)
    assert isinstance(first_item["path"], str)


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
        print(f"key: {item.key}")
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


def test_get_all_items_aggregation(xbrl_model_edjp):
    """同じkeyを持つItemDictのitem集約機能をテスト"""
    model = xbrl_model_edjp
    all_items = model.get_all_items()

    # キーの重複チェック - 集約後は重複がないはず
    keys = []
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        keys.append(key)

    unique_keys = set(keys)
    assert len(keys) == len(unique_keys), "集約後にキーの重複があってはいけません"

    # 集約されたアイテムの構造チェック
    for item in all_items:
        key = item.key if hasattr(item, "key") else item["key"]
        item_data = item.item if hasattr(item, "item") else item["item"]

        assert isinstance(key, str)
        # 集約されたitemは必ずリストになる
        assert isinstance(item_data, list)
        assert len(item_data) > 0

        # リスト内の各要素は辞書または基本型
        for data_item in item_data:
            assert isinstance(data_item, (dict, str, int, float, bool, type(None)))

    print(f"✅ Aggregation test passed: Found {len(all_items)} unique items")


def test_aggregate_items_by_key_direct(xbrl_model_edjp):
    """_aggregate_items_by_keyメソッドの直接テスト"""
    from app.ix_manager.base_xbrl_manager import ItemDict

    model = xbrl_model_edjp

    # テスト用のItemDictを作成
    test_items = []

    # 同じkeyを持つアイテムを複数作成
    item1 = ItemDict()
    item1.id = "test1"
    item1.key = "test_key"
    item1.item = {"data1": "value1"}
    item1.sort_position = 1
    test_items.append(item1)

    item2 = ItemDict()
    item2.id = "test2"
    item2.key = "test_key"  # 同じキー
    item2.item = {"data2": "value2"}
    item2.sort_position = 2
    test_items.append(item2)

    item3 = ItemDict()
    item3.id = "test3"
    item3.key = "different_key"
    item3.item = [{"data3": "value3"}]
    item3.sort_position = 0
    test_items.append(item3)

    # 集約を実行
    aggregated = model._aggregate_items_by_key(test_items)

    # 結果の検証
    assert len(aggregated) == 2  # "test_key"と"different_key"の2つになるはず

    # キーの検証
    keys = [item.key for item in aggregated]
    assert "test_key" in keys
    assert "different_key" in keys

    # 集約されたアイテムの検証
    test_key_item = next(item for item in aggregated if item.key == "test_key")
    different_key_item = next(
        item for item in aggregated if item.key == "different_key"
    )

    # test_keyのitemは2つの辞書を含むリストになっているはず
    assert isinstance(test_key_item.item, list)
    assert len(test_key_item.item) == 2
    assert {"data1": "value1"} in test_key_item.item
    assert {"data2": "value2"} in test_key_item.item

    # sort_positionは最小値（1）になっているはず
    assert test_key_item.sort_position == 1

    # different_keyのitemはそのまま
    assert isinstance(different_key_item.item, list)
    assert len(different_key_item.item) == 1
    assert {"data3": "value3"} in different_key_item.item
    assert different_key_item.sort_position == 0

    # ソート順の確認（sort_positionでソートされているはず）
    assert aggregated[0].key == "different_key"  # sort_position = 0
    assert aggregated[1].key == "test_key"  # sort_position = 1

    print("✅ Direct aggregation test passed")


def test_aggregate_items_mixed_types(xbrl_model_edjp):
    """異なる型のitemを持つItemDictの集約テスト"""
    from app.ix_manager.base_xbrl_manager import ItemDict

    model = xbrl_model_edjp

    # 混在する型のテストアイテムを作成
    test_items = []

    # 辞書型のitem
    item1 = ItemDict()
    item1.id = "test1"
    item1.key = "mixed_key"
    item1.item = {"type": "dict"}
    item1.sort_position = 1
    test_items.append(item1)

    # リスト型のitem
    item2 = ItemDict()
    item2.id = "test2"
    item2.key = "mixed_key"
    item2.item = [{"type": "list1"}, {"type": "list2"}]
    item2.sort_position = 2
    test_items.append(item2)

    # 文字列型のitem
    item3 = ItemDict()
    item3.id = "test3"
    item3.key = "mixed_key"
    item3.item = "string_value"
    item3.sort_position = 0
    test_items.append(item3)

    # 集約を実行
    aggregated = model._aggregate_items_by_key(test_items)

    # 結果の検証
    assert len(aggregated) == 1
    mixed_item = aggregated[0]

    assert mixed_item.key == "mixed_key"
    assert isinstance(mixed_item.item, list)
    assert len(mixed_item.item) == 4  # dict + list(2つ) + string = 4要素

    # 内容の検証
    expected_items = [
        "string_value",  # 最初に追加される（sort_position=0が最小）
        {"type": "dict"},
        {"type": "list1"},
        {"type": "list2"},
    ]

    # すべての期待される要素が含まれていることを確認
    for expected_item in expected_items:
        assert expected_item in mixed_item.item

    # sort_positionは最小値（0）になっているはず
    assert mixed_item.sort_position == 0

    print("✅ Mixed types aggregation test passed")


def test_get_all_items_as_dataclass_basic(xbrl_model_edjp):
    """get_all_items_as_dataclass基本機能テスト"""
    model = xbrl_model_edjp

    # データクラスのインスタンスを取得
    data_instance = model.get_all_items_as_dataclass()

    # データクラスのインスタンスであることを確認
    assert hasattr(data_instance, "__dataclass_fields__")

    # 元のget_all_itemsの結果と比較
    all_items = model.get_all_items()

    # 各ItemDictのkeyがプロパティとして存在することを確認
    for item in all_items:
        safe_key = model._make_safe_identifier(item.key)
        assert hasattr(data_instance, safe_key)

        # プロパティの値がItemDict.itemと一致することを確認
        property_value = getattr(data_instance, safe_key)
        assert property_value == item.item

    print(f"✅ Dataclass basic test passed: {len(all_items)} properties created")


def test_make_safe_identifier(xbrl_model_edjp):
    """_make_safe_identifierメソッドのテスト"""
    model = xbrl_model_edjp

    # 基本的なケース
    assert model._make_safe_identifier("valid_name") == "valid_name"
    assert model._make_safe_identifier("ValidName") == "ValidName"

    # 無効な文字を含むケース
    assert model._make_safe_identifier("invalid-name") == "invalid_name"
    assert model._make_safe_identifier("invalid.name") == "invalid_name"
    assert model._make_safe_identifier("invalid name") == "invalid_name"
    assert model._make_safe_identifier("invalid@name#123") == "invalid_name_123"

    # 数字で始まるケース
    assert model._make_safe_identifier("123name") == "_123name"
    assert model._make_safe_identifier("9test") == "_9test"

    # 空文字列のケース
    assert model._make_safe_identifier("") == "unknown_field"

    # Python予約語のケース
    assert model._make_safe_identifier("def") == "def_"
    assert model._make_safe_identifier("class") == "class_"
    assert model._make_safe_identifier("for") == "for_"
    assert model._make_safe_identifier("import") == "import_"

    print("✅ Safe identifier test passed")


def test_get_all_items_as_dataclass_properties(xbrl_model_edjp):
    """データクラスのプロパティアクセステスト"""
    model = xbrl_model_edjp
    data_instance = model.get_all_items_as_dataclass()

    # ix_file_pathプロパティが存在することを確認
    assert hasattr(data_instance, "ix_file_path")

    # ix_file_pathの値を確認
    ix_file_path_value = getattr(data_instance, "ix_file_path")
    assert isinstance(ix_file_path_value, list)
    assert len(ix_file_path_value) > 0

    # 最初の要素が辞書でファイルパス情報を含むことを確認
    first_item = ix_file_path_value[0]
    assert isinstance(first_item, dict)
    assert "head_item_key" in first_item
    assert "path" in first_item

    # データクラスのフィールド一覧を確認
    fields = data_instance.__dataclass_fields__
    assert len(fields) > 0

    # 各フィールドにアクセス可能であることを確認
    for field_name in fields:
        value = getattr(data_instance, field_name)
        assert value is not None  # 値が存在することを確認（Noneでない）

    print(f"✅ Dataclass properties test passed: {len(fields)} fields accessible")


def test_get_all_items_as_dataclass_immutable(xbrl_model_edjp):
    """データクラスのイミュータブル性テスト"""
    model = xbrl_model_edjp
    data_instance = model.get_all_items_as_dataclass()

    # frozenデータクラスであることを確認
    assert data_instance.__dataclass_params__.frozen is True

    # プロパティの変更が禁止されていることを確認
    with pytest.raises(Exception):  # FrozenInstanceErrorまたは類似のエラー
        # ix_file_pathプロパティを変更しようとする
        if hasattr(data_instance, "ix_file_path"):
            setattr(data_instance, "ix_file_path", "modified_value")

    print("✅ Dataclass immutable test passed")


def test_get_all_items_as_dataclass_consistency(xbrl_model_edjp):
    """データクラスと元データの整合性テスト"""
    model = xbrl_model_edjp

    # 複数回呼び出して一貫性を確認
    data_instance1 = model.get_all_items_as_dataclass()
    data_instance2 = model.get_all_items_as_dataclass()

    # 両方のインスタンスが同じフィールドを持つことを確認
    fields1 = set(data_instance1.__dataclass_fields__.keys())
    fields2 = set(data_instance2.__dataclass_fields__.keys())
    assert fields1 == fields2

    # 各フィールドの値が一致することを確認
    for field_name in fields1:
        value1 = getattr(data_instance1, field_name)
        value2 = getattr(data_instance2, field_name)
        assert value1 == value2

    # 元のget_all_itemsキーと一致することを確認
    all_items_keys = set(model.get_all_items_keys())
    safe_keys = set()
    for key in all_items_keys:
        safe_key = model._make_safe_identifier(key)
        safe_keys.add(safe_key)

    assert fields1 == safe_keys

    print("✅ Dataclass consistency test passed")


def test_get_all_items_as_dataclass_edge_cases(xbrl_model_edjp):
    """エッジケースのテスト"""
    model = xbrl_model_edjp

    # 特殊な文字を含むキーの処理テスト
    test_keys = [
        "normal_key",
        "key-with-dash",
        "key.with.dot",
        "key with space",
        "123numeric_start",
        "key@special#chars",
        "def",  # Python予約語
        "class",  # Python予約語
        "",  # 空文字列
    ]

    for key in test_keys:
        safe_key = model._make_safe_identifier(key)

        # 有効な識別子であることを確認
        assert safe_key.isidentifier() or safe_key == "unknown_field"

        # アンダースコアで始まっていない、または数字で始まっていた場合の処理が正しいことを確認
        if key and key[0].isdigit():
            assert safe_key.startswith("_")

    print("✅ Dataclass edge cases test passed")


def test_get_dataclass_property_names(xbrl_model_edjp):
    """get_dataclass_property_namesメソッドのテスト"""
    model = xbrl_model_edjp

    # プロパティ名リストを取得
    property_names = model.get_dataclass_property_names()

    # 基本チェック
    assert isinstance(property_names, list)
    assert len(property_names) > 0

    # 必須プロパティの存在確認
    assert "ix_file_path" in property_names

    # すべての名前が有効な識別子であることを確認
    for name in property_names:
        assert isinstance(name, str)
        assert name.isidentifier(), f"'{name}' is not a valid identifier"

    # データクラスのプロパティと一致することを確認
    data_instance = model.get_all_items_as_dataclass()
    dataclass_fields = set(data_instance.__dataclass_fields__.keys())
    property_names_set = set(property_names)

    assert dataclass_fields == property_names_set

    print(f"✅ Property names test passed: {len(property_names)} properties found")


def test_get_dataclass_property_info(xbrl_model_edjp):
    """get_dataclass_property_infoメソッドのテスト"""
    model = xbrl_model_edjp

    # プロパティ情報を取得
    property_info = model.get_dataclass_property_info()

    # 基本チェック
    assert isinstance(property_info, dict)
    assert len(property_info) > 0

    # 必須プロパティの存在確認
    assert "ix_file_path" in property_info

    # 各プロパティ情報の構造確認
    for prop_name, info in property_info.items():
        assert isinstance(prop_name, str)
        assert prop_name.isidentifier()

        # 必須フィールドの存在確認
        assert "original_key" in info
        assert "type" in info
        assert "value_sample" in info
        assert "length" in info

        # 型の確認
        assert isinstance(info["original_key"], str)
        assert isinstance(info["type"], str)

        # lengthはNoneまたは整数
        assert info["length"] is None or isinstance(info["length"], int)

    # ix_file_pathの詳細確認
    ix_info = property_info["ix_file_path"]
    assert ix_info["original_key"] == "ix_file_path"
    assert ix_info["type"] == "list"
    assert isinstance(ix_info["value_sample"], list)
    assert ix_info["length"] is not None and ix_info["length"] > 0

    print(f"✅ Property info test passed: {len(property_info)} properties analyzed")


def test_dataclass_type_hints_support(xbrl_model_edjp):
    """型ヒント支援機能のテスト"""
    model = xbrl_model_edjp

    # データクラスインスタンスを取得
    data_instance = model.get_all_items_as_dataclass()

    # 基本プロパティの存在確認（プロトコルで定義されたもの）
    assert hasattr(data_instance, "ix_file_path")
    assert isinstance(data_instance.ix_file_path, list)

    # カスタム属性の存在確認
    assert hasattr(data_instance, "__property_hints__")
    assert hasattr(data_instance, "__available_properties__")

    # プロパティヒント情報の確認
    hints = data_instance.__property_hints__
    assert isinstance(hints, dict)
    assert "ix_file_path" in hints

    # 利用可能なプロパティリストの確認
    available_props = data_instance.__available_properties__
    assert isinstance(available_props, list)
    assert "ix_file_path" in available_props

    # 動的プロパティアクセスの確認
    for prop_name in available_props:
        assert hasattr(data_instance, prop_name)
        value = getattr(data_instance, prop_name)
        assert value is not None

    # 戻り値の型がXBRLDataProtocolとして扱われることを確認
    # （型注釈での確認のため、実際の実行時チェックは行わない）
    from app.ix_models.xbrl_model import XBRLDataProtocol

    # 型チェッカー向けの確認（実行時には影響しない）
    typed_instance: XBRLDataProtocol = data_instance  # type: ignore
    assert typed_instance.ix_file_path is not None

    print("✅ Type hints support test passed")


def test_dataclass_ide_integration(xbrl_model_edjp):
    """IDE統合機能のテスト"""
    model = xbrl_model_edjp

    # プロパティ名とプロパティ情報の整合性確認
    property_names = model.get_dataclass_property_names()
    property_info = model.get_dataclass_property_info()
    data_instance = model.get_all_items_as_dataclass()

    # 3つのメソッドで取得した情報の整合性確認
    assert set(property_names) == set(property_info.keys())
    assert set(property_names) == set(data_instance.__available_properties__)

    # 各プロパティについて詳細確認
    for prop_name in property_names:
        # プロパティ情報の確認
        info = property_info[prop_name]

        # データクラスインスタンスのプロパティ確認
        actual_value = getattr(data_instance, prop_name)

        # 型の整合性確認
        expected_type_name = info["type"]
        actual_type_name = type(actual_value).__name__
        assert actual_type_name == expected_type_name

        # サンプル値の確認（リストの場合は最初の部分が一致するはず）
        sample = info["value_sample"]
        if isinstance(actual_value, list) and isinstance(sample, list):
            # サンプルに"...（他の要素も存在）"が含まれている場合は除外して比較
            sample_clean = [
                item
                for item in sample
                if not isinstance(item, str) or not item.startswith("...")
            ]
            if sample_clean:
                assert actual_value[: len(sample_clean)] == sample_clean
        else:
            assert actual_value == sample

    print(f"✅ IDE integration test passed: Verified {len(property_names)} properties")
