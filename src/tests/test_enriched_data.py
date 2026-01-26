"""統合されたデータ（ix_non_fraction_enriched, ix_non_numeric_enriched）のテスト"""

import json
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ix_models.xbrl_model import XBRLModel


def test_enriched_data():
    """統合されたデータが正しく生成されるかテスト"""
    test_data_dir = Path(__file__).parent / "data"
    output_dir = Path(__file__).parent / "output"
    temp_output_path = output_dir / "temp_output"
    
    # 最初のzipファイルを使用
    zip_files = sorted(test_data_dir.glob("*.zip"))
    if not zip_files:
        print("エラー: テストデータが見つかりませんでした。")
        return
    
    zip_file = zip_files[0]
    print(f"テスト対象: {zip_file.name}\n")
    
    # XBRLModelのインスタンスを作成
    model = XBRLModel(
        xbrl_zip_path=zip_file,
        output_path=temp_output_path
    )
    
    # データクラスを取得
    data_class = model.get_all_items_as_dataclass()
    
    # 統合されたデータを確認
    print("【統合されたデータの確認】")
    print("-" * 80)
    
    # ix_non_fraction_enriched
    if hasattr(data_class, "ix_non_fraction_enriched"):
        enriched_fraction = getattr(data_class, "ix_non_fraction_enriched")
        print(f"ix_non_fraction_enriched: {len(enriched_fraction)}件")
        
        if enriched_fraction:
            # 最初のアイテムを表示
            sample = enriched_fraction[0]
            print("\nサンプル（最初のアイテム）:")
            print(json.dumps(sample, indent=2, ensure_ascii=False)[:2000])
            
            # ラベルが統合されているか確認
            if "labels" in sample:
                print(f"\n✓ ラベルが統合されています: {len(sample['labels'])}件")
            else:
                print("\n✗ ラベルが統合されていません")
            
            # 計算リンクが統合されているか確認
            if "calculation_links" in sample:
                print(f"✓ 計算リンクが統合されています: {len(sample['calculation_links'])}件")
            else:
                print("✗ 計算リンクが統合されていません")
    else:
        print("✗ ix_non_fraction_enriched が見つかりません")
    
    print("\n" + "-" * 80)
    
    # ix_non_numeric_enriched
    if hasattr(data_class, "ix_non_numeric_enriched"):
        enriched_numeric = getattr(data_class, "ix_non_numeric_enriched")
        print(f"ix_non_numeric_enriched: {len(enriched_numeric)}件")
        
        if enriched_numeric:
            # 最初のアイテムを表示
            sample = enriched_numeric[0]
            print("\nサンプル（最初のアイテム）:")
            print(json.dumps(sample, indent=2, ensure_ascii=False)[:2000])
            
            # ラベルが統合されているか確認
            if "labels" in sample:
                print(f"\n✓ ラベルが統合されています: {len(sample['labels'])}件")
            else:
                print("\n✗ ラベルが統合されていません")
    else:
        print("✗ ix_non_numeric_enriched が見つかりません")
    
    # 既存のキーが保持されているか確認
    print("\n【既存キーの確認】")
    print("-" * 80)
    if hasattr(data_class, "ix_non_fraction"):
        print("✓ ix_non_fraction が保持されています")
    else:
        print("✗ ix_non_fraction が見つかりません")
    
    if hasattr(data_class, "ix_non_numeric"):
        print("✓ ix_non_numeric が保持されています")
    else:
        print("✗ ix_non_numeric が見つかりません")
    
    # 新しいキーがget_all_items_keysに含まれているか確認
    print("\n【キー一覧の確認】")
    print("-" * 80)
    keys = model.get_all_items_keys()
    if "ix_non_fraction_enriched" in keys:
        print("✓ ix_non_fraction_enriched がキー一覧に含まれています")
    else:
        print("✗ ix_non_fraction_enriched がキー一覧に含まれていません")
    
    if "ix_non_numeric_enriched" in keys:
        print("✓ ix_non_numeric_enriched がキー一覧に含まれています")
    else:
        print("✗ ix_non_numeric_enriched がキー一覧に含まれていません")


if __name__ == "__main__":
    test_enriched_data()
