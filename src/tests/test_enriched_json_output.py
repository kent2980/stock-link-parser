"""統合されたデータを含むJSON出力のテスト

統合されたix_non_fraction_enrichedとix_non_numeric_enrichedを含む
JSONファイルを生成します。
"""

import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ix_models.xbrl_model import XBRLModel


def dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """データクラスを辞書に変換する
    
    Args:
        obj: データクラスのインスタンス
        
    Returns:
        辞書形式のデータ
    """
    # データクラスの場合はasdictを使用
    if is_dataclass(obj):
        result = asdict(obj)
        # _jsonサフィックスが付いたプロパティを除外（元のプロパティのみを保持）
        return {k: v for k, v in result.items() if not k.endswith("_json")}
    
    # データクラスでない場合は、利用可能なプロパティを取得
    result = {}
    if hasattr(obj, "__available_properties__"):
        for prop_name in obj.__available_properties__:
            # _jsonサフィックスが付いていないプロパティのみを取得（JSON版は除外）
            if not prop_name.endswith("_json"):
                try:
                    value = getattr(obj, prop_name)
                    result[prop_name] = value
                except AttributeError:
                    pass
    
    return result


def test_enriched_json_output():
    """統合されたデータを含むJSONファイルを生成"""
    test_data_dir = Path(__file__).parent / "data"
    output_dir = Path(__file__).parent / "output"
    temp_output_path = output_dir / "temp_output"
    
    # zipファイルを取得（最初の1つを使用）
    zip_files = sorted(test_data_dir.glob("*.zip"))
    if not zip_files:
        print("エラー: テストデータが見つかりませんでした。")
        return
    
    zip_file = zip_files[0]
    print(f"処理対象: {zip_file.name}\n")
    
    try:
        # XBRLModelのインスタンスを作成
        model = XBRLModel(
            xbrl_zip_path=zip_file,
            output_path=temp_output_path
        )
        
        # データクラスを取得
        data_class = model.get_all_items_as_dataclass()
        
        # データクラスを辞書に変換
        data_dict = dataclass_to_dict(data_class)
        
        # 統合されたデータの情報を追加
        enriched_info = {}
        if "ix_non_fraction_enriched" in data_dict:
            enriched_info["ix_non_fraction_enriched"] = {
                "count": len(data_dict["ix_non_fraction_enriched"]),
                "sample_count": min(3, len(data_dict["ix_non_fraction_enriched"])),
            }
        
        if "ix_non_numeric_enriched" in data_dict:
            enriched_info["ix_non_numeric_enriched"] = {
                "count": len(data_dict["ix_non_numeric_enriched"]),
                "sample_count": min(3, len(data_dict["ix_non_numeric_enriched"])),
            }
        
        # メタ情報を追加
        output_data = {
            "zip_file_name": zip_file.name,
            "head_item_key": model.head_item_key,
            "xbrl_category": model.xbrl_category,
            "enriched_data_info": enriched_info,
            "data": data_dict
        }
        
        # JSONファイルとして保存
        output_file = output_dir / f"{zip_file.stem}_enriched.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                output_data,
                f,
                ensure_ascii=False,
                indent=2,
                default=str
            )
        
        print(f"✓ 成功: {output_file.name}")
        print(f"  ファイルサイズ: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        # 統合されたデータのサマリーを表示
        if "ix_non_fraction_enriched" in data_dict:
            enriched_fraction = data_dict["ix_non_fraction_enriched"]
            print(f"\n【ix_non_fraction_enriched】")
            print(f"  総件数: {len(enriched_fraction)}")
            if enriched_fraction:
                sample = enriched_fraction[0]
                labels_count = len(sample.get("labels", []))
                calc_count = len(sample.get("calculation_links", []))
                def_count = len(sample.get("definition_links", []))
                pre_count = len(sample.get("presentation_links", []))
                print(f"  サンプル（最初のアイテム）:")
                print(f"    - ラベル数: {labels_count}")
                print(f"    - 計算リンク数: {calc_count}")
                print(f"    - 定義リンク数: {def_count}")
                print(f"    - 表示リンク数: {pre_count}")
        
        if "ix_non_numeric_enriched" in data_dict:
            enriched_numeric = data_dict["ix_non_numeric_enriched"]
            print(f"\n【ix_non_numeric_enriched】")
            print(f"  総件数: {len(enriched_numeric)}")
            if enriched_numeric:
                sample = enriched_numeric[0]
                labels_count = len(sample.get("labels", []))
                calc_count = len(sample.get("calculation_links", []))
                def_count = len(sample.get("definition_links", []))
                pre_count = len(sample.get("presentation_links", []))
                print(f"  サンプル（最初のアイテム）:")
                print(f"    - ラベル数: {labels_count}")
                print(f"    - 計算リンク数: {calc_count}")
                print(f"    - 定義リンク数: {def_count}")
                print(f"    - 表示リンク数: {pre_count}")
        
        print(f"\n出力ファイル: {output_file}")
        
    except Exception as e:
        error_msg = f"✗ エラー: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_enriched_json_output()
