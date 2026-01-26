"""Webアプリ向けデータフォーマットのテスト"""

import json
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.web_app_formatter import format_for_web_app, format_list_for_web_app


def test_web_app_format():
    """Webアプリ向けフォーマットのテスト"""
    json_file = Path(__file__).parent / "output" / "081220250911556517_enriched.json"
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # ix_non_fraction_enrichedのサンプルを取得
    if "data" in data and "ix_non_fraction_enriched" in data["data"]:
        enriched = data["data"]["ix_non_fraction_enriched"]
        if enriched:
            sample = enriched[0]
            
            print("=== 元のデータ構造 ===")
            print(json.dumps(sample, indent=2, ensure_ascii=False)[:1000])
            print("\n")
            
            # ix_contextデータを取得
            context_data = None
            if "data" in data and "ix_context" in data["data"]:
                context_data = data["data"]["ix_context"]
            
            # Webアプリ向けにフォーマット
            formatted = format_for_web_app(sample, context_data)
            
            print("=== Webアプリ向けフォーマット ===")
            print(json.dumps(formatted, indent=2, ensure_ascii=False))
            
            # 出力ファイルに保存
            output_file = Path(__file__).parent / "output" / "web_app_formatted_sample.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(formatted, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ フォーマット済みデータを保存しました: {output_file}")
            
            # 複数アイテムのフォーマットテスト
            formatted_list = format_list_for_web_app(enriched[:5], context_data)
            print(f"\n✓ リストフォーマット: {len(formatted_list)}件")


if __name__ == "__main__":
    test_web_app_format()
