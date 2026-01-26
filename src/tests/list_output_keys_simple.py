"""既存のJSON出力ファイルからキー一覧を調査するスクリプト

このスクリプトは、既存のJSON出力ファイルから
すべてのデータキーを調査し、一覧を表示します。
"""

import json
from collections import Counter
from pathlib import Path
from typing import Dict, Set


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


def categorize_keys(keys: list) -> Dict[str, list]:
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
    output_dir = Path(__file__).parent / "output"
    
    # JSONファイルを取得
    json_files = sorted(output_dir.glob("*.json"))
    json_files = [f for f in json_files if f.name != "test_summary.json" and f.name != "output_keys_analysis.json"]
    
    if not json_files:
        print("エラー: JSON出力ファイルが見つかりませんでした。")
        return
    
    print("=" * 80)
    print("XBRLModel 出力データキー一覧の調査")
    print("=" * 80)
    print(f"\nJSON出力ファイル数: {len(json_files)}\n")
    
    # 全キーを収集
    all_keys: Set[str] = set()
    key_frequency: Counter = Counter()
    
    # 各JSONファイルからキーを取得
    print("【JSONファイルからキーを取得】")
    print("-" * 80)
    for i, json_file in enumerate(json_files, 1):
        print(f"[{i}/{len(json_files)}] 処理中: {json_file.name}")
        keys = get_keys_from_json(json_file)
        all_keys.update(keys)
        key_frequency.update(keys)
        print(f"  取得キー数: {len(keys)}")
    
    print(f"\n合計ユニークキー数: {len(all_keys)}")
    
    # カテゴリ別に分類
    print("\n【カテゴリ別キー一覧】")
    print("-" * 80)
    categories = categorize_keys(list(all_keys))
    
    for category, keys in categories.items():
        if keys:
            print(f"\n{category} ({len(keys)}個):")
            for key in keys:
                frequency = key_frequency[key]
                percentage = (frequency / len(json_files)) * 100
                print(f"  - {key} (出現: {frequency}/{len(json_files)} = {percentage:.1f}%)")
    
    # ソースファイル関連のキー
    print("\n【ソースファイル関連キー】")
    print("-" * 80)
    source_file_keys = [k for k in all_keys if k.endswith("_source_file")]
    print(f"ソースファイル関連キー ({len(source_file_keys)}個):")
    for key in sorted(source_file_keys):
        frequency = key_frequency[key]
        print(f"  - {key} (出現: {frequency}/{len(json_files)})")
    
    # 結果をJSONファイルに保存
    output_file = output_dir / "output_keys_analysis.json"
    result = {
        "total_unique_keys": len(all_keys),
        "total_json_files": len(json_files),
        "all_keys": sorted(list(all_keys)),
        "categories": {k: sorted(v) for k, v in categories.items()},
        "source_file_keys": sorted(source_file_keys),
        "key_frequency": dict(key_frequency),
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n【結果の保存】")
    print("-" * 80)
    print(f"詳細な結果を保存しました: {output_file}")
    
    # 簡易一覧をテキストファイルにも保存
    txt_output_file = output_dir / "output_keys_list.txt"
    with open(txt_output_file, "w", encoding="utf-8") as f:
        f.write("XBRLModel 出力データキー一覧\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"調査対象JSONファイル数: {len(json_files)}\n")
        f.write(f"合計ユニークキー数: {len(all_keys)}\n\n")
        f.write("全キー一覧（ソート済み）:\n")
        for key in sorted(all_keys):
            frequency = key_frequency[key]
            percentage = (frequency / len(json_files)) * 100
            f.write(f"  - {key} (出現: {frequency}/{len(json_files)} = {percentage:.1f}%)\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("カテゴリ別分類\n")
        f.write("=" * 80 + "\n\n")
        for category, keys in categories.items():
            if keys:
                f.write(f"{category} ({len(keys)}個):\n")
                for key in keys:
                    frequency = key_frequency[key]
                    percentage = (frequency / len(json_files)) * 100
                    f.write(f"  - {key} (出現: {frequency}/{len(json_files)} = {percentage:.1f}%)\n")
                f.write("\n")
    
    print(f"キー一覧を保存しました: {txt_output_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    analyze_output_keys()
