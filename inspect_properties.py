#!/usr/bin/env python3
"""
実際に利用可能なプロパティを確認するスクリプト
"""

from app.ix_models import XBRLModel
from pathlib import Path


def inspect_properties():
    """プロパティを調査"""

    # テスト用のXBRLファイル
    xbrl_path = Path("app/tests/.xbrl/edjp.zip")
    output_path = Path("app/tests/.output")

    if not xbrl_path.exists():
        print("テストファイルが見つかりません。")
        return

    # XBRLModelのインスタンスを作成
    model = XBRLModel(xbrl_path, output_path)

    # プロパティ名を取得
    property_names = model.get_dataclass_property_names()
    property_info = model.get_dataclass_property_info()

    print("=== 利用可能なプロパティと型情報 ===")

    type_definitions = []

    for prop_name in sorted(property_names):
        if prop_name in property_info:
            info = property_info[prop_name]
            type_name = info["type"]
            original_key = info["original_key"]

            # 型定義を生成
            if type_name == "list":
                type_def = f"    {prop_name}: List[Dict[str, Any]]  # {original_key}"
            elif type_name == "dict":
                type_def = f"    {prop_name}: Dict[str, Any]  # {original_key}"
            else:
                type_def = f"    {prop_name}: {type_name}  # {original_key}"

            type_definitions.append(type_def)
            print(f"{prop_name:25} : {type_name:10} ({original_key})")

    print(f"\n合計 {len(property_names)} 個のプロパティ")

    # プロトコル定義を生成
    print("\n=== 生成されるプロトコル定義 ===")
    print("@runtime_checkable")
    print("class XBRLDataProtocol(Protocol):")
    print('    """XBRLデータクラスのプロトコル定義"""')
    print()
    for type_def in type_definitions:
        print(type_def)
    print()
    print("    # メタデータ属性")
    print("    __property_hints__: Dict[str, type]")
    print("    __available_properties__: List[str]")
    print()
    print("    def __getattr__(self, name: str) -> Any:")
    print('        """動的プロパティアクセス用"""')
    print("        ...")


if __name__ == "__main__":
    inspect_properties()
