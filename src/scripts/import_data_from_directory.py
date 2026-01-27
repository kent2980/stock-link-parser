"""指定ディレクトリからzipファイルをデータディレクトリにインポートするスクリプト"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import shutil
from typing import List, Optional

from src.config import settings
from src.exception.error_handler import get_logger

logger = get_logger(__name__)


def import_zip_files_from_directory(
    source_dir: Path,
    target_dir: Optional[Path] = None,
    clear_existing: bool = True,
    recursive: bool = True,
) -> dict:
    """指定ディレクトリからzipファイルをインポート
    
    Args:
        source_dir: ソースディレクトリのパス
        target_dir: ターゲットディレクトリのパス（デフォルト: プロジェクトルート/data）
        clear_existing: 既存のzipファイルを削除するかどうか
        recursive: サブディレクトリも検索するかどうか
        
    Returns:
        インポート結果のサマリー
    """
    if target_dir is None:
        # プロジェクトルートのdataディレクトリを使用
        target_dir = settings.project_root / "data"
    
    # ディレクトリを作成
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # ソースディレクトリの確認
    if not source_dir.exists():
        raise FileNotFoundError(f"ソースディレクトリが見つかりません: {source_dir}")
    
    # 既存のzipファイルを削除
    if clear_existing:
        existing_zips = list(target_dir.glob("*.zip"))
        if existing_zips:
            logger.info(f"既存のzipファイルを削除します: {len(existing_zips)}件")
            for zip_file in existing_zips:
                try:
                    zip_file.unlink()
                    logger.debug(f"削除しました: {zip_file.name}")
                except Exception as e:
                    logger.warning(f"削除に失敗しました: {zip_file.name}, Error: {e}")
    
    # ソースディレクトリからzipファイルを再帰的に検索
    zip_files = []
    errors_encountered = []
    
    def search_zip_files_recursive(directory: Path, max_depth: int = None, current_depth: int = 0):
        """再帰的にzipファイルを検索（エラーハンドリング付き）"""
        nonlocal zip_files, errors_encountered
        
        if max_depth is not None and current_depth > max_depth:
            return
        
        try:
            # 現在のディレクトリ内のzipファイルを検索
            try:
                local_zips = list(directory.glob("*.zip"))
                zip_files.extend(local_zips)
                if local_zips:
                    logger.debug(f"Found {len(local_zips)} zip files in {directory}")
            except PermissionError as e:
                errors_encountered.append(f"Permission denied in {directory}: {e}")
                logger.debug(f"Permission denied in {directory}, skipping...")
                return
            except Exception as e:
                errors_encountered.append(f"Error searching {directory}: {e}")
                logger.debug(f"Error in {directory}: {e}")
                return
            
            # サブディレクトリを再帰的に検索
            if recursive:
                try:
                    subdirs = [d for d in directory.iterdir() if d.is_dir()]
                    for subdir in subdirs:
                        # 隠しディレクトリをスキップ
                        if subdir.name.startswith('.'):
                            continue
                        search_zip_files_recursive(subdir, max_depth, current_depth + 1)
                except PermissionError as e:
                    errors_encountered.append(f"Permission denied accessing subdirectories of {directory}: {e}")
                    logger.debug(f"Permission denied accessing subdirectories of {directory}")
                except Exception as e:
                    errors_encountered.append(f"Error accessing subdirectories of {directory}: {e}")
                    logger.debug(f"Error accessing subdirectories of {directory}: {e}")
        
        except Exception as e:
            errors_encountered.append(f"Unexpected error in {directory}: {e}")
            logger.debug(f"Unexpected error in {directory}: {e}")
    
    # os.walkを使ったフォールバック検索（より堅牢）
    def search_with_os_walk(directory: Path):
        """os.walkを使った再帰的検索（フォールバック）"""
        nonlocal zip_files, errors_encountered
        import os
        
        try:
            for root, dirs, files in os.walk(str(directory)):
                # 隠しディレクトリをスキップ
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.endswith('.zip'):
                        zip_path = Path(root) / file
                        try:
                            # ファイルが実際に存在し、読み取り可能か確認
                            if zip_path.exists() and zip_path.is_file():
                                zip_files.append(zip_path)
                        except Exception as e:
                            errors_encountered.append(f"Error accessing {zip_path}: {e}")
        except PermissionError as e:
            errors_encountered.append(f"Permission denied in os.walk: {e}")
            logger.warning(f"os.walkでもアクセス権限エラーが発生しました: {e}")
        except Exception as e:
            errors_encountered.append(f"Error in os.walk: {e}")
            logger.warning(f"os.walkでエラーが発生しました: {e}")
    
    # まずPath.rglobを試す
    if recursive:
        try:
            logger.info(f"再帰的にzipファイルを検索中: {source_dir}")
            zip_files = list(source_dir.rglob("*.zip"))
            logger.info(f"rglobで {len(zip_files)} 件のzipファイルが見つかりました")
            
            # rglobが0件を返した場合、アクセス権限の問題の可能性があるのでフォールバックを試す
            if len(zip_files) == 0:
                logger.info("rglobで0件でした。フォールバック検索を試します...")
                # フォールバック: カスタム再帰検索
                logger.info("カスタム再帰検索を実行中...")
                search_zip_files_recursive(source_dir)
                
                # それでも見つからない場合はos.walkを試す
                if not zip_files:
                    logger.info("os.walkによる検索を試します...")
                    search_with_os_walk(source_dir)
                    
        except (PermissionError, OSError) as e:
            logger.warning(f"rglobでアクセス権限エラーが発生しました。代替方法を試します: {e}")
            # フォールバック: カスタム再帰検索
            logger.info("カスタム再帰検索を実行中...")
            search_zip_files_recursive(source_dir)
            
            # それでも見つからない場合はos.walkを試す
            if not zip_files:
                logger.info("os.walkによる検索を試します...")
                search_with_os_walk(source_dir)
        except Exception as e:
            logger.warning(f"rglobで予期しないエラーが発生しました: {e}")
            # フォールバックを試す
            search_zip_files_recursive(source_dir)
            if not zip_files:
                search_with_os_walk(source_dir)
    else:
        try:
            zip_files = list(source_dir.glob("*.zip"))
        except Exception as e:
            logger.error(f"ディレクトリ検索中にエラーが発生しました: {e}")
            errors_encountered.append(str(e))
    
    # 重複を除去
    zip_files = list(set(zip_files))
    
    # エラーがあった場合は警告を表示
    if errors_encountered:
        logger.warning(f"検索中に {len(errors_encountered)} 件のエラーが発生しました（一部のディレクトリにアクセスできない可能性があります）")
        if len(errors_encountered) <= 5:
            for err in errors_encountered:
                logger.debug(f"  - {err}")
    
    if not zip_files:
        logger.warning(f"ソースディレクトリにzipファイルが見つかりません: {source_dir}")
        if errors_encountered:
            logger.warning(f"検索中に {len(errors_encountered)} 件のエラーが発生しました。アクセス権限の問題の可能性があります。")
        logger.info("ヒント: アクセス権限の問題の可能性があります。macOSの場合は、")
        logger.info("  1. システム環境設定 > セキュリティとプライバシー > プライバシー")
        logger.info("  2. 'フルディスクアクセス'にターミナルまたはPythonを追加")
        logger.info("  または、zipファイルがサブディレクトリにある場合は、そのディレクトリを直接指定してください。")
        return {
            "source_dir": str(source_dir),
            "target_dir": str(target_dir),
            "imported_files": [],
            "skipped_files": [],
            "errors": errors_encountered[:10],  # 最初の10件のエラーのみ
            "total_found": 0,
            "total_imported": 0,
        }
    
    logger.info(f"インポート対象のzipファイル数: {len(zip_files)}")
    
    results = {
        "source_dir": str(source_dir),
        "target_dir": str(target_dir),
        "imported_files": [],
        "skipped_files": [],
        "errors": [],
        "total_found": len(zip_files),
        "total_imported": 0,
    }
    
    # zipファイルをコピー
    for zip_file in zip_files:
        try:
            target_zip = target_dir / zip_file.name
            
            # 既に存在する場合はスキップ
            if target_zip.exists():
                logger.debug(f"既に存在します: {zip_file.name}")
                results["skipped_files"].append({
                    "file": zip_file.name,
                    "reason": "already exists"
                })
                continue
            
            # コピー
            shutil.copy2(zip_file, target_zip)
            logger.info(f"インポートしました: {zip_file.name}")
            results["imported_files"].append({
                "file": zip_file.name,
                "size": zip_file.stat().st_size,
            })
            results["total_imported"] += 1
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {zip_file.name}, Error: {e}"
            logger.error(error_msg)
            results["errors"].append({
                "file": zip_file.name,
                "error": str(e)
            })
    
    logger.info(f"インポート完了: {results['total_imported']}件成功, {len(results['skipped_files'])}件スキップ, {len(results['errors'])}件エラー")
    
    return results


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="指定ディレクトリからzipファイルをインポートします")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="ソースディレクトリのパス（デフォルト: XBRL_XBRL_DATA_PATH環境変数の値）",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="ターゲットディレクトリのパス（デフォルト: プロジェクトルート/data）",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="既存のzipファイルを削除しない",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="サブディレクトリを検索しない",
    )
    
    args = parser.parse_args()
    
    # ソースディレクトリの決定
    if args.source_dir:
        source_dir = Path(args.source_dir)
    else:
        # 環境変数から取得
        source_dir = Path(settings.xbrl_data_path) if settings.xbrl_data_path else None
    
    if source_dir is None or not source_dir.exists():
        logger.error(f"ソースディレクトリが指定されていないか、存在しません: {source_dir}")
        return 1
    
    # インポート実行
    try:
        results = import_zip_files_from_directory(
            source_dir=source_dir,
            target_dir=args.target_dir,
            clear_existing=not args.no_clear,
            recursive=not args.no_recursive,
        )
        
        # 結果を表示
        print("\n" + "=" * 60)
        print("インポート結果サマリー")
        print("=" * 60)
        print(f"ソースディレクトリ: {results['source_dir']}")
        print(f"ターゲットディレクトリ: {results['target_dir']}")
        print(f"見つかったzipファイル数: {results['total_found']}")
        print(f"インポート成功: {results['total_imported']}件")
        print(f"スキップ: {len(results['skipped_files'])}件")
        print(f"エラー: {len(results['errors'])}件")
        
        if results['imported_files']:
            print("\nインポートされたファイル:")
            for item in results['imported_files'][:10]:  # 最初の10件のみ表示
                print(f"  - {item['file']} ({item['size']:,} bytes)")
            if len(results['imported_files']) > 10:
                print(f"  ... 他 {len(results['imported_files']) - 10}件")
        
        if results['errors']:
            print("\nエラーが発生しました:")
            for item in results['errors']:
                if isinstance(item, dict):
                    if 'file' in item:
                        print(f"  - {item['file']}: {item.get('error', 'Unknown error')}")
                    elif 'error' in item:
                        print(f"  - {item['error']}")
                    else:
                        print(f"  - {item}")
                else:
                    print(f"  - {item}")
        
        return 0
        
    except Exception as e:
        logger.error(f"インポート処理中にエラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
