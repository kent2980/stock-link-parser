"""XBRLデータをデータベースにインポートするスクリプト"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from src.config import settings, db_settings
try:
    from src.connect.postgre_sql_connector import PostgreSqlConnector
except ImportError as e:
    print("エラー: psycopg2がインストールされていません。")
    print("以下のコマンドでインストールしてください:")
    print("  uv add psycopg2-binary")
    print("  または")
    print("  pip install psycopg2-binary")
    sys.exit(1)
from src.ix_models.xbrl_model import XBRLModel
from src.exception.error_handler import get_logger
from src.utils.utils import Utils
from src.utils.qualitative_utils import format_qualitative_info_hierarchical

logger = get_logger(__name__)


class DatabaseImporter:
    """XBRLデータをデータベースにインポートするクラス"""
    
    def __init__(self, host_override: Optional[str] = None):
        """データベース接続を初期化
        
        Args:
            host_override: ホスト名のオーバーライド（Noneの場合は設定値を使用）
        """
        # ホスト名の決定（ローカル環境ではpostgresをlocalhostにフォールバック）
        db_host = host_override or db_settings.host
        
        # postgresというホスト名が解決できない場合（ローカル環境）はlocalhostを試す
        if db_host == "postgres":
            import socket
            try:
                socket.gethostbyname("postgres")
                # postgresが解決できる場合はそのまま使用（コンテナ環境）
            except socket.gaierror:
                # postgresが解決できない場合はlocalhostを使用（ローカル環境）
                logger.info("postgresホスト名が解決できないため、localhostを使用します")
                db_host = "localhost"
        
        self.connector = PostgreSqlConnector(
            host=db_host,
            port=db_settings.port,
            database=db_settings.database,
            user=db_settings.username,
            password=db_settings.password,
        )
        self.connector.connect()
        
        if not self.connector.connection:
            # 接続に失敗した場合、postgresからlocalhostにフォールバックを試す
            if db_host == "postgres":
                logger.warning("postgresへの接続に失敗しました。localhostを試します...")
                self.connector = PostgreSqlConnector(
                    host="localhost",
                    port=db_settings.port,
                    database=db_settings.database,
                    user=db_settings.username,
                    password=db_settings.password,
                )
                self.connector.connect()
            
            if not self.connector.connection:
                raise ConnectionError("データベースに接続できませんでした。設定を確認してください。")
        
        logger.info(f"データベース接続が確立されました (host={db_host})")
    
    def __del__(self):
        """データベース接続を閉じる"""
        if hasattr(self, 'connector'):
            self.connector.disconnect()
    
    def import_xbrl_zip(self, zip_path: Path, output_path: Path) -> Dict[str, Any]:
        """単一のXBRL zipファイルをデータベースにインポート
        
        Args:
            zip_path: zipファイルのパス
            output_path: 出力ディレクトリのパス
            
        Returns:
            インポート結果のサマリー
        """
        result = {
            "zip_file": str(zip_path),
            "head_item_key": None,
            "imported_tables": [],
            "errors": [],
            "success": False,
        }
        
        try:
            # head_item_keyを生成
            head_item_key = str(Utils.string_to_uuid(zip_path.name))
            result["head_item_key"] = head_item_key
            
            # XBRLModelのインスタンスを作成
            model = XBRLModel(zip_path, output_path)
            
            # データを取得
            items = model.get_all_items()
            data_dict = {item.key: item.item for item in items}
            
            # 除外カテゴリ（統合元データ、リンクデータ、スキーマ情報）
            # 注意: ix_non_fraction_enriched と ix_non_numeric_enriched は含める
            excluded_categories = [
                "ix_non_fraction",  # 統合元データ（_enriched版を使用）
                "ix_non_numeric",   # 統合元データ（_enriched版を使用）
                "cal_link_arcs",
                "cal_link_locs",
                "cal_link_roles",
                "cal_source_file",
                "def_link_arcs",
                "def_link_locs",
                "def_link_roles",
                "def_source_file",
                "pre_link_arcs",
                "pre_link_locs",
                "pre_link_roles",
                "pre_source_file",
                "lab_link_arcs",
                "lab_link_locs",
                "lab_link_values",
                "lab_source_file",
                "sc_elements",
                "sc_import",
                "sc_linkbase_ref",
                "sc_source_file",
            ]
            
            # データをフィルタリング
            filtered_data = {k: v for k, v in data_dict.items() if k not in excluded_categories}
            
            # 各カテゴリをデータベースにインポート
            for category, data in filtered_data.items():
                if not data:
                    continue
                
                try:
                    # qualitative_infoの場合は階層構造に変換
                    if category == "qualitative_info":
                        if isinstance(data, list):
                            # 各要素が辞書であることを確認（Pydanticモデルの場合はmodel_dump()が必要）
                            qualitative_list = []
                            for item in data:
                                if hasattr(item, 'model_dump'):
                                    qualitative_list.append(item.model_dump())
                                elif isinstance(item, dict):
                                    qualitative_list.append(item)
                                else:
                                    qualitative_list.append(dict(item))
                            
                            # 階層構造に変換
                            data = format_qualitative_info_hierarchical(qualitative_list)
                        else:
                            # 単一のデータの場合
                            if hasattr(data, 'model_dump'):
                                data = format_qualitative_info_hierarchical([data.model_dump()])
                            elif isinstance(data, dict):
                                data = format_qualitative_info_hierarchical([data])
                            else:
                                data = format_qualitative_info_hierarchical([dict(data)])
                    
                    # データをDataFrameに変換
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame([data])
                    
                    # head_item_keyを追加
                    if 'head_item_key' not in df.columns:
                        df['head_item_key'] = head_item_key
                    
                    # テーブル名を決定（カテゴリ名をそのまま使用）
                    table_name = category
                    
                    # テーブルが存在しない場合は作成
                    if not self.connector.is_exist_table(table_name):
                        logger.info(f"テーブルが存在しないため作成します: {table_name}")
                        self.connector.create_table_from_df(table_name, df)
                    else:
                        # データベースに挿入（重複は無視）
                        try:
                            self.connector.add_data_from_df_ignore_duplicate(table_name, df)
                        except Exception as e:
                            # ON CONFLICTが使えない場合は通常の挿入を試す
                            logger.warning(f"重複無視の挿入に失敗しました。通常の挿入を試します: {e}")
                            self.connector.add_data_from_df(table_name, df)
                    
                    result["imported_tables"].append({
                        "table": table_name,
                        "rows": len(df),
                    })
                    
                    logger.info(f"インポート成功: {table_name} ({len(df)}行)")
                    
                except Exception as e:
                    error_msg = f"{category}のインポート中にエラーが発生: {e}"
                    logger.error(error_msg, exc_info=True)
                    result["errors"].append({
                        "category": category,
                        "error": str(e),
                    })
            
            result["success"] = len(result["errors"]) == 0
            return result
            
        except Exception as e:
            error_msg = f"XBRLファイル処理中にエラーが発生: {zip_path}, Error: {e}"
            logger.error(error_msg, exc_info=True)
            result["errors"].append({
                "category": "general",
                "error": str(e),
            })
            return result
    
    def import_xbrl_directory(
        self,
        data_dir: Path,
        output_path: Path,
        max_workers: int = 4,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """ディレクトリ内のXBRL zipファイルをデータベースにインポート
        
        Args:
            data_dir: zipファイルが格納されているディレクトリ
            output_path: 出力ディレクトリのパス
            max_workers: 並列処理の最大ワーカー数
            limit: インポートする最大ファイル数（Noneの場合はすべて）
            
        Returns:
            インポート結果のサマリー
        """
        # zipファイルを検索
        zip_files = list(data_dir.glob("*.zip"))
        
        if not zip_files:
            logger.warning(f"zipファイルが見つかりません: {data_dir}")
            return {
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "results": [],
            }
        
        # 件数制限を適用
        if limit is not None and limit > 0:
            zip_files = zip_files[:limit]
            logger.info(f"インポート対象のzipファイル数: {len(zip_files)} (制限: {limit}件)")
        else:
            logger.info(f"インポート対象のzipファイル数: {len(zip_files)}")
        
        results = []
        successful = 0
        failed = 0
        
        # 並列処理でインポート
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.import_xbrl_zip, zip_file, output_path): zip_file
                for zip_file in zip_files
            }
            
            # プログレスバーを表示
            with tqdm(total=len(zip_files), desc="インポート中") as pbar:
                for future in as_completed(futures):
                    zip_file = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        if result["success"]:
                            successful += 1
                        else:
                            failed += 1
                    except Exception as e:
                        logger.error(f"インポート処理中にエラーが発生: {zip_file}, Error: {e}", exc_info=True)
                        results.append({
                            "zip_file": str(zip_file),
                            "success": False,
                            "errors": [{"error": str(e)}],
                        })
                        failed += 1
                    finally:
                        pbar.update(1)
        
        return {
            "total_files": len(zip_files),
            "successful": successful,
            "failed": failed,
            "results": results,
        }


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="XBRLデータをデータベースにインポートします")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="zipファイルが格納されているディレクトリ（デフォルト: settings.resolved_data_path）",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="出力ディレクトリのパス（デフォルト: settings.resolved_output_path）",
    )
    parser.add_argument(
        "--zip-file",
        type=Path,
        default=None,
        help="単一のzipファイルをインポート",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="並列処理の最大ワーカー数（デフォルト: 4）",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="インポートする最大ファイル数（指定しない場合はすべて）",
    )
    
    args = parser.parse_args()
    
    # データベース設定の確認
    if not db_settings.username or not db_settings.password:
        logger.error("データベースの認証情報が設定されていません。")
        logger.error("XBRL_DB_USERNAME と XBRL_DB_PASSWORD を設定してください。")
        return 1
    
    # データディレクトリの決定
    if args.zip_file:
        data_dir = None
        zip_file = args.zip_file
        if not zip_file.exists():
            logger.error(f"zipファイルが見つかりません: {zip_file}")
            return 1
    else:
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
            logger.error(f"コンテナ内で実行する場合は、/app/dataディレクトリにzipファイルを配置してください")
            return 1
        
        zip_file = None
    
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
    
    try:
        importer = DatabaseImporter()
        
        if zip_file:
            # 単一ファイルのインポート
            logger.info(f"単一ファイルをインポートします: {zip_file}")
            result = importer.import_xbrl_zip(zip_file, output_path)
            
            print("\n" + "=" * 60)
            print("インポート結果")
            print("=" * 60)
            print(f"ファイル: {result['zip_file']}")
            print(f"head_item_key: {result['head_item_key']}")
            print(f"成功: {result['success']}")
            print(f"インポートされたテーブル数: {len(result['imported_tables'])}")
            print(f"エラー数: {len(result['errors'])}")
            
            if result['imported_tables']:
                print("\nインポートされたテーブル:")
                for table_info in result['imported_tables']:
                    print(f"  - {table_info['table']}: {table_info['rows']}行")
            
            if result['errors']:
                print("\nエラー:")
                for error in result['errors']:
                    print(f"  - {error.get('category', 'general')}: {error['error']}")
            
            return 0 if result['success'] else 1
        
        else:
            # ディレクトリ内のファイルをインポート
            logger.info(f"ディレクトリ内のファイルをインポートします: {data_dir}")
            results = importer.import_xbrl_directory(
                data_dir,
                output_path,
                max_workers=args.max_workers,
                limit=args.limit,
            )
            
            print("\n" + "=" * 60)
            print("インポート結果サマリー")
            print("=" * 60)
            print(f"総ファイル数: {results['total_files']}")
            print(f"成功: {results['successful']}件")
            print(f"失敗: {results['failed']}件")
            
            if results['failed'] > 0:
                print("\n失敗したファイル:")
                for result in results['results']:
                    if not result.get('success', False):
                        print(f"  - {result.get('zip_file', 'Unknown')}")
                        if result.get('errors'):
                            for error in result['errors']:
                                print(f"    Error: {error.get('error', 'Unknown error')}")
            
            return 0 if results['failed'] == 0 else 1
    
    except Exception as e:
        logger.error(f"インポート処理中にエラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
