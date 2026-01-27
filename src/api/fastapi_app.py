"""FastAPIアプリケーション

XBRLデータを配信するためのREST API
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.exception.error_handler import get_logger
from src.ix_models.xbrl_model import XBRLModel
from src.utils.utils import Utils

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
async def get_head_item_keys():
    """すべてのhead_item_keyの一覧を取得

    Returns:
        head_item_keys: zipファイルから生成されたhead_item_keyの一覧
    """
    try:
        data_dir = Path(settings.resolved_data_path)
        zip_files = list(data_dir.glob("*.zip"))

        head_item_keys = []
        for zip_file in zip_files:
            head_item_key = str(Utils.string_to_uuid(zip_file.name))
            head_item_keys.append(
                {
                    "head_item_key": head_item_key,
                    "zip_file_name": zip_file.name,
                }
            )

        return {
            "total": len(head_item_keys),
            "head_item_keys": head_item_keys,
        }
    except Exception as e:
        logger.error(f"Failed to get head_item_keys: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/xbrl/categories")
async def get_categories():
    """利用可能なデータカテゴリ一覧"""
    categories = [
        {
            "name": "ix_non_fraction_enriched",
            "display_name": "iXBRL非分数データ（統合版）",
            "description": "iXBRLの非分数値データ（ラベル・計算・定義・表示リンク情報統合済み）",
        },
        {
            "name": "ix_non_numeric_enriched",
            "display_name": "iXBRL非数値データ（統合版）",
            "description": "iXBRLの非数値データ（ラベル・計算・定義・表示リンク情報統合済み）",
        },
        {
            "name": "ix_context",
            "display_name": "iXBRLコンテキスト",
            "description": "iXBRLのコンテキスト情報",
        },
        {
            "name": "ix_head_title",
            "display_name": "iXBRLヘッダータイトル",
            "description": "iXBRLのヘッダー情報",
        },
        {
            "name": "ix_file_path",
            "display_name": "iXBRLファイルパス",
            "description": "iXBRLファイルのパス情報",
        },
        {
            "name": "ix_source_file",
            "display_name": "iXBRLソースファイル",
            "description": "iXBRLのソースファイル情報",
        },
        {
            "name": "qualitative_info",
            "display_name": "定性情報",
            "description": "XBRLの定性情報",
        },
        {
            "name": "qualitative_source_file",
            "display_name": "定性情報ソースファイル",
            "description": "定性情報のソースファイル情報",
        },
        {
            "name": "href_master",
            "display_name": "リンクマスター",
            "description": "XBRLのリンクマスター情報",
        },
    ]
    return {"categories": categories}


@app.get("/api/v1/xbrl/files")
async def get_xbrl_files(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    head_item_key: Optional[str] = None,
):
    """XBRLファイルの一覧を取得"""
    try:
        data_dir = Path(settings.resolved_data_path)
        zip_files = list(data_dir.glob("*.zip"))

        # フィルタリング
        if head_item_key:
            # head_item_keyでフィルタ（簡易実装）
            zip_files = [f for f in zip_files if head_item_key in f.name]

        # ページネーション
        total = len(zip_files)
        pages = (total + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit
        paginated_files = zip_files[start:end]

        # ファイル情報を構築
        files_data = []
        for zip_file in paginated_files:
            # head_item_keyを計算
            head_item_key = str(Utils.string_to_uuid(zip_file.name))
            files_data.append(
                {
                    "head_item_key": head_item_key,
                    "zip_file_name": zip_file.name,
                    "file_path": str(zip_file),
                }
            )

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
        logger.error(f"Failed to get xbrl files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/xbrl/files/{head_item_key}")
async def get_xbrl_file_info(head_item_key: str):
    """特定のXBRLファイルのメタ情報を取得"""
    try:
        model = get_xbrl_model(head_item_key)
        if not model:
            raise HTTPException(status_code=404, detail="XBRLファイルが見つかりません")

        items = model.get_all_items()
        data_dict = {item.key: item.item for item in items}

        # ファイルパス情報
        file_path = data_dict.get("ix_file_path", [{}])[0] if data_dict.get("ix_file_path") else {}
        header = data_dict.get("ix_head_title", [{}])[0] if data_dict.get("ix_head_title") else {}

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
    categories: Optional[str] = Query(None, description="取得するカテゴリ（カンマ区切り）"),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    """XBRLデータを取得"""
    try:
        model = get_xbrl_model(head_item_key)
        if not model:
            raise HTTPException(status_code=404, detail="XBRLファイルが見つかりません")

        # データを取得
        items = model.get_all_items()
        data_dict = {item.key: item.item for item in items}

        # 統合元のデータ、リンクデータ、スキーマ情報を除外
        excluded_categories = [
            "ix_non_fraction",
            "ix_non_numeric",  # 統合元データ
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
            "sc_source_file",  # スキーマ情報
        ]

        data_dict = {k: v for k, v in data_dict.items() if k not in excluded_categories}

        # カテゴリでフィルタ
        if categories:
            category_list = [c.strip() for c in categories.split(",")]
            data_dict = {k: v for k, v in data_dict.items() if k in category_list}

        return {
            "head_item_key": head_item_key,
            "data": data_dict,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get xbrl data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def format_qualitative_info_hierarchical(qualitative_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """qualitative_infoを親子関係に基づいて階層構造に変換
    
    Args:
        qualitative_data: qualitative_infoのデータリスト
        
    Returns:
        階層構造化されたデータ [{title: str, content: List[str]}, ...]
    """
    if not qualitative_data:
        return []
    
    # currentIdをキーとした辞書を作成（高速検索用）
    items_by_id: Dict[str, Dict[str, Any]] = {}
    for item in qualitative_data:
        current_id = item.get("currentId")
        if current_id:
            items_by_id[current_id] = item
    
    def collect_children_content(parent_id: str) -> List[str]:
        """親IDに紐づくすべてのコンテンツを再帰的に収集"""
        contents = []
        
        # 直接の子要素を取得
        child_items = [
            item for item in qualitative_data 
            if item.get("parentId") == parent_id
        ]
        child_items.sort(key=lambda x: x.get("order", 0))
        
        for child_item in child_items:
            child_type = child_item.get("type", "")
            child_content = child_item.get("content", "")
            child_id = child_item.get("currentId")
            
            if child_type == "content":
                # contentタイプの場合はそのまま追加
                contents.append(child_content)
            elif child_type in ["sub_title", "heading"]:
                # sub_titleやheadingの場合は、そのコンテンツも含めて、さらに子要素を再帰的に収集
                contents.append(child_content)
                # 子要素を再帰的に収集
                contents.extend(collect_children_content(child_id))
            else:
                # その他のタイプも再帰的に収集
                contents.extend(collect_children_content(child_id))
        
        return contents
    
    # ルート要素（parentIdがNone、typeがtitle）を探す
    root_items = [
        item for item in qualitative_data 
        if item.get("parentId") is None and item.get("type") == "title"
    ]
    
    # orderでソート
    root_items.sort(key=lambda x: x.get("order", 0))
    
    result: List[Dict[str, Any]] = []
    
    for root_item in root_items:
        title = root_item.get("content", "")
        current_id = root_item.get("currentId")
        
        # 子要素のコンテンツを再帰的に収集
        content_list = collect_children_content(current_id)
        
        result.append({
            "title": title,
            "content": content_list if content_list else []
        })
    
    return result


@app.get("/api/v1/xbrl/files/{head_item_key}/data/{category}")
async def get_xbrl_category_data(
    head_item_key: str,
    category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
):
    """特定のカテゴリのデータを取得"""
    try:
        model = get_xbrl_model(head_item_key)
        if not model:
            raise HTTPException(status_code=404, detail="XBRLファイルが見つかりません")

        items = model.get_all_items()
        data_dict = {item.key: item.item for item in items}

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

        if category not in data_dict:
            raise HTTPException(status_code=404, detail=f"カテゴリ '{category}' が見つかりません")

        category_data = data_dict[category]
        if not isinstance(category_data, list):
            category_data = [category_data]

        # qualitative_infoの場合は階層構造に変換
        if category == "qualitative_info":
            category_data = format_qualitative_info_hierarchical(category_data)

        # ページネーション
        total = len(category_data)
        pages = (total + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit
        paginated_data = category_data[start:end]

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
    """メタデータを取得"""
    try:
        model = get_xbrl_model(head_item_key)
        if not model:
            raise HTTPException(status_code=404, detail="XBRLファイルが見つかりません")

        items = model.get_all_items()
        data_dict = {item.key: item.item for item in items}

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
