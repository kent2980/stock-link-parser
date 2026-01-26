"""出力ファイルに含まれているキーと、XBRLModelから取得可能なキーを比較するスクリプト"""

import json
import sys
from pathlib import Path
from typing import Dict, Set

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ix_models.xbrl_model import XBRLModel


def get_keys_from_json_file(json_file: Path) -> Set[str]:
    """JSONファイルからdataキー配下のキーを取得する"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "data" in data and isinstance(data["data"], dict):
            return set(data["data"].keys())
    return set()


def get_expected_keys_from_model(zip_file: Path, output_path: Path) -> Set[str]:
    """XBRLModelから取得可能なキーを取得する"""
    try:
        model = XBRLModel(xbrl_zip_path=zip_file, output_path=output_path)
        # get_all_items_keys()を使用してキーを取得
        keys = model.get_all_items_keys()
        return set(keys)
    except Exception as e:
        print(f"  エラー: {zip_file.name} の処理中にエラーが発生: {e}")
        return set()


def check_missing_keys():
    """出力ファイルとXBRLModelから取得可能なキーを比較する"""
    
    output_dir = Path(__file__).parent / "output"
    test_data_dir = Path(__file__).parent / "data"
    temp_output_path = output_dir / "temp_output"
    
    # JSONファイルを取得
    json_files = sorted(output_dir.glob("*.json"))
    json_files = [f for f in json_files if f.name != "test_summary.json"]
    
    if not json_files:
        print("エラー: 出力ファイルが見つかりませんでした。")
        return
    
    print(f"確認対象のJSONファイル数: {len(json_files)}\n")
    
    all_missing_keys: Dict[str, Set[str]] = {}
    all_extra_keys: Dict[str, Set[str]] = {}
    
    for json_file in json_files:
        print(f"確認中: {json_file.name}")
        
        # JSONファイルからキーを取得
        json_keys = get_keys_from_json_file(json_file)
        
        # 対応するzipファイルを探す
        zip_file_name = json_file.stem + ".zip"
        zip_file = test_data_dir / zip_file_name
        
        if not zip_file.exists():
            print(f"  警告: 対応するzipファイルが見つかりません: {zip_file_name}")
            continue
        
        # XBRLModelから期待されるキーを取得
        expected_keys = get_expected_keys_from_model(zip_file, temp_output_path)
        
        if not expected_keys:
            print(f"  警告: 期待されるキーを取得できませんでした")
            continue
        
        # 欠けているキーを確認
        missing_keys = expected_keys - json_keys
        extra_keys = json_keys - expected_keys
        
        if missing_keys:
            all_missing_keys[json_file.name] = missing_keys
            print(f"  ✗ 欠けているキー ({len(missing_keys)}個): {sorted(missing_keys)}")
        else:
            print(f"  ✓ すべてのキーが含まれています")
        
        if extra_keys:
            all_extra_keys[json_file.name] = extra_keys
            print(f"  ⚠ 予期しないキー ({len(extra_keys)}個): {sorted(extra_keys)}")
        
        print()
    
    # サマリーを表示
    print("=" * 60)
    print("サマリー")
    print("=" * 60)
    
    if all_missing_keys:
        print(f"\n欠けているキーがあるファイル: {len(all_missing_keys)}個")
        for file_name, keys in all_missing_keys.items():
            print(f"  {file_name}: {sorted(keys)}")
        
        # すべてのファイルで共通して欠けているキー
        if len(all_missing_keys) > 1:
            common_missing = set.intersection(*all_missing_keys.values())
            if common_missing:
                print(f"\nすべてのファイルで共通して欠けているキー: {sorted(common_missing)}")
    else:
        print("\n✓ すべてのファイルに必要なキーが含まれています")
    
    if all_extra_keys:
        print(f"\n予期しないキーがあるファイル: {len(all_extra_keys)}個")
        for file_name, keys in all_extra_keys.items():
            print(f"  {file_name}: {sorted(keys)}")
    
    # 詳細な比較レポートをJSONファイルに保存
    report_file = output_dir / "key_comparison_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "missing_keys": {k: sorted(v) for k, v in all_missing_keys.items()},
                "extra_keys": {k: sorted(v) for k, v in all_extra_keys.items()},
                "common_missing_keys": sorted(set.intersection(*all_missing_keys.values())) if len(all_missing_keys) > 1 else []
            },
            f,
            ensure_ascii=False,
            indent=2
        )
    
    print(f"\n詳細レポート: {report_file}")


if __name__ == "__main__":
    check_missing_keys()
