"""XBRLModelからJSON出力をテストするスクリプト

このスクリプトは、src/tests/data配下のzipファイルを5個使用して、
XBRLModelから正しいデータがJSONで出力されるかテストします。
各zipファイルの処理結果は個別のJSONファイルとして保存されます。
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


def test_xbrl_json_output():
    """XBRLModelからJSON出力をテストする"""
    
    # テストデータのディレクトリ
    test_data_dir = Path(__file__).parent / "data"
    output_dir = Path(__file__).parent / "output"
    
    # 出力ディレクトリを作成
    output_dir.mkdir(exist_ok=True)
    
    # テスト用のoutput_path（一時ディレクトリ）
    temp_output_path = output_dir / "temp_output"
    temp_output_path.mkdir(exist_ok=True)
    
    # zipファイルを取得（最初の5個）
    zip_files = sorted(test_data_dir.glob("*.zip"))[:5]
    
    if not zip_files:
        print(f"エラー: {test_data_dir} にzipファイルが見つかりませんでした。")
        return
    
    print(f"テスト対象のzipファイル数: {len(zip_files)}")
    
    results = []
    
    for i, zip_file in enumerate(zip_files, 1):
        print(f"\n[{i}/{len(zip_files)}] 処理中: {zip_file.name}")
        
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
            
            # メタ情報を追加
            output_data = {
                "zip_file_name": zip_file.name,
                "head_item_key": model.head_item_key,
                "xbrl_category": model.xbrl_category,
                "data": data_dict
            }
            
            # JSONファイルとして保存
            output_file = output_dir / f"{zip_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    output_data,
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )
            
            print(f"  ✓ 成功: {output_file.name}")
            
            # 結果を記録
            results.append({
                "zip_file": zip_file.name,
                "output_file": output_file.name,
                "status": "success",
                "head_item_key": model.head_item_key,
                "xbrl_category": model.xbrl_category,
                "data_keys_count": len(data_dict)
            })
            
        except Exception as e:
            error_msg = f"  ✗ エラー: {str(e)}"
            print(error_msg)
            
            # エラー情報を記録
            results.append({
                "zip_file": zip_file.name,
                "status": "error",
                "error": str(e)
            })
    
    # サマリーファイルを作成
    summary_file = output_dir / "test_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_files": len(zip_files),
                "success_count": sum(1 for r in results if r.get("status") == "success"),
                "error_count": sum(1 for r in results if r.get("status") == "error"),
                "results": results
            },
            f,
            ensure_ascii=False,
            indent=2
        )
    
    print(f"\n{'='*60}")
    print(f"テスト完了")
    print(f"  成功: {sum(1 for r in results if r.get('status') == 'success')}件")
    print(f"  エラー: {sum(1 for r in results if r.get('status') == 'error')}件")
    print(f"  サマリーファイル: {summary_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_xbrl_json_output()
