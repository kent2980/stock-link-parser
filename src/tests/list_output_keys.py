"""XBRLModelから出力されるデータキー一覧を調査するスクリプト

このスクリプトは、テストデータを使用してXBRLModelから出力される
すべてのデータキーを調査し、一覧を表示します。
"""

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ix_models.xbrl_model import XBRLModel


def get_keys_from_model(zip_file: Path, output_path: Path) -> Set[str]:
    """XBRLModelからキー一覧を取得する"""
    try:
        model = XBRLModel(xbrl_zip_path=zip_file, output_path=output_path)
        keys = model.get_all_items_keys()
        return set(keys)
    except Exception as e:
        print(f"  エラー: {zip_file.name} の処理中にエラーが発生: {e}")
        return set()


def get_keys_from_json(json_file: Path) -> Set[str]:
    """JSONファイルからキー一覧を取得する"""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # dataキーの中のキーを取得
        if "data" in data and isinstance(data["data"], dict):
            return set(data["data"].keys())
        return set()
    except Exception as e:
        print(f"  エラー: {json_file.name} の読み込み中にエラーが発生: {e}")
        return set()


def categorize_keys(keys: List[str]) -> Dict[str, List[str]]:
    """キーをカテゴリ別に分類する"""
    categories = {
        "ix_": [],
        "cal_": [],
        "def_": [],
        "pre_": [],
        "lab_": [],
        "sc_": [],
        "qualitative_": [],
        "href_": [],
        "その他": [],
    }
    
    for key in sorted(keys):
        categorized = False
        for prefix in ["ix_", "cal_", "def_", "pre_", "lab_", "sc_", "qualitative_", "href_"]:
            if key.startswith(prefix):
                categories[prefix].append(key)
                categorized = True
                break
        
        if not categorized:
            categories["その他"].append(key)
    
    return categories


def analyze_output_keys():
    """出力データキー一覧を調査する"""
    test_data_dir = Path(__file__).parent / "data"
    output_dir = Path(__file__).parent / "output"
    temp_output_path = output_dir / "temp_output"
    
    # zipファイルを取得
    zip_files = sorted(test_data_dir.glob("*.zip"))
    
    if not zip_files:
        print("エラー: テストデータが見つかりませんでした。")
        return
    
    print("=" * 80)
    print("XBRLModel 出力データキー一覧の調査")
    print("=" * 80)
    print(f"\nテストデータファイル数: {len(zip_files)}\n")
    
    # 全キーを収集
    all_keys_from_models: Set[str] = set()
    all_keys_from_json: Set[str] = set()
    key_frequency: Counter = Counter()
    
    # 各ファイルからキーを取得
    print("【1. XBRLModelから直接取得】")
    print("-" * 80)
    for i, zip_file in enumerate(zip_files, 1):
        print(f"[{i}/{len(zip_files)}] 処理中: {zip_file.name}")
        keys = get_keys_from_model(zip_file, temp_output_path)
        all_keys_from_models.update(keys)
        key_frequency.update(keys)
        print(f"  取得キー数: {len(keys)}")
    
    print(f"\n合計ユニークキー数: {len(all_keys_from_models)}")
    
    # JSONファイルからもキーを取得
    print("\n【2. 出力JSONファイルから取得】")
    print("-" * 80)
    json_files = sorted(output_dir.glob("*.json"))
    json_files = [f for f in json_files if f.name != "test_summary.json"]
    
    if json_files:
        for i, json_file in enumerate(json_files, 1):
            print(f"[{i}/{len(json_files)}] 処理中: {json_file.name}")
            keys = get_keys_from_json(json_file)
            all_keys_from_json.update(keys)
            print(f"  取得キー数: {len(keys)}")
        
        print(f"\n合計ユニークキー数: {len(all_keys_from_json)}")
    else:
        print("JSONファイルが見つかりませんでした。")
    
    # キーの比較
    print("\n【3. キーの比較】")
    print("-" * 80)
    only_in_model = all_keys_from_models - all_keys_from_json
    only_in_json = all_keys_from_json - all_keys_from_models
    common_keys = all_keys_from_models & all_keys_from_json
    
    print(f"XBRLModelのみ: {len(only_in_model)}個")
    if only_in_model:
        print(f"  {sorted(only_in_model)}")
    
    print(f"\nJSONのみ: {len(only_in_json)}個")
    if only_in_json:
        print(f"  {sorted(only_in_json)}")
    
    print(f"\n共通: {len(common_keys)}個")
    
    # カテゴリ別に分類
    print("\n【4. カテゴリ別キー一覧】")
    print("-" * 80)
    categories = categorize_keys(list(all_keys_from_models))
    
    for category, keys in categories.items():
        if keys:
            print(f"\n{category} ({len(keys)}個):")
            for key in keys:
                frequency = key_frequency[key]
                print(f"  - {key} (出現回数: {frequency}/{len(zip_files)})")
    
    # ソースファイル関連のキー
    print("\n【5. ソースファイル関連キー】")
    print("-" * 80)
    source_file_keys = [k for k in all_keys_from_models if k.endswith("_source_file")]
    print(f"ソースファイル関連キー ({len(source_file_keys)}個):")
    for key in sorted(source_file_keys):
        print(f"  - {key}")
    
    # JSON版プロパティ
    print("\n【6. JSON版プロパティ（_jsonサフィックス）】")
    print("-" * 80)
    json_keys = [k for k in all_keys_from_models if k.endswith("_json")]
    if json_keys:
        print(f"JSON版プロパティ ({len(json_keys)}個):")
        for key in sorted(json_keys):
            print(f"  - {key}")
    else:
        print("JSON版プロパティは含まれていません（get_all_items_keys()では除外されます）")
    
    # 結果をJSONファイルに保存
    output_file = output_dir / "output_keys_analysis.json"
    result = {
        "total_unique_keys": len(all_keys_from_models),
        "keys_from_model": sorted(list(all_keys_from_models)),
        "keys_from_json": sorted(list(all_keys_from_json)) if json_files else [],
        "only_in_model": sorted(list(only_in_model)),
        "only_in_json": sorted(list(only_in_json)),
        "common_keys": sorted(list(common_keys)),
        "categories": {k: sorted(v) for k, v in categories.items()},
        "source_file_keys": sorted(source_file_keys),
        "key_frequency": dict(key_frequency),
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n【7. 結果の保存】")
    print("-" * 80)
    print(f"詳細な結果を保存しました: {output_file}")
    
    # 簡易一覧をテキストファイルにも保存
    txt_output_file = output_dir / "output_keys_list.txt"
    with open(txt_output_file, "w", encoding="utf-8") as f:
        f.write("XBRLModel 出力データキー一覧\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"合計キー数: {len(all_keys_from_models)}\n\n")
        f.write("全キー一覧（ソート済み）:\n")
        for key in sorted(all_keys_from_models):
            f.write(f"  - {key}\n")
    
    print(f"キー一覧を保存しました: {txt_output_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    analyze_output_keys()
