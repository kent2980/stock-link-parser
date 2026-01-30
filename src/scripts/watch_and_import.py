"""データディレクトリを監視して、新しいzipファイルを自動インポートするスクリプト"""

import sys
import time
from pathlib import Path
from typing import Set

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
except ImportError:
    print("エラー: watchdogがインストールされていません。")
    print("以下のコマンドでインストールしてください:")
    print("  uv add watchdog")
    print("  または")
    print("  pip install watchdog")
    sys.exit(1)

from src.config import settings, db_settings
from src.exception.error_handler import get_logger
from src.scripts.import_to_database import DatabaseImporter

logger = get_logger(__name__)


class XBRLFileHandler(FileSystemEventHandler):
    """XBRLファイルの変更を監視するハンドラー"""
    
    def __init__(self, importer: DatabaseImporter, output_path: Path):
        """初期化
        
        Args:
            importer: データベースインポーター
            output_path: 出力ディレクトリのパス
        """
        self.importer = importer
        self.output_path = output_path
        self.processed_files: Set[str] = set()
        self.debounce_time = 5  # ファイルが完全にコピーされるまで待つ秒数
        self.pending_files: dict[str, float] = {}  # {file_path: timestamp}
        
    def on_created(self, event: FileSystemEvent):
        """ファイルが作成されたときの処理"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # zipファイルのみ処理
        if file_path.suffix.lower() != '.zip':
            return
        
        logger.info(f"新しいzipファイルを検出: {file_path.name}")
        
        # デバウンス: ファイルが完全にコピーされるまで待つ
        self.pending_files[str(file_path)] = time.time()
    
    def on_moved(self, event: FileSystemEvent):
        """ファイルが移動されたときの処理（コピー完了時など）"""
        if event.is_directory:
            return
        
        file_path = Path(event.dest_path)
        
        # zipファイルのみ処理
        if file_path.suffix.lower() != '.zip':
            return
        
        logger.info(f"zipファイルの移動を検出: {file_path.name}")
        
        # デバウンス: ファイルが完全にコピーされるまで待つ
        self.pending_files[str(file_path)] = time.time()
    
    def process_pending_files(self):
        """保留中のファイルを処理"""
        current_time = time.time()
        files_to_process = []
        
        for file_path_str, timestamp in list(self.pending_files.items()):
            file_path = Path(file_path_str)
            
            # ファイルが存在し、デバウンス時間が経過しているか確認
            if file_path.exists():
                file_age = current_time - timestamp
                if file_age >= self.debounce_time:
                    # ファイルサイズが安定しているか確認（1秒間変化がない）
                    try:
                        size1 = file_path.stat().st_size
                        time.sleep(1)
                        size2 = file_path.stat().st_size
                        
                        if size1 == size2 and str(file_path) not in self.processed_files:
                            files_to_process.append(file_path)
                            self.processed_files.add(str(file_path))
                    except Exception as e:
                        logger.warning(f"ファイル {file_path.name} のサイズ確認に失敗: {e}")
            else:
                # ファイルが存在しない場合は保留リストから削除
                self.pending_files.pop(file_path_str, None)
        
        # ファイルを処理
        for file_path in files_to_process:
            self.pending_files.pop(str(file_path), None)
            self._import_file(file_path)
    
    def _import_file(self, file_path: Path):
        """ファイルをインポート
        
        Args:
            file_path: インポートするzipファイルのパス
        """
        try:
            logger.info(f"インポートを開始: {file_path.name}")
            result = self.importer.import_xbrl_zip(file_path, self.output_path)
            
            if result["success"]:
                logger.info(
                    f"インポート成功: {file_path.name} "
                    f"(head_item_key: {result['head_item_key']}, "
                    f"テーブル数: {len(result['imported_tables'])})"
                )
            else:
                logger.error(
                    f"インポート失敗: {file_path.name}, "
                    f"エラー数: {len(result['errors'])}"
                )
                for error in result["errors"]:
                    logger.error(f"  - {error.get('category', 'general')}: {error['error']}")
        except Exception as e:
            logger.error(f"インポート処理中にエラーが発生: {file_path.name}, Error: {e}", exc_info=True)


def watch_directory(data_dir: Path, output_path: Path, check_interval: int = 5):
    """ディレクトリを監視して自動インポート
    
    Args:
        data_dir: 監視するデータディレクトリ
        output_path: 出力ディレクトリのパス
        check_interval: 保留ファイルのチェック間隔（秒）
    """
    # データベース設定の確認
    if not db_settings.username or not db_settings.password:
        logger.error("データベースの認証情報が設定されていません。")
        logger.error("XBRL_DB_USERNAME と XBRL_DB_PASSWORD を設定してください。")
        return 1
    
    # データディレクトリの確認
    if not data_dir.exists():
        logger.error(f"データディレクトリが見つかりません: {data_dir}")
        return 1
    
    try:
        # データベースインポーターを作成
        importer = DatabaseImporter()
        
        # 既存のファイルをスキャンしてインポート済みか確認
        logger.info(f"既存のzipファイルをスキャン中: {data_dir}")
        existing_files = list(data_dir.glob("*.zip"))
        logger.info(f"既存のzipファイル数: {len(existing_files)}")
        
        # ファイルハンドラーを作成
        event_handler = XBRLFileHandler(importer, output_path)
        
        # オブザーバーを作成
        observer = Observer()
        observer.schedule(event_handler, str(data_dir), recursive=False)
        observer.start()
        
        logger.info(f"ファイル監視を開始: {data_dir}")
        logger.info("新しいzipファイルが追加されると自動的にインポートされます。")
        logger.info("Ctrl+Cで停止します。")
        
        try:
            # メインループ: 保留ファイルを定期的にチェック
            while True:
                event_handler.process_pending_files()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("監視を停止します...")
        finally:
            observer.stop()
            observer.join()
            logger.info("監視を停止しました。")
        
        return 0
        
    except Exception as e:
        logger.error(f"監視処理中にエラーが発生しました: {e}", exc_info=True)
        return 1


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="データディレクトリを監視して自動インポートします")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="監視するデータディレクトリ（デフォルト: settings.resolved_data_path）",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="出力ディレクトリのパス（デフォルト: settings.resolved_output_path）",
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=5,
        help="保留ファイルのチェック間隔（秒、デフォルト: 5）",
    )
    
    args = parser.parse_args()
    
    # データディレクトリの決定
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        # コンテナ内で実行されている場合（/appが存在する場合）は/app/dataを使用
        if Path("/app").exists():
            data_dir = Path("/app/data")
            logger.info(f"コンテナ内で実行されているため、/app/dataを使用します")
        else:
            data_dir = settings.resolved_data_path
    
    if not data_dir.exists():
        logger.error(f"データディレクトリが見つかりません: {data_dir}")
        return 1
    
    # 出力パスの決定
    if args.output_path:
        output_path = Path(args.output_path)
    else:
        # コンテナ内で実行されている場合（/appが存在する場合）は/app/outputを使用
        if Path("/app").exists():
            output_path = Path("/app/output")
        else:
            output_path = settings.resolved_output_path
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    return watch_directory(data_dir, output_path, args.check_interval)


if __name__ == "__main__":
    exit(main())
