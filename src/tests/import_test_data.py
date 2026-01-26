"""テストデータをインポートするスクリプト

src/tests/output/配下のJSONファイルを読み込んで、
FastAPIアプリケーションで利用できるようにします。
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.exception.error_handler import ErrorContext, get_logger

logger = get_logger(__name__)


def load_json_file(json_path: Path) -> Dict[str, Any]:
    """JSONファイルを読み込む"""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        with ErrorContext("load_json_file", {"json_path": str(json_path), "error": str(e)}):
            logger.error(f"Failed to load JSON file: {json_path}")
            raise


def import_test_data_to_data_dir(
    json_dir: Path = None,
    target_data_dir: Path = None,
    copy_zip_files: bool = True,
) -> Dict[str, Any]:
    """テストデータをデータディレクトリにインポート

    Args:
        json_dir: JSONファイルが格納されているディレクトリ（デフォルト: src/tests/output）
        target_data_dir: インポート先のデータディレクトリ（デフォルト: settings.resolved_data_path）
        copy_zip_files: zipファイルもコピーするかどうか

    Returns:
        インポート結果のサマリー
    """
    if json_dir is None:
        json_dir = Path(__file__).parent / "output"

    if target_data_dir is None:
        target_data_dir = Path(settings.resolved_data_path)

    # ディレクトリを作成
    target_data_dir.mkdir(parents=True, exist_ok=True)

    # JSONファイルを取得
    json_files = sorted(json_dir.glob("*.json"))
    # test_summary.jsonとenrichedファイルは除外
    json_files = [
        f
        for f in json_files
        if f.name != "test_summary.json"
        and not f.name.endswith("_enriched.json")
        and not f.name.startswith("key_")
        and not f.name.startswith("output_keys_")
        and f.name != "web_app_formatted_sample.json"
    ]

    logger.info(f"インポート対象のJSONファイル数: {len(json_files)}")

    results = {
        "imported_files": [],
        "skipped_files": [],
        "errors": [],
        "total": len(json_files),
    }

    # テストデータのディレクトリ
    test_data_dir = Path(__file__).parent / "data"

    for json_file in json_files:
        try:
            # JSONファイルを読み込む
            data = load_json_file(json_file)

            # zip_file_nameを取得
            zip_file_name = data.get("zip_file_name")
            if not zip_file_name:
                logger.warning(f"zip_file_nameが見つかりません: {json_file.name}")
                results["skipped_files"].append(
                    {"json_file": json_file.name, "reason": "zip_file_name not found"}
                )
                continue

            # 対応するzipファイルを探す
            zip_file = test_data_dir / zip_file_name
            if not zip_file.exists():
                logger.warning(f"zipファイルが見つかりません: {zip_file}")
                results["skipped_files"].append(
                    {"json_file": json_file.name, "zip_file": zip_file_name, "reason": "zip file not found"}
                )
                continue

            # zipファイルをコピー
            if copy_zip_files:
                import shutil

                target_zip = target_data_dir / zip_file_name
                if not target_zip.exists():
                    shutil.copy2(zip_file, target_zip)
                    logger.info(f"zipファイルをコピーしました: {target_zip}")
                else:
                    logger.info(f"zipファイルは既に存在します: {target_zip}")

            results["imported_files"].append(
                {
                    "json_file": json_file.name,
                    "zip_file": zip_file_name,
                    "head_item_key": data.get("head_item_key"),
                    "xbrl_category": data.get("xbrl_category"),
                }
            )

        except Exception as e:
            error_msg = f"エラーが発生しました: {json_file.name}, Error: {e}"
            logger.error(error_msg)
            results["errors"].append({"json_file": json_file.name, "error": str(e)})

    logger.info(f"インポート完了: {len(results['imported_files'])}件成功, {len(results['errors'])}件エラー")
    return results


def import_test_data_to_fastapi_cache(
    json_dir: Path = None,
    fastapi_app_module: str = "src.api.fastapi_app",
) -> Dict[str, Any]:
    """テストデータをFastAPIアプリケーションのキャッシュにインポート

    Args:
        json_dir: JSONファイルが格納されているディレクトリ
        fastapi_app_module: FastAPIアプリケーションモジュール名

    Returns:
        インポート結果のサマリー
    """
    if json_dir is None:
        json_dir = Path(__file__).parent / "output"

    # JSONファイルを取得
    json_files = sorted(json_dir.glob("*.json"))
    # test_summary.jsonとenrichedファイルは除外
    json_files = [
        f
        for f in json_files
        if f.name != "test_summary.json"
        and not f.name.endswith("_enriched.json")
        and not f.name.startswith("key_")
        and not f.name.startswith("output_keys_")
        and f.name != "web_app_formatted_sample.json"
    ]

    logger.info(f"FastAPIキャッシュにインポート対象のJSONファイル数: {len(json_files)}")

    results = {
        "imported_files": [],
        "skipped_files": [],
        "errors": [],
        "total": len(json_files),
    }

    # FastAPIアプリケーションモジュールを動的にインポート
    try:
        import importlib

        app_module = importlib.import_module(fastapi_app_module)
        # キャッシュにアクセス（存在しない場合は作成）
        if not hasattr(app_module, "_xbrl_model_cache"):
            logger.warning("FastAPIアプリケーションのキャッシュが見つかりません")
            return results

        cache = app_module._xbrl_model_cache

        for json_file in json_files:
            try:
                # JSONファイルを読み込む
                data = load_json_file(json_file)

                head_item_key = data.get("head_item_key")
                if not head_item_key:
                    logger.warning(f"head_item_keyが見つかりません: {json_file.name}")
                    results["skipped_files"].append(
                        {"json_file": json_file.name, "reason": "head_item_key not found"}
                    )
                    continue

                # テストデータのディレクトリからzipファイルを探す
                test_data_dir = Path(__file__).parent / "data"
                zip_file_name = data.get("zip_file_name")
                if not zip_file_name:
                    logger.warning(f"zip_file_nameが見つかりません: {json_file.name}")
                    results["skipped_files"].append(
                        {"json_file": json_file.name, "reason": "zip_file_name not found"}
                    )
                    continue

                zip_file = test_data_dir / zip_file_name
                if not zip_file.exists():
                    logger.warning(f"zipファイルが見つかりません: {zip_file}")
                    results["skipped_files"].append(
                        {"json_file": json_file.name, "zip_file": zip_file_name, "reason": "zip file not found"}
                    )
                    continue

                # XBRLModelを作成してキャッシュに追加
                from src.ix_models.xbrl_model import XBRLModel

                output_path = Path(settings.resolved_output_path)
                model = XBRLModel(zip_file, output_path)
                cache[head_item_key] = model

                results["imported_files"].append(
                    {
                        "json_file": json_file.name,
                        "head_item_key": head_item_key,
                        "xbrl_category": data.get("xbrl_category"),
                    }
                )

            except Exception as e:
                error_msg = f"エラーが発生しました: {json_file.name}, Error: {e}"
                logger.error(error_msg)
                results["errors"].append({"json_file": json_file.name, "error": str(e)})

        logger.info(
            f"FastAPIキャッシュへのインポート完了: {len(results['imported_files'])}件成功, {len(results['errors'])}件エラー"
        )

    except ImportError as e:
        logger.error(f"FastAPIアプリケーションモジュールのインポートに失敗しました: {e}")
        results["errors"].append({"error": f"Module import failed: {e}"})

    return results


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description="テストデータをインポートします")
    parser.add_argument(
        "--target",
        choices=["data_dir", "fastapi_cache", "both"],
        default="data_dir",
        help="インポート先 (data_dir: データディレクトリ, fastapi_cache: FastAPIキャッシュ, both: 両方)",
    )
    parser.add_argument(
        "--json-dir",
        type=Path,
        default=None,
        help="JSONファイルが格納されているディレクトリ（デフォルト: src/tests/output）",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="インポート先のデータディレクトリ（デフォルト: settings.resolved_data_path）",
    )
    parser.add_argument(
        "--no-copy-zip",
        action="store_true",
        help="zipファイルをコピーしない",
    )

    args = parser.parse_args()

    results = {}

    if args.target in ["data_dir", "both"]:
        logger.info("データディレクトリへのインポートを開始します...")
        results["data_dir"] = import_test_data_to_data_dir(
            json_dir=args.json_dir,
            target_data_dir=args.data_dir,
            copy_zip_files=not args.no_copy_zip,
        )

    if args.target in ["fastapi_cache", "both"]:
        logger.info("FastAPIキャッシュへのインポートを開始します...")
        results["fastapi_cache"] = import_test_data_to_fastapi_cache(json_dir=args.json_dir)

    # 結果を表示
    print("\n" + "=" * 60)
    print("インポート結果サマリー")
    print("=" * 60)

    for target, result in results.items():
        print(f"\n[{target}]")
        print(f"  総ファイル数: {result.get('total', 0)}")
        print(f"  インポート成功: {len(result.get('imported_files', []))}件")
        print(f"  スキップ: {len(result.get('skipped_files', []))}件")
        print(f"  エラー: {len(result.get('errors', []))}件")

        if result.get("imported_files"):
            print("\n  インポート成功ファイル:")
            for item in result["imported_files"]:
                print(f"    - {item.get('json_file')} (head_item_key: {item.get('head_item_key')})")

        if result.get("errors"):
            print("\n  エラー:")
            for item in result["errors"]:
                print(f"    - {item.get('json_file')}: {item.get('error')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
