"""FastAPIアプリケーション

XBRLデータを配信するためのREST API
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings, db_settings
from src.exception.error_handler import get_logger
from src.ix_models.xbrl_model import XBRLModel
from src.utils.utils import Utils
from src.utils.qualitative_utils import format_qualitative_info_hierarchical

try:
    from src.connect.postgre_sql_connector import PostgreSqlConnector
except ImportError:
    PostgreSqlConnector = None
    print("警告: psycopg2がインストールされていません。データベース機能は使用できません。")

# ロガーを取得
logger = get_logger(__name__)

# FastAPIアプリケーションを作成
app = FastAPI(
    title="XBRL Data API",
    description="XBRLデータを配信するためのREST API",
    version="1.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# XBRLModelのキャッシュ（簡易実装）
_xbrl_model_cache: Dict[str, XBRLModel] = {}

# データベース接続（グローバル）
_db_connector: Optional[PostgreSqlConnector] = None


def get_db_connector() -> Optional[PostgreSqlConnector]:
    """データベースコネクターを取得（シングルトン）"""
    global _db_connector
    
    if PostgreSqlConnector is None:
        return None
    
    if _db_connector is None:
        try:
            # ホスト名の決定（コンテナ環境ではpostgres、ローカル環境ではlocalhost）
            db_host = db_settings.host
            
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
            
            _db_connector = PostgreSqlConnector(
                host=db_host,
                port=db_settings.port,
                database=db_settings.database,
                user=db_settings.username,
                password=db_settings.password,
            )
            _db_connector.connect()
            
            if not _db_connector.connection:
                logger.error("データベースに接続できませんでした。")
                _db_connector = None
            else:
                logger.info(f"データベース接続が確立されました (host={db_host})")
        except Exception as e:
            logger.error(f"データベース接続に失敗しました: {e}", exc_info=True)
            _db_connector = None
    
    return _db_connector


def get_data_from_db(
    head_item_key: str, 
    category: Optional[str] = None,
    page: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """データベースからデータを取得
    
    Args:
        head_item_key: head_item_key
        category: カテゴリ名（Noneの場合はすべてのカテゴリ）
        page: ページ番号（Noneの場合はページネーションなし）
        limit: 1ページあたりの取得数（Noneの場合はページネーションなし）
    
    Returns:
        データの辞書
    """
    connector = get_db_connector()
    if not connector or not connector.connection:
        return {}
    
    cursor = None
    try:
        cursor = connector.connection.cursor()
        
        # すべてのテーブルを取得
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
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
        
        data_dict = {}
        
        for table_name in tables:
            if table_name in excluded_categories:
                continue
            
            if category and table_name != category:
                continue
            
            try:
                # ページネーションがある場合は総数を取得
                if page is not None and limit is not None:
                    count_query = f'SELECT COUNT(*) FROM "{table_name}" WHERE head_item_key = %s'
                    cursor.execute(count_query, (head_item_key,))
                    total = cursor.fetchone()[0]
                    
                    # head_item_keyでフィルタリングしてデータを取得（ページネーション適用）
                    offset = (page - 1) * limit
                    query = f'SELECT * FROM "{table_name}" WHERE head_item_key = %s LIMIT %s OFFSET %s'
                    cursor.execute(query, (head_item_key, limit, offset))
                else:
                    # ページネーションなし
                    query = f'SELECT * FROM "{table_name}" WHERE head_item_key = %s'
                    cursor.execute(query, (head_item_key,))
                    total = None
                
                # カラム名を取得
                columns = [desc[0] for desc in cursor.description]
                
                # データを取得
                rows = cursor.fetchall()
                
                if rows:
                    # 各行を辞書に変換
                    table_data = []
                    for row in rows:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            value = row[i]
                            # JSONB型の場合はそのまま使用
                            if isinstance(value, (dict, list)):
                                row_dict[col] = value
                            else:
                                row_dict[col] = value
                        table_data.append(row_dict)
                    
                    data_dict[table_name] = table_data if len(table_data) > 1 else table_data[0] if len(table_data) == 1 else []
            except Exception as e:
                logger.warning(f"テーブル {table_name} からのデータ取得に失敗: {e}")
                # エラーが発生した場合、トランザクションをロールバック
                try:
                    connector.connection.rollback()
                except:
                    pass
                continue
        
        cursor.close()
        cursor = None
        return data_dict
        
    except Exception as e:
        if cursor:
            try:
                connector.connection.rollback()
            except:
                pass
            cursor.close()
        logger.error(f"データベースからのデータ取得に失敗: {e}", exc_info=True)
        return {}


def get_xbrl_model(head_item_key: str) -> Optional[XBRLModel]:
    """XBRLModelを取得（キャッシュから）"""
    if head_item_key in _xbrl_model_cache:
        return _xbrl_model_cache[head_item_key]

    # キャッシュにない場合は、zipファイルを検索
    data_dir = Path(settings.resolved_data_path)
    zip_files = list(data_dir.glob("*.zip"))

    # head_item_keyからzipファイルを直接特定（効率化）
    # すべてのzipファイル名からhead_item_keyを計算して一致するものを探す
    for zip_file in zip_files:
        try:
            # zipファイル名からhead_item_keyを計算
            calculated_head_item_key = str(Utils.string_to_uuid(zip_file.name))
            if calculated_head_item_key == head_item_key:
                # 一致するzipファイルが見つかったら、モデルを作成
                model = XBRLModel(zip_file, settings.resolved_output_path)
                # キャッシュに追加
                _xbrl_model_cache[head_item_key] = model
                return model
        except Exception as e:
            logger.warning(f"Failed to calculate head_item_key from {zip_file.name}: {e}")
            continue

    # フォールバック: 従来の方法（すべてのzipファイルを読み込んで確認）
    # これは時間がかかるため、上記の方法で見つからない場合のみ使用
    logger.warning(f"head_item_key {head_item_key} not found by direct calculation, trying fallback method")
    for zip_file in zip_files:
        try:
            model = XBRLModel(zip_file, settings.resolved_output_path)
            items = model.get_all_items()
            # head_item_keyを取得
            file_path_items = [item for item in items if item.key == "ix_file_path"]
            if file_path_items and file_path_items[0].item:
                file_path_data = file_path_items[0].item[0] if isinstance(file_path_items[0].item, list) else file_path_items[0].item
                model_head_item_key = file_path_data.get("head_item_key")
                if model_head_item_key == head_item_key:
                    _xbrl_model_cache[head_item_key] = model
                    return model
            # モデルを破棄（メモリ節約）
            del model
        except Exception as e:
            logger.warning(f"Failed to load model from {zip_file}: {e}")
            continue

    return None


def dataclass_to_dict(data_class: Any) -> Dict[str, Any]:
    """データクラスを辞書に変換"""
    result = {}
    if hasattr(data_class, "__available_properties__"):
        for prop_name in data_class.__available_properties__:
            if hasattr(data_class, prop_name):
                value = getattr(data_class, prop_name)
                # JSON文字列の場合はパース
                if prop_name.endswith("_json") and isinstance(value, str):
                    try:
                        value = json.loads(value)
                        # _jsonサフィックスを削除
                        prop_name = prop_name[:-5]
                    except json.JSONDecodeError:
                        pass
                result[prop_name] = value
    return result


@app.get("/")
async def root():
    """APIの基本情報"""
    return {
        "name": "XBRL Data API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "head_item_keys": "/api/v1/xbrl/head-item-keys",
            "headers": "/api/v1/xbrl/headers",
            "xbrl_files": "/api/v1/xbrl/files",
            "xbrl_data": "/api/v1/xbrl/files/{head_item_key}/data",
            "categories": "/api/v1/xbrl/categories",
        },
    }


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2026-01-27T06:00:00Z",
    }


@app.get("/api/v1/xbrl/head-item-keys")
async def get_head_item_keys(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
):
    """すべてのhead_item_keyの一覧を取得

    Args:
        page: ページ番号（1から開始）
        limit: 1ページあたりの取得数（最大500）

    Returns:
        head_item_keys: zipファイルから生成されたhead_item_keyの一覧
    """
    try:
        connector = get_db_connector()
        
        # データベースから取得を試みる
        if connector and connector.connection:
            try:
                cursor = connector.connection.cursor()
                
                # 総数を取得
                cursor.execute("""
                    SELECT COUNT(DISTINCT head_item_key) 
                    FROM ix_file_path
                """)
                total = cursor.fetchone()[0]
                
                # ページネーション
                pages = (total + limit - 1) // limit
                start = (page - 1) * limit
                
                # head_item_keyを取得（ページネーション適用）
                cursor.execute("""
                    SELECT DISTINCT head_item_key 
                    FROM ix_file_path
                    ORDER BY head_item_key
                    LIMIT %s OFFSET %s
                """, (limit, start))
                head_item_keys = [row[0] for row in cursor.fetchall()]
                
                # zip_file_nameも取得
                result = []
                for key in head_item_keys:
                    cursor.execute(
                        'SELECT path FROM ix_file_path WHERE head_item_key = %s LIMIT 1',
                        (key,)
                    )
                    file_result = cursor.fetchone()
                    zip_file_name = Path(file_result[0]).name if file_result and file_result[0] else None
                    
                    result.append({
                        "head_item_key": key,
                        "zip_file_name": zip_file_name,
                    })
                
                cursor.close()
                
                return {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": pages,
                    "has_next": page < pages,
                    "has_prev": page > 1,
                    "head_item_keys": result,
                }
            except Exception as e:
                logger.warning(f"データベースからの取得に失敗、zipファイルから取得します: {e}")
        
        # フォールバック: zipファイルから取得
        data_dir = Path(settings.resolved_data_path)
        zip_files = list(data_dir.glob("*.zip"))

        # ページネーション
        total = len(zip_files)
        pages = (total + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit
        paginated_files = zip_files[start:end]

        head_item_keys = []
        for zip_file in paginated_files:
            head_item_key = str(Utils.string_to_uuid(zip_file.name))
            head_item_keys.append(
                {
                    "head_item_key": head_item_key,
                    "zip_file_name": zip_file.name,
                }
            )

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
            "head_item_keys": head_item_keys,
        }
    except Exception as e:
        logger.error(f"Failed to get head_item_keys: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/xbrl/headers")
async def get_headers(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
):
    """すべてのheader（ix_head_title）の一覧を取得（提出日降順、データベースからのみ）
    
    Args:
        page: ページ番号（1から開始）
        limit: 1ページあたりの取得数（最大500）
    
    Returns:
        headers: header情報のリスト（提出日降順）
    """
    cursor = None
    try:
        # データベース接続を確認
        connector = get_db_connector()
        if not connector or not connector.connection:
            raise HTTPException(
                status_code=503,
                detail="データベースに接続できません。データベースが起動していることを確認してください。"
            )
        
        cursor = connector.connection.cursor()
        
        # 総数を取得
        cursor.execute("SELECT COUNT(*) FROM ix_head_title")
        total = cursor.fetchone()[0]
        
        # ページネーション
        pages = (total + limit - 1) // limit
        offset = (page - 1) * limit
        
        # reporting_date降順でソートして取得
        # reporting_dateがNULLの場合は最後に配置
        query = """
            SELECT * FROM ix_head_title
            ORDER BY 
                CASE 
                    WHEN reporting_date IS NULL OR reporting_date = '' THEN 1 
                    ELSE 0 
                END,
                reporting_date DESC NULLS LAST
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, offset))
        
        # カラム名を取得
        columns = [desc[0] for desc in cursor.description]
        
        # データを取得
        rows = cursor.fetchall()
        
        headers = []
        for row in rows:
            header_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # JSONB型の場合はそのまま使用
                if isinstance(value, (dict, list)):
                    header_dict[col] = value
                else:
                    header_dict[col] = value
            headers.append(header_dict)
        
        cursor.close()
        cursor = None
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
            "headers": headers,
        }
    except HTTPException:
        if cursor:
            try:
                connector.connection.rollback()
            except:
                pass
            cursor.close()
        raise
    except Exception as e:
        if cursor:
            try:
                connector.connection.rollback()
            except:
                pass
            cursor.close()
        logger.error(f"Failed to get headers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# カテゴリ一覧（IDと名前のマッピング）
CATEGORIES_LIST = [
    {
        "id": 1,
        "name": "ix_non_fraction_enriched",
        "display_name": "iXBRL非分数データ（統合版）",
        "description": "iXBRLの非分数値データ（ラベル・計算・定義・表示リンク情報統合済み）",
    },
    {
        "id": 2,
        "name": "ix_non_numeric_enriched",
        "display_name": "iXBRL非数値データ（統合版）",
        "description": "iXBRLの非数値データ（ラベル・計算・定義・表示リンク情報統合済み）",
    },
    {
        "id": 3,
        "name": "ix_context",
        "display_name": "iXBRLコンテキスト",
        "description": "iXBRLのコンテキスト情報",
    },
    {
        "id": 4,
        "name": "ix_head_title",
        "display_name": "iXBRLヘッダータイトル",
        "description": "iXBRLのヘッダー情報",
    },
    {
        "id": 5,
        "name": "ix_file_path",
        "display_name": "iXBRLファイルパス",
        "description": "iXBRLファイルのパス情報",
    },
    {
        "id": 6,
        "name": "ix_source_file",
        "display_name": "iXBRLソースファイル",
        "description": "iXBRLのソースファイル情報",
    },
    {
        "id": 7,
        "name": "qualitative_info",
        "display_name": "定性情報",
        "description": "XBRLの定性情報",
    },
    {
        "id": 8,
        "name": "qualitative_source_file",
        "display_name": "定性情報ソースファイル",
        "description": "定性情報のソースファイル情報",
    },
    {
        "id": 9,
        "name": "href_master",
        "display_name": "リンクマスター",
        "description": "XBRLのリンクマスター情報",
    },
]

# カテゴリIDから名前へのマッピング
CATEGORY_ID_TO_NAME = {cat["id"]: cat["name"] for cat in CATEGORIES_LIST}
# カテゴリ名からIDへのマッピング
CATEGORY_NAME_TO_ID = {cat["name"]: cat["id"] for cat in CATEGORIES_LIST}


def parse_categories_param(categories_param: Optional[str]) -> List[str]:
    """categoriesパラメータをパース（文字列または番号で指定可能）
    
    Args:
        categories_param: カテゴリ指定（カンマ区切りの文字列または番号）
    
    Returns:
        カテゴリ名のリスト
    """
    if not categories_param:
        return []
    
    category_names = []
    for item in categories_param.split(","):
        item = item.strip()
        if not item:
            continue
        
        # 番号で指定されている場合
        try:
            category_id = int(item)
            if category_id in CATEGORY_ID_TO_NAME:
                category_names.append(CATEGORY_ID_TO_NAME[category_id])
            else:
                logger.warning(f"無効なカテゴリID: {category_id}")
        except ValueError:
            # 文字列で指定されている場合
            if item in CATEGORY_NAME_TO_ID:
                category_names.append(item)
            else:
                logger.warning(f"無効なカテゴリ名: {item}")
    
    return category_names


@app.get("/api/v1/xbrl/categories")
async def get_categories():
    """利用可能なデータカテゴリ一覧"""
    return {"categories": CATEGORIES_LIST}


@app.get("/api/v1/xbrl/files")
async def get_xbrl_files(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
    head_item_key: Optional[str] = None,
):
    """XBRLファイルの一覧を取得（データベースからのみ）"""
    try:
        # データベース接続を確認
        connector = get_db_connector()
        if not connector or not connector.connection:
            raise HTTPException(
                status_code=503,
                detail="データベースに接続できません。データベースが起動していることを確認してください。"
            )
        
        cursor = connector.connection.cursor()
        
        try:
            # ix_file_pathテーブルからhead_item_keyの一覧を取得
            if head_item_key:
                query = """
                    SELECT DISTINCT head_item_key 
                    FROM ix_file_path
                    WHERE head_item_key = %s
                    ORDER BY head_item_key
                """
                cursor.execute(query, (head_item_key,))
            else:
                query = """
                    SELECT DISTINCT head_item_key 
                    FROM ix_file_path
                    ORDER BY head_item_key
                """
                cursor.execute(query)
            
            all_head_item_keys = [row[0] for row in cursor.fetchall()]
            
            # ページネーション
            total = len(all_head_item_keys)
            pages = (total + limit - 1) // limit
            start = (page - 1) * limit
            end = start + limit
            paginated_keys = all_head_item_keys[start:end]
            
            # ファイル情報を構築
            files_data = []
            for key in paginated_keys:
                # zipファイル名を取得（ix_file_pathテーブルから）
                cursor.execute(
                    'SELECT path FROM ix_file_path WHERE head_item_key = %s LIMIT 1',
                    (key,)
                )
                result = cursor.fetchone()
                zip_file_name = Path(result[0]).name if result and result[0] else None
                
                files_data.append({
                    "head_item_key": key,
                    "zip_file_name": zip_file_name,
                    "file_path": result[0] if result and result[0] else None,
                })
            
            cursor.close()
            cursor = None
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1,
                "data": files_data,
            }
        except Exception as e:
            if cursor:
                try:
                    connector.connection.rollback()
                except:
                    pass
                cursor.close()
            logger.error(f"データベースからの取得に失敗: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"データベースからのデータ取得に失敗しました: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get xbrl files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/xbrl/ix/head/is_active/")
async def is_active_head(head_item_key: str = Query(..., description="head_item_key")):
    """指定したhead_item_keyがデータベースに存在するか（有効か）を返す。
    Insertスクリプトが重複挿入をスキップするために使用する。
    """
    try:
        connector = get_db_connector()
        if not connector or not connector.connection:
            return {"is_active": False}
        cursor = connector.connection.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM ix_file_path WHERE head_item_key = %s LIMIT 1",
                (head_item_key,),
            )
            exists = cursor.fetchone() is not None
            return {"is_active": exists}
        finally:
            cursor.close()
    except Exception as e:
        logger.warning(f"is_active_head 確認中にエラー: {e}")
        return {"is_active": False}


@app.get("/api/v1/xbrl/files/{head_item_key}")
async def get_xbrl_file_info(head_item_key: str):
    """特定のXBRLファイルのメタ情報を取得（データベースからのみ）"""
    try:
        # データベース接続を確認
        connector = get_db_connector()
        if not connector or not connector.connection:
            raise HTTPException(
                status_code=503,
                detail="データベースに接続できません。データベースが起動していることを確認してください。"
            )
        
        # データベースから取得
        data_dict = get_data_from_db(head_item_key)
        
        # データが見つからない場合
        if not data_dict:
            raise HTTPException(
                status_code=404,
                detail=f"head_item_key '{head_item_key}' のデータが見つかりません。データベースにデータがインポートされていることを確認してください。"
            )

        # ファイルパス情報
        ix_file_path_data = data_dict.get("ix_file_path")
        if ix_file_path_data:
            if isinstance(ix_file_path_data, list):
                file_path = ix_file_path_data[0] if len(ix_file_path_data) > 0 else {}
            elif isinstance(ix_file_path_data, dict):
                file_path = ix_file_path_data
            else:
                file_path = {}
        else:
            file_path = {}
        
        # ヘッダー情報
        ix_head_title_data = data_dict.get("ix_head_title")
        if ix_head_title_data:
            if isinstance(ix_head_title_data, list):
                header = ix_head_title_data[0] if len(ix_head_title_data) > 0 else {}
            elif isinstance(ix_head_title_data, dict):
                header = ix_head_title_data
            else:
                header = {}
        else:
            header = {}

        return {
            "head_item_key": head_item_key,
            "file_path": file_path,
            "header": header,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get xbrl file info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/xbrl/files/{head_item_key}/data")
async def get_xbrl_data(
    head_item_key: str,
    categories: Optional[str] = Query(None, description="取得するカテゴリ（カンマ区切り、カテゴリ名またはID番号で指定可能。例: 'ix_head_title,ix_context' または '4,3'）"),
    format: str = Query("json", pattern="^(json|csv)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
):
    """XBRLデータを取得（データベースからのみ）
    
    Args:
        head_item_key: head_item_key
        categories: 取得するカテゴリ（カンマ区切り、カテゴリ名またはID番号で指定可能）
        format: 出力形式（jsonまたはcsv）
        page: ページ番号（1から開始）
        limit: 1ページあたりの取得数（最大500、カテゴリごと）
    """
    try:
        # データベース接続を確認
        connector = get_db_connector()
        if not connector or not connector.connection:
            raise HTTPException(
                status_code=503,
                detail="データベースに接続できません。データベースが起動していることを確認してください。"
            )
        
        # データベースから取得
        data_dict = get_data_from_db(head_item_key)
        
        # データが見つからない場合
        if not data_dict:
            raise HTTPException(
                status_code=404,
                detail=f"head_item_key '{head_item_key}' のデータが見つかりません。データベースにデータがインポートされていることを確認してください。"
            )
        
        # 除外カテゴリをフィルタ
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
        data_dict = {k: v for k, v in data_dict.items() if k not in excluded_categories}

        # カテゴリでフィルタ（文字列または番号で指定可能）
        if categories:
            category_list = parse_categories_param(categories)
            data_dict = {k: v for k, v in data_dict.items() if k in category_list}
        
        # 各カテゴリにページネーションを適用
        paginated_data = {}
        for category, category_data in data_dict.items():
            if not isinstance(category_data, list):
                category_data = [category_data]
            
            # qualitative_infoの場合は階層構造に変換
            if category == "qualitative_info":
                # データベースから取得した場合でも、階層構造でない場合は変換
                if not is_hierarchical_format(category_data):
                    # 各要素が辞書であることを確認（Pydanticモデルの場合はmodel_dump()が必要）
                    qualitative_list = []
                    for item in category_data:
                        if hasattr(item, 'model_dump'):
                            qualitative_list.append(item.model_dump())
                        elif isinstance(item, dict):
                            qualitative_list.append(item)
                        else:
                            qualitative_list.append(dict(item))
                    
                    category_data = format_qualitative_info_hierarchical(qualitative_list)
            
            # ページネーション
            total = len(category_data)
            pages = (total + limit - 1) // limit
            start = (page - 1) * limit
            end = start + limit
            paginated_items = category_data[start:end]
            
            paginated_data[category] = {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1,
                "data": paginated_items,
            }

        return {
            "head_item_key": head_item_key,
            "data": paginated_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get xbrl data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def is_hierarchical_format(data: Any) -> bool:
    """データが階層構造（{title: str, content: List[str]}）形式かどうかを判定
    
    Args:
        data: 判定するデータ
        
    Returns:
        階層構造形式の場合はTrue、そうでない場合はFalse
    """
    if not isinstance(data, (list, dict)):
        return False
    
    # リストの場合、最初の要素をチェック
    if isinstance(data, list):
        if not data:
            return False
        # 複数の要素をチェック（すべて階層構造であることを確認）
        for item in data[:3]:  # 最大3つまでチェック
            if not isinstance(item, dict):
                return False
            has_title = "title" in item
            has_content = "content" in item
            has_current_id = "currentId" in item
            has_parent_id = "parentId" in item
            
            # titleとcontentがあり、currentIdやparentIdがない場合は階層構造
            # また、contentがリストであることも確認
            if has_title and has_content and not has_current_id and not has_parent_id:
                if isinstance(item.get("content"), list):
                    continue
                else:
                    return False
            else:
                return False
        return True
    
    # 辞書の場合
    if isinstance(data, dict):
        # titleとcontentフィールドがあり、currentIdやparentIdがない場合は階層構造
        has_title = "title" in data
        has_content = "content" in data
        has_current_id = "currentId" in data
        has_parent_id = "parentId" in data
        
        # titleとcontentがあり、currentIdやparentIdがない場合は階層構造
        # また、contentがリストであることも確認
        if has_title and has_content and not has_current_id and not has_parent_id:
            if isinstance(data.get("content"), list):
                return True
    
    return False


@app.get("/api/v1/xbrl/files/{head_item_key}/data/{category}")
async def get_xbrl_category_data(
    head_item_key: str,
    category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=500),
):
    """特定のカテゴリのデータを取得
    
    Args:
        head_item_key: head_item_key
        category: カテゴリ名またはID番号（例: "ix_head_title" または "4"）
        page: ページ番号（1から開始）
        limit: 1ページあたりの取得数（最大500）
    """
    try:
        # 番号で指定されている場合はカテゴリ名に変換
        try:
            category_id = int(category)
            if category_id in CATEGORY_ID_TO_NAME:
                category = CATEGORY_ID_TO_NAME[category_id]
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"無効なカテゴリID: {category_id}。有効なIDは1-9です。",
                )
        except ValueError:
            # 文字列の場合はそのまま使用
            pass
        
        # 除外カテゴリチェック
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

        if category in excluded_categories:
            raise HTTPException(
                status_code=400,
                detail=f"カテゴリ '{category}' は統合データに含まれているため、個別には提供されていません。",
            )

        # データベース接続を確認
        connector = get_db_connector()
        if not connector or not connector.connection:
            raise HTTPException(
                status_code=503,
                detail="データベースに接続できません。データベースが起動していることを確認してください。"
            )
        
        # qualitative_infoの場合は、階層構造変換のために全データを取得する必要がある
        if category == "qualitative_info":
            # 階層構造変換のため、ページネーションなしで全データを取得
            data_dict = get_data_from_db(head_item_key, category=category, page=None, limit=None)
            
            if not data_dict or category not in data_dict:
                raise HTTPException(
                    status_code=404,
                    detail=f"head_item_key '{head_item_key}' のカテゴリ '{category}' が見つかりません。データベースにデータがインポートされていることを確認してください。"
                )

            category_data = data_dict[category]
            if not isinstance(category_data, list):
                category_data = [category_data]

            # 階層構造でない場合は変換
            if not is_hierarchical_format(category_data):
                # 各要素が辞書であることを確認（Pydanticモデルの場合はmodel_dump()が必要）
                qualitative_list = []
                for item in category_data:
                    if hasattr(item, 'model_dump'):
                        qualitative_list.append(item.model_dump())
                    elif isinstance(item, dict):
                        qualitative_list.append(item)
                    else:
                        qualitative_list.append(dict(item))
                
                category_data = format_qualitative_info_hierarchical(qualitative_list)
            
            # 階層構造変換後にページネーションを適用
            total = len(category_data)
            pages = (total + limit - 1) // limit
            start = (page - 1) * limit
            end = start + limit
            paginated_data = category_data[start:end]
        else:
            # その他のカテゴリは通常通りページネーション適用で取得
            data_dict = get_data_from_db(head_item_key, category=category, page=page, limit=limit)
            
            if not data_dict or category not in data_dict:
                raise HTTPException(
                    status_code=404,
                    detail=f"head_item_key '{head_item_key}' のカテゴリ '{category}' が見つかりません。データベースにデータがインポートされていることを確認してください。"
                )

            category_data = data_dict[category]
            if not isinstance(category_data, list):
                category_data = [category_data]

            # データベースから取得した場合は既にページネーションが適用されている
            # リストの場合はページネーションを適用、そうでない場合は既に適用済み
            if isinstance(category_data, list):
                total = len(category_data)
                pages = (total + limit - 1) // limit
                start = (page - 1) * limit
                end = start + limit
                paginated_data = category_data[start:end]
            else:
                # データベースから取得した場合（既にページネーション適用済み）
                paginated_data = category_data
                # 総数を取得するために再度クエリ
                if connector and connector.connection:
                    try:
                        cursor = connector.connection.cursor()
                        cursor.execute(f'SELECT COUNT(*) FROM "{category}" WHERE head_item_key = %s', (head_item_key,))
                        total = cursor.fetchone()[0]
                        cursor.close()
                    except Exception as e:
                        logger.warning(f"総数の取得に失敗: {e}")
                        total = len(paginated_data) if isinstance(paginated_data, list) else 1
                else:
                    total = len(paginated_data) if isinstance(paginated_data, list) else 1
                
                pages = (total + limit - 1) // limit

        return {
            "head_item_key": head_item_key,
            "category": category,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
            "data": paginated_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get xbrl category data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/xbrl/files/{head_item_key}/metadata")
async def get_xbrl_metadata(head_item_key: str):
    """メタデータを取得（データベースからのみ）"""
    try:
        # データベース接続を確認
        connector = get_db_connector()
        if not connector or not connector.connection:
            raise HTTPException(
                status_code=503,
                detail="データベースに接続できません。データベースが起動していることを確認してください。"
            )
        
        # データベースから取得
        data_dict = get_data_from_db(head_item_key)
        
        # データが見つからない場合
        if not data_dict:
            raise HTTPException(
                status_code=404,
                detail=f"head_item_key '{head_item_key}' のデータが見つかりません。データベースにデータがインポートされていることを確認してください。"
            )

        # 統計情報
        statistics = {}
        for key, value in data_dict.items():
            if isinstance(value, list):
                statistics[f"{key}_count"] = len(value)
            else:
                statistics[f"{key}_count"] = 1

        # ヘッダー情報
        header = data_dict.get("ix_head_title", [{}])[0] if data_dict.get("ix_head_title") else {}

        return {
            "head_item_key": head_item_key,
            "header": header,
            "statistics": statistics,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get xbrl metadata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """グローバル例外ハンドラー"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "内部サーバーエラーが発生しました",
                "details": {"exception": str(exc)},
            }
        },
    )
