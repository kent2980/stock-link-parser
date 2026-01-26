# REST API 実装ガイド

このドキュメントは、REST APIエンドポイントの実装例と推奨事項を記載しています。

## 推奨フレームワーク

- **FastAPI** (推奨): モダンで高速、自動ドキュメント生成
- **Flask**: シンプルで軽量
- **Django REST Framework**: フル機能が必要な場合

## FastAPI実装例

### 基本的な構造

```python
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from pydantic import BaseModel
from src.ix_models.xbrl_model import XBRLModel
from src.config import settings

app = FastAPI(
    title="XBRL Data API",
    version="1.0.0",
    description="XBRLデータを配信するREST API"
)

# データモデル
class XBRLFileInfo(BaseModel):
    head_item_key: str
    xbrl_category: str
    zip_file_name: str
    created_at: str
    updated_at: str

class XBRLDataResponse(BaseModel):
    head_item_key: str
    xbrl_category: str
    data: dict

# エンドポイント実装例
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/xbrl/files/{head_item_key}/data")
async def get_xbrl_data(
    head_item_key: str = Path(..., description="ヘッドアイテムキー"),
    categories: Optional[List[str]] = Query(None, description="取得するカテゴリ"),
    format: str = Query("json", regex="^(json|csv)$")
):
    """XBRLデータを取得"""
    try:
        # XBRLModelのインスタンスを作成（キャッシュから取得）
        model = get_xbrl_model(head_item_key)
        
        if not model:
            raise HTTPException(status_code=404, detail="XBRLファイルが見つかりません")
        
        # データを取得
        data_class = model.get_all_items_as_dataclass()
        data_dict = dataclass_to_dict(data_class)
        
        # 統合元のデータ、リンクデータ、スキーマ情報を除外（統合後のデータのみを提供）
        # 除外するカテゴリ:
        # - ix_non_fraction, ix_non_numeric (統合データに置き換え)
        # - cal_*, def_*, pre_*, lab_* (統合データに含まれているため不要)
        # - sc_* (スキーマ情報は通常のデータ取得では不要)
        excluded_categories = [
            "ix_non_fraction", "ix_non_numeric",  # 統合元データ
            "cal_link_arcs", "cal_link_locs", "cal_link_roles", "cal_source_file",
            "def_link_arcs", "def_link_locs", "def_link_roles", "def_source_file",
            "pre_link_arcs", "pre_link_locs", "pre_link_roles", "pre_source_file",
            "lab_link_arcs", "lab_link_locs", "lab_link_values", "lab_source_file",
            "sc_elements", "sc_import", "sc_linkbase_ref", "sc_source_file",  # スキーマ情報
        ]
        
        data_dict = {
            k: v for k, v in data_dict.items() 
            if k not in excluded_categories
        }
        
        # 統合後のデータが存在することを確認
        if "ix_non_fraction_enriched" not in data_dict:
            logger.warning(f"ix_non_fraction_enriched not found for {head_item_key}")
        if "ix_non_numeric_enriched" not in data_dict:
            logger.warning(f"ix_non_numeric_enriched not found for {head_item_key}")
        
        # カテゴリでフィルタ
        if categories:
            data_dict = {k: v for k, v in data_dict.items() if k in categories}
        
        response = XBRLDataResponse(
            head_item_key=head_item_key,
            xbrl_category=model.xbrl_category,
            data=data_dict
        )
        
        if format == "csv":
            # CSV形式でエクスポート
            return export_to_csv(response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## キャッシュ戦略

```python
from functools import lru_cache
from pathlib import Path

# XBRLModelのキャッシュ
_xbrl_model_cache = {}

def get_xbrl_model(head_item_key: str) -> Optional[XBRLModel]:
    """XBRLModelを取得（キャッシュから）"""
    if head_item_key in _xbrl_model_cache:
        return _xbrl_model_cache[head_item_key]
    
    # ファイルを検索
    zip_file = find_zip_file_by_head_item_key(head_item_key)
    if not zip_file:
        return None
    
    # モデルを作成
    model = XBRLModel(
        xbrl_zip_path=zip_file,
        output_path=settings.resolved_output_path
    )
    
    # キャッシュに保存
    _xbrl_model_cache[head_item_key] = model
    
    return model
```

## データベース連携

既存のデータベースからデータを取得する場合：

```python
from src.connect.postgre_sql_connector import PostgreSqlConnector

@app.get("/xbrl/files")
async def list_xbrl_files(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    head_item_key: Optional[str] = None
):
    """XBRLファイル一覧を取得"""
    db = PostgreSqlConnector()
    
    query = "SELECT * FROM xbrl_files WHERE 1=1"
    params = []
    
    if head_item_key:
        query += " AND head_item_key = %s"
        params.append(head_item_key)
    
    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, (page - 1) * limit])
    
    results = db.execute_query(query, params)
    
    return {
        "total": get_total_count(),
        "page": page,
        "limit": limit,
        "data": results
    }
```

## 認証・認可

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """トークンを検証"""
    token = credentials.credentials
    # トークン検証ロジック
    if not is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token

@app.get("/xbrl/files/{head_item_key}/data")
async def get_xbrl_data(
    head_item_key: str,
    token: str = Depends(verify_token)
):
    # 認証済みユーザーのみアクセス可能
    ...
```

## レート制限

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/xbrl/files")
@limiter.limit("1000/hour")
async def list_xbrl_files(request: Request):
    ...
```

## エラーハンドリング

```python
from src.exception.base_exception import XBRLBaseException

@app.exception_handler(XBRLBaseException)
async def xbrl_exception_handler(request: Request, exc: XBRLBaseException):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.error_code.name,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "内部サーバーエラーが発生しました"
            }
        }
    )
```

## テスト

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_xbrl_data():
    response = client.get("/xbrl/files/test-key/data")
    assert response.status_code == 200
    assert "data" in response.json()
```
