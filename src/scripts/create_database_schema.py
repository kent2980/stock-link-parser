"""データベーススキーマを作成するスクリプト"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, List, Optional
import pandas as pd

from src.config import settings, db_settings
from src.connect.postgre_sql_connector import PostgreSqlConnector
from src.exception.error_handler import get_logger

logger = get_logger(__name__)


class DatabaseSchemaCreator:
    """データベーススキーマを作成するクラス"""
    
    def __init__(self, host_override: Optional[str] = None):
        """データベース接続を初期化
        
        Args:
            host_override: ホスト名のオーバーライド（Noneの場合は設定値を使用）
        """
        try:
            from src.connect.postgre_sql_connector import PostgreSqlConnector
        except ImportError as e:
            print("エラー: psycopg2がインストールされていません。")
            print("以下のコマンドでインストールしてください:")
            print("  uv add psycopg2-binary")
            print("  または")
            print("  pip install psycopg2-binary")
            sys.exit(1)
        
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
        
        # 接続を試行（複数のホストを順番に試す）
        connection_successful = False
        hosts_to_try = [db_host]
        
        # localhostが指定されている場合、127.0.0.1も試す
        if db_host == "localhost":
            hosts_to_try.append("127.0.0.1")
        
        # postgresが指定されている場合、localhostと127.0.0.1も試す
        if db_host == "postgres":
            hosts_to_try.extend(["localhost", "127.0.0.1"])
        
        for try_host in hosts_to_try:
            try:
                logger.info(f"データベースに接続を試みます: {try_host}:{db_settings.port}")
                self.connector = PostgreSqlConnector(
                    host=try_host,
                    port=db_settings.port,
                    database=db_settings.database,
                    user=db_settings.username,
                    password=db_settings.password,
                )
                self.connector.connect()
                
                if self.connector.connection:
                    connection_successful = True
                    db_host = try_host  # 成功したホスト名を保存
                    break
            except Exception as e:
                logger.debug(f"{try_host}への接続に失敗: {e}")
                continue
        
        if not connection_successful:
            raise ConnectionError(
                f"データベースに接続できませんでした。"
                f"試行したホスト: {', '.join(hosts_to_try)}。"
                f"設定を確認してください。"
            )
        
        logger.info(f"データベース接続が確立されました (host={db_host})")
    
    def __del__(self):
        """データベース接続を閉じる"""
        if hasattr(self, 'connector'):
            self.connector.disconnect()
    
    def drop_all_tables(self) -> List[str]:
        """すべてのテーブルを削除
        
        Returns:
            削除されたテーブル名のリスト
        """
        dropped_tables = []
        
        try:
            cursor = self.connector.connection.cursor()
            
            # すべてのテーブルを取得
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            
            tables = cursor.fetchall()
            
            # 外部キー制約を無効化
            cursor.execute("SET session_replication_role = 'replica';")
            
            # 各テーブルを削除
            for (table_name,) in tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                    dropped_tables.append(table_name)
                    logger.info(f"テーブルを削除しました: {table_name}")
                except Exception as e:
                    logger.warning(f"テーブル削除に失敗しました: {table_name}, Error: {e}")
            
            # 外部キー制約を再有効化
            cursor.execute("SET session_replication_role = 'origin';")
            
            self.connector.connection.commit()
            logger.info(f"合計 {len(dropped_tables)} 個のテーブルを削除しました")
            
        except Exception as e:
            logger.error(f"テーブル削除中にエラーが発生しました: {e}", exc_info=True)
            self.connector.connection.rollback()
        finally:
            if cursor:
                cursor.close()
        
        return dropped_tables
    
    def create_table_from_sample_data(
        self,
        table_name: str,
        sample_data: List[Dict],
        primary_keys: Optional[List[str]] = None,
    ) -> bool:
        """サンプルデータからテーブルを作成
        
        Args:
            table_name: テーブル名
            sample_data: サンプルデータのリスト
            primary_keys: 主キーとして使用するカラム名のリスト
            
        Returns:
            作成に成功した場合はTrue
        """
        if not sample_data:
            logger.warning(f"サンプルデータが空のため、テーブルを作成できません: {table_name}")
            return False
        
        try:
            # データをDataFrameに変換
            df = pd.DataFrame(sample_data)
            
            # head_item_keyを追加（存在しない場合）
            if 'head_item_key' not in df.columns:
                df['head_item_key'] = None
            
            # テーブルが既に存在する場合はスキップ
            if self.connector.is_exist_table(table_name):
                logger.info(f"テーブルは既に存在します: {table_name}")
                return True
            
            # テーブルを作成
            self.connector.create_table_from_df(table_name, df)
            
            # 主キーを設定
            if primary_keys:
                try:
                    cursor = self.connector.connection.cursor()
                    pk_columns = ', '.join(primary_keys)
                    cursor.execute(f"""
                        ALTER TABLE {table_name} 
                        ADD PRIMARY KEY ({pk_columns})
                    """)
                    self.connector.connection.commit()
                    logger.info(f"主キーを設定しました: {table_name} ({pk_columns})")
                except Exception as e:
                    logger.warning(f"主キーの設定に失敗しました: {table_name}, Error: {e}")
                    self.connector.connection.rollback()
                finally:
                    if cursor:
                        cursor.close()
            
            logger.info(f"テーブルを作成しました: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"テーブル作成中にエラーが発生しました: {table_name}, Error: {e}", exc_info=True)
            return False
    
    def create_schema_from_sample_zip(self, zip_path: Path, output_path: Path) -> Dict[str, bool]:
        """サンプルzipファイルからスキーマを作成
        
        Args:
            zip_path: サンプルzipファイルのパス
            output_path: 出力ディレクトリのパス
            
        Returns:
            テーブル名をキーとし、作成成功フラグを値とする辞書
        """
        from src.ix_models.xbrl_model import XBRLModel
        from src.utils.utils import Utils
        
        results = {}
        
        try:
            # XBRLModelのインスタンスを作成
            model = XBRLModel(zip_path, output_path)
            
            # データを取得
            items = model.get_all_items()
            data_dict = {item.key: item.item for item in items}
            
            # 除外カテゴリ
            excluded_categories = [
                "ix_non_fraction",
                "ix_non_numeric",
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
            
            # 各カテゴリのテーブルを作成
            for category, data in filtered_data.items():
                if not data:
                    continue
                
                # データをリストに変換
                if isinstance(data, list):
                    sample_data = data[:1] if data else []  # 最初の1件をサンプルとして使用
                else:
                    sample_data = [data]
                
                if not sample_data:
                    continue
                
                # 主キーの候補を決定
                primary_keys = None
                if 'item_key' in sample_data[0]:
                    primary_keys = ['item_key']
                elif 'head_item_key' in sample_data[0] and 'currentId' in sample_data[0]:
                    primary_keys = ['head_item_key', 'currentId']
                
                # テーブルを作成
                success = self.create_table_from_sample_data(
                    category,
                    sample_data,
                    primary_keys=primary_keys,
                )
                results[category] = success
            
            return results
            
        except Exception as e:
            logger.error(f"スキーマ作成中にエラーが発生しました: {zip_path}, Error: {e}", exc_info=True)
            return results
    
    def recreate_schema(
        self,
        zip_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        drop_existing: bool = True,
    ) -> Dict[str, any]:
        """データベーススキーマを再作成
        
        Args:
            zip_path: サンプルzipファイルのパス（スキーマ作成用）
            output_path: 出力ディレクトリのパス
            drop_existing: 既存のテーブルを削除するかどうか
            
        Returns:
            作成結果のサマリー
        """
        result = {
            "dropped_tables": [],
            "created_tables": {},
            "success": False,
        }
        
        try:
            # 既存のテーブルを削除
            if drop_existing:
                logger.info("既存のテーブルを削除します...")
                result["dropped_tables"] = self.drop_all_tables()
            
            # サンプルzipファイルからスキーマを作成
            if zip_path and zip_path.exists():
                logger.info(f"サンプルzipファイルからスキーマを作成します: {zip_path}")
                if output_path is None:
                    output_path = settings.resolved_output_path
                
                result["created_tables"] = self.create_schema_from_sample_zip(
                    zip_path,
                    output_path,
                )
            else:
                logger.warning("サンプルzipファイルが指定されていないため、スキーマを作成できません。")
                logger.info("既存のテーブルのみを削除しました。")
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"スキーマ再作成中にエラーが発生しました: {e}", exc_info=True)
            return result


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="データベーススキーマを再作成します")
    parser.add_argument(
        "--sample-zip",
        type=Path,
        default=None,
        help="スキーマ作成用のサンプルzipファイルのパス",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="出力ディレクトリのパス（デフォルト: settings.resolved_output_path）",
    )
    parser.add_argument(
        "--no-drop",
        action="store_true",
        help="既存のテーブルを削除しない",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="データディレクトリ（サンプルzipファイルを自動検索）",
    )
    
    args = parser.parse_args()
    
    # データベース設定の確認
    if not db_settings.username or not db_settings.password:
        logger.error("データベースの認証情報が設定されていません。")
        logger.error("XBRL_DB_USERNAME と XBRL_DB_PASSWORD を設定してください。")
        return 1
    
    # サンプルzipファイルの決定
    zip_path = args.sample_zip
    
    if not zip_path and args.data_dir:
        # データディレクトリから最初のzipファイルを検索
        data_dir = Path(args.data_dir)
        if data_dir.exists():
            zip_files = list(data_dir.glob("*.zip"))
            if zip_files:
                zip_path = zip_files[0]
                logger.info(f"サンプルzipファイルを自動検出: {zip_path}")
    
    if not zip_path:
        # 設定から取得
        # コンテナ内で実行されている場合（/appが存在する場合）は/app/dataを使用
        if Path("/app").exists():
            data_dir = Path("/app/data")
            logger.info(f"コンテナ内で実行されているため、/app/dataを使用します")
        else:
            data_dir = settings.resolved_data_path
        
        if data_dir.exists():
            zip_files = list(data_dir.glob("*.zip"))
            if zip_files:
                zip_path = zip_files[0]
                logger.info(f"サンプルzipファイルを自動検出: {zip_path}")
    
    if not zip_path or not zip_path.exists():
        logger.warning("サンプルzipファイルが見つかりません。")
        logger.warning("--sample-zipオプションで指定するか、データディレクトリにzipファイルを配置してください。")
        if args.no_drop:
            logger.info("--no-dropが指定されているため、処理を終了します。")
            return 0
        else:
            # 非対話モード: 既存のテーブルのみを削除
            logger.info("既存のテーブルを削除します（スキーマ作成はスキップ）。")
            try:
                creator = DatabaseSchemaCreator()
                result = creator.recreate_schema(
                    zip_path=None,
                    output_path=output_path,
                    drop_existing=True,
                )
                print("\n" + "=" * 60)
                print("テーブル削除結果")
                print("=" * 60)
                if result["dropped_tables"]:
                    print(f"削除されたテーブル数: {len(result['dropped_tables'])}")
                    for table in result["dropped_tables"][:10]:
                        print(f"  - {table}")
                    if len(result["dropped_tables"]) > 10:
                        print(f"  ... 他 {len(result['dropped_tables']) - 10}件")
                else:
                    print("削除されたテーブルはありません。")
                return 0
            except Exception as e:
                logger.error(f"テーブル削除処理中にエラーが発生しました: {e}", exc_info=True)
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
    
    try:
        creator = DatabaseSchemaCreator()
        
        result = creator.recreate_schema(
            zip_path=zip_path,
            output_path=output_path,
            drop_existing=not args.no_drop,
        )
        
        print("\n" + "=" * 60)
        print("スキーマ再作成結果")
        print("=" * 60)
        
        if result["dropped_tables"]:
            print(f"\n削除されたテーブル数: {len(result['dropped_tables'])}")
            for table in result["dropped_tables"][:10]:
                print(f"  - {table}")
            if len(result["dropped_tables"]) > 10:
                print(f"  ... 他 {len(result['dropped_tables']) - 10}件")
        
        if result["created_tables"]:
            print(f"\n作成されたテーブル数: {len(result['created_tables'])}")
            successful = sum(1 for v in result["created_tables"].values() if v)
            failed = sum(1 for v in result["created_tables"].values() if not v)
            
            print(f"  成功: {successful}件")
            print(f"  失敗: {failed}件")
            
            if successful > 0:
                print("\n作成されたテーブル:")
                for table_name, success in result["created_tables"].items():
                    if success:
                        print(f"  ✓ {table_name}")
            
            if failed > 0:
                print("\n作成に失敗したテーブル:")
                for table_name, success in result["created_tables"].items():
                    if not success:
                        print(f"  ✗ {table_name}")
        
        print(f"\n処理結果: {'成功' if result['success'] else '失敗'}")
        
        return 0 if result["success"] else 1
    
    except Exception as e:
        logger.error(f"スキーマ再作成処理中にエラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
