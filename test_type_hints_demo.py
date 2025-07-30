#!/usr/bin/env python3
"""
型ヒント機能のデモンストレーション

このファイルは、実装した型ヒント機能がIDEでどのように動作するかを
確認するためのデモです。
"""

from app.ix_models import XBRLModel
from pathlib import Path


def demo_type_hints():
    """型ヒント機能のデモ"""

    # テスト用のXBRLファイル（実際の使用時は適切なパスを指定）
    xbrl_path = Path("app/tests/.xbrl/edjp.zip")
    output_path = Path("app/tests/.output")

    if not xbrl_path.exists():
        print("テストファイルが見つかりません。")
        return

    # XBRLModelのインスタンスを作成
    model = XBRLModel(xbrl_path, output_path)

    print("=== 利用可能なプロパティ名 ===")
    property_names = model.get_dataclass_property_names()
    for i, name in enumerate(property_names[:10], 1):  # 最初の10個のみ表示
        print(f"{i:2d}. {name}")
    if len(property_names) > 10:
        print(f"    ... 他 {len(property_names) - 10} 個のプロパティ")

    print("\n=== プロパティ情報の詳細 ===")
    property_info = model.get_dataclass_property_info()

    # ix_file_pathの詳細表示
    if "ix_file_path" in property_info:
        info = property_info["ix_file_path"]
        print(f"プロパティ名: ix_file_path")
        print(f"  元のキー: {info['original_key']}")
        print(f"  型: {info['type']}")
        print(f"  要素数: {info['length']}")
        print(f"  サンプル値: {info['value_sample']}")

    print("\n=== データクラスインスタンスの使用 ===")
    data = model.get_all_items_as_dataclass()

    # 型ヒント付きでアクセス（IDEで自動補完されるはず）
    file_path_data = data.ix_file_path
    print(f"ファイルパス情報: {len(file_path_data)} 件")

    # 動的プロパティアクセスの例
    print("\n=== 利用可能なプロパティの一覧 ===")
    available_props = data.__available_properties__
    for prop_name in available_props[:5]:  # 最初の5個のみ表示
        value = getattr(data, prop_name)
        value_info = f"({type(value).__name__}"
        if isinstance(value, (list, dict, str)):
            value_info += f", 要素数: {len(value)}"
        value_info += ")"
        print(f"  {prop_name}: {value_info}")

    print(f"\n合計 {len(available_props)} 個のプロパティが利用可能です。")

    # 型ヒント情報の表示
    print("\n=== 型ヒント情報 ===")
    hints = data.__property_hints__
    for prop_name in list(hints.keys())[:5]:  # 最初の5個のみ表示
        type_info = hints[prop_name].__name__
        print(f"  {prop_name}: {type_info}")


if __name__ == "__main__":
    demo_type_hints()
