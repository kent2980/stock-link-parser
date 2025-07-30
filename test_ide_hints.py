#!/usr/bin/env python3
"""
型ヒント確認用テストファイル

このファイルでIDEの型ヒント表示を確認してください。
VSCodeやPyCharmで以下の行のitems.を入力した後、
利用可能なプロパティが自動補完で表示されるはずです。
"""

from app.ix_models import XBRLModel
from pathlib import Path


def test_type_hints():
    """型ヒントのテスト"""

    # テスト用のパス（実際には存在しない可能性があります）
    xbrl_path = Path("test.zip")
    output_path = Path("output")

    # XBRLModelのインスタンスを作成
    model = XBRLModel(xbrl_path, output_path)

    # データクラスを取得（型はXBRLDataProtocolとして認識される）
    items = model.get_all_items_as_dataclass()

    # 以下の行でIDEの自動補完を確認してください
    # items. と入力すると、利用可能なプロパティが表示されるはずです

    # 例：
    file_path = items.ix_file_path  # ← 型ヒント: List[Dict[str, Any]]
    head_title = items.ix_head_title  # ← 型ヒント: List[Dict[str, Any]]
    cal_arcs = items.cal_link_arcs  # ← 型ヒント: List[Dict[str, Any]]

    # メタデータにもアクセス可能
    available_props = items.__available_properties__
    property_hints = items.__property_hints__

    print("型ヒントが正常に機能しています。")
    print(f"利用可能なプロパティ数: {len(available_props)}")


if __name__ == "__main__":
    # このファイルは実行用ではなく、IDE での型ヒント確認用です
    print("このファイルはIDEでの型ヒント確認用です。")
    print("items.を入力した後に自動補完を確認してください。")
