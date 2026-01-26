# FastAPI 使用方法

## 概要

このプロジェクトには、XBRLデータを配信するためのFastAPIアプリケーションが含まれています。

## 起動方法

### Docker Composeを使用する場合（推奨）

```bash
# APIコンテナを起動
docker-compose up api

# バックグラウンドで起動
docker-compose up -d api
```

APIは `http://localhost:8000` で利用可能です。

### ローカルで起動する場合

```bash
# 依存関係をインストール
uv pip install -e .

# FastAPIアプリケーションを起動
uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

## エンドポイント一覧

### 基本エンドポイント

#### `GET /`
APIの基本情報と利用可能なエンドポイント一覧

```bash
curl http://localhost:8000/
```

#### `GET /health`
ヘルスチェック

```bash
curl http://localhost:8000/health
```

### XBRLデータエンドポイント

#### `GET /api/v1/xbrl/head-item-key`
zipファイル名からhead_item_keyを取得

```bash
# zipファイル名を指定
curl "http://localhost:8000/api/v1/xbrl/head-item-key?zip_file_name=081220250911556517.zip"
```

**レスポンス:**
```json
{
  "zip_file_name": "081220250911556517.zip",
  "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2"
}
```

#### `GET /api/v1/xbrl/head-item-keys`
すべてのhead_item_keyの一覧を取得（パラメータなし）

```bash
curl http://localhost:8000/api/v1/xbrl/head-item-keys
```

**レスポンス:**
```json
{
  "total": 5,
  "head_item_keys": [
    {
      "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
      "zip_file_name": "081220250911556517.zip"
    },
    {
      "head_item_key": "0c31f99d-0861-e260-6185-f8b5b063bfd1",
      "zip_file_name": "081220250921560488.zip"
    }
  ]
}
```

#### `GET /api/v1/xbrl/categories`
利用可能なデータカテゴリ一覧

```bash
curl http://localhost:8000/api/v1/xbrl/categories
```

#### `GET /api/v1/xbrl/files`
XBRLファイルの一覧を取得

```bash
# 基本
curl http://localhost:8000/api/v1/xbrl/files

# ページネーション
curl "http://localhost:8000/api/v1/xbrl/files?page=1&limit=20"
```

**レスポンス:**
```json
{
  "total": 5,
  "page": 1,
  "limit": 20,
  "pages": 1,
  "has_next": false,
  "has_prev": false,
  "data": [
    {
      "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
      "zip_file_name": "081220250911556517.zip",
      "file_path": "/app/data/081220250911556517.zip"
    }
  ]
}
```

#### `GET /api/v1/xbrl/files/{head_item_key}`
特定のXBRLファイルのメタ情報を取得

```bash
curl http://localhost:8000/api/v1/xbrl/files/3454ba2c-fdea-12f3-a27a-083f6447e3b2
```

#### `GET /api/v1/xbrl/files/{head_item_key}/data`
特定のXBRLファイルの全データを取得

```bash
# 全データ
curl http://localhost:8000/api/v1/xbrl/files/3454ba2c-fdea-12f3-a27a-083f6447e3b2/data

# 特定のカテゴリのみ
curl "http://localhost:8000/api/v1/xbrl/files/3454ba2c-fdea-12f3-a27a-083f6447e3b2/data?categories=ix_non_fraction_enriched,ix_non_numeric_enriched"
```

#### `GET /api/v1/xbrl/files/{head_item_key}/data/{category}`
特定のカテゴリのデータを取得

```bash
# ix_non_fraction_enrichedを取得
curl "http://localhost:8000/api/v1/xbrl/files/3454ba2c-fdea-12f3-a27a-083f6447e3b2/data/ix_non_fraction_enriched?page=1&limit=100"

# ix_contextを取得
curl "http://localhost:8000/api/v1/xbrl/files/3454ba2c-fdea-12f3-a27a-083f6447e3b2/data/ix_context"
```

#### `GET /api/v1/xbrl/files/{head_item_key}/metadata`
メタデータを取得

```bash
curl http://localhost:8000/api/v1/xbrl/files/3454ba2c-fdea-12f3-a27a-083f6447e3b2/metadata
```

## 利用可能なカテゴリ

以下のカテゴリが利用可能です：

- `ix_non_fraction_enriched`: iXBRL非分数データ（統合版）
- `ix_non_numeric_enriched`: iXBRL非数値データ（統合版）
- `ix_context`: iXBRLコンテキスト
- `ix_head_title`: iXBRLヘッダータイトル
- `ix_file_path`: iXBRLファイルパス
- `ix_source_file`: iXBRLソースファイル
- `qualitative_info`: 定性情報
- `qualitative_source_file`: 定性情報ソースファイル
- `href_master`: リンクマスター

**注意**: 以下のカテゴリは統合データに含まれているため、個別には提供されていません：
- `ix_non_fraction`, `ix_non_numeric` (統合データに置き換え)
- `cal_*`, `def_*`, `pre_*`, `lab_*` (統合データに含まれているため不要)
- `sc_*` (スキーマ情報は通常のデータ取得では不要)

## APIドキュメント

FastAPIの自動生成ドキュメントにアクセスできます：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## エラーハンドリング

すべてのエンドポイントは以下の形式でエラーを返します：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": {}
  }
}
```

### HTTPステータスコード

- `200 OK`: 成功
- `400 Bad Request`: リクエストが不正
- `404 Not Found`: リソースが見つからない
- `500 Internal Server Error`: サーバーエラー

## 設定

環境変数で設定を変更できます：

- `XBRL_DATA_PATH`: XBRLファイルが格納されているディレクトリ（デフォルト: `./data`）
- `XBRL_OUTPUT_PATH`: 出力ディレクトリ（デフォルト: `./output`）

詳細は `.env.example` を参照してください。
