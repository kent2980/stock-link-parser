# REST API エンドポイント設計

このドキュメントは、XBRLデータを配信するためのREST APIエンドポイント設計です。

## ベースURL

```
https://api.example.com/api/v1
```

## 認証

すべてのエンドポイントは認証が必要です（JWT、API Keyなど）。

## エンドポイント一覧

### 1. ヘルスチェック・メタ情報

#### `GET /health`
APIの稼働状況を確認

**レスポンス:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-27T06:00:00Z"
}
```

#### `GET /`
APIの基本情報と利用可能なエンドポイント一覧

**レスポンス:**
```json
{
  "name": "XBRL Data API",
  "version": "1.0.0",
  "endpoints": {
    "xbrl_files": "/api/v1/xbrl/files",
    "xbrl_data": "/api/v1/xbrl/data",
    "categories": "/api/v1/xbrl/categories"
  }
}
```

---

### 2. XBRLファイル管理

#### `GET /xbrl/files`
XBRLファイルの一覧を取得

**クエリパラメータ:**
- `page` (int, default: 1): ページ番号
- `limit` (int, default: 20, max: 100): 1ページあたりの件数
- `head_item_key` (string, optional): ヘッドアイテムキーでフィルタ
- `xbrl_category` (string, optional): XBRLカテゴリでフィルタ
- `date_from` (date, optional): 開始日
- `date_to` (date, optional): 終了日
- `sort` (string, default: "created_at"): ソート項目 (created_at, head_item_key, xbrl_category)

**レスポンス:**
```json
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5,
  "data": [
    {
      "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
      "xbrl_category": "fr",
      "zip_file_name": "081220250911556517.zip",
      "created_at": "2026-01-27T06:00:00Z",
      "updated_at": "2026-01-27T06:00:00Z"
    }
  ]
}
```

#### `GET /xbrl/files/{head_item_key}`
特定のXBRLファイルのメタ情報を取得

**レスポンス:**
```json
{
  "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
  "xbrl_category": "fr",
  "zip_file_name": "081220250911556517.zip",
  "file_path": {
    "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
    "path": "/path/to/file.zip"
  },
  "header": {
    "company_name": "株式会社サンプル",
    "securities_code": "1234",
    "document_name": "有価証券報告書",
    "reporting_date": "2025-03-31"
  },
  "created_at": "2026-01-27T06:00:00Z",
  "updated_at": "2026-01-27T06:00:00Z"
}
```

---

### 3. XBRLデータ取得

#### `GET /xbrl/files/{head_item_key}/data`
特定のXBRLファイルの全データを取得

**クエリパラメータ:**
- `categories` (string[], optional): 取得するカテゴリ（カンマ区切り）
  - 例: `categories=ix_non_fraction_enriched,ix_non_numeric_enriched,ix_context`
- `format` (string, default: "json"): レスポンス形式 (json, csv)

**レスポンス:**
```json
{
  "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
  "xbrl_category": "fr",
  "data": {
    "ix_non_fraction_enriched": [...],
    "ix_non_numeric_enriched": [...],
    "ix_context": [...],
    ...
  }
}
```

#### `GET /xbrl/files/{head_item_key}/data/{category}`
特定のカテゴリのデータを取得

**パスパラメータ:**
- `category`: データカテゴリ
  - `ix_non_fraction_enriched`, `ix_non_numeric_enriched` (統合データ - ラベル・リンク情報統合済み)
  - `ix_context`, `ix_head_title`, `ix_file_path`, `ix_source_file`
  - `qualitative_info`, `qualitative_source_file`
  - `href_master`
  
  **注意**: 
  - `ix_non_fraction`と`ix_non_numeric`は統合データ（`ix_non_fraction_enriched`、`ix_non_numeric_enriched`）に置き換えられています。
  - `cal_*`、`def_*`、`pre_*`、`lab_*`のリンク情報は統合データに含まれているため、個別には提供されていません。
  - `sc_*`（スキーマ情報）はXBRLの構造定義メタデータのため、通常のデータ取得では不要です。

**クエリパラメータ:**
- `page` (int, default: 1): ページ番号
- `limit` (int, default: 100, max: 1000): 1ページあたりの件数
- `filter` (object, optional): フィルタ条件（JSON形式）

**レスポンス:**
```json
{
  "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
  "category": "ix_non_fraction_enriched",
  "total": 237,
  "page": 1,
  "limit": 100,
  "data": [...]
}
```

---

### 4. 検索・フィルタリング

#### `GET /xbrl/search`
XBRLデータを検索

**クエリパラメータ:**
- `q` (string, required): 検索クエリ
- `category` (string, optional): 検索対象カテゴリ
- `field` (string, optional): 検索対象フィールド（name, value, label等）
- `head_item_key` (string, optional): 特定のファイルに限定
- `page` (int, default: 1)
- `limit` (int, default: 20, max: 100)

**レスポンス:**
```json
{
  "query": "ProfitLoss",
  "total": 15,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
      "category": "ix_non_fraction_enriched",
      "item": {...},
      "score": 0.95
    }
  ]
}
```

#### `GET /xbrl/filter`
高度なフィルタリング

**クエリパラメータ:**
- `head_item_key` (string[], optional): 複数のヘッドアイテムキー
- `xbrl_category` (string[], optional): 複数のカテゴリ
- `date_from` (date, optional)
- `date_to` (date, optional)
- `name` (string, optional): 要素名
- `context` (string[], optional): コンテキスト
- `report_type` (string[], optional): レポートタイプ
- `page` (int, default: 1)
- `limit` (int, default: 20, max: 100)

---

### 5. カテゴリ・メタデータ

#### `GET /xbrl/categories`
利用可能なデータカテゴリ一覧

**レスポンス:**
```json
{
  "categories": [
    {
      "name": "ix_non_fraction_enriched",
      "display_name": "iXBRL非分数データ（統合版）",
      "description": "iXBRLの非分数値データ（ラベル・計算・定義・表示リンク情報統合済み）",
      "count": 237
    },
    {
      "name": "ix_non_numeric_enriched",
      "display_name": "iXBRL非数値データ（統合版）",
      "description": "iXBRLの非数値データ（ラベル・計算・定義・表示リンク情報統合済み）",
      "count": 90
    },
    {
      "name": "ix_context",
      "display_name": "iXBRLコンテキスト",
      "description": "iXBRLのコンテキスト情報",
      "count": 15
    },
    {
      "name": "ix_head_title",
      "display_name": "iXBRLヘッダータイトル",
      "description": "iXBRLのヘッダー情報",
      "count": 1
    },
    {
      "name": "ix_file_path",
      "display_name": "iXBRLファイルパス",
      "description": "iXBRLファイルのパス情報",
      "count": 1
    },
    {
      "name": "ix_source_file",
      "display_name": "iXBRLソースファイル",
      "description": "iXBRLのソースファイル情報",
      "count": 10
    },
    {
      "name": "qualitative_info",
      "display_name": "定性情報",
      "description": "XBRLの定性情報",
      "count": 50
    },
    {
      "name": "qualitative_source_file",
      "display_name": "定性情報ソースファイル",
      "description": "定性情報のソースファイル情報",
      "count": 5
    },
    {
      "name": "href_master",
      "display_name": "リンクマスター",
      "description": "XBRLのリンクマスター情報",
      "count": 100
    }
  ]
}
```

#### `GET /xbrl/files/{head_item_key}/metadata`
メタデータを取得

**レスポンス:**
```json
{
  "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
  "header": {
    "company_name": "株式会社サンプル",
    "securities_code": "1234",
    "document_name": "有価証券報告書",
    "reporting_date": "2025-03-31"
  },
  "statistics": {
    "ix_non_fraction_enriched_count": 237,
    "ix_non_numeric_enriched_count": 90,
    "ix_context_count": 15,
    "total_categories": 9
  },
  "source_files": [...]
}
```

---

### 6. 統計・集計

#### `GET /xbrl/statistics`
全体統計情報

**クエリパラメータ:**
- `group_by` (string, optional): グループ化項目 (category, date, company)

**レスポンス:**
```json
{
  "total_files": 1000,
  "total_items": 50000,
  "categories": {
    "ix_non_fraction_enriched": 25000,
    "ix_non_numeric_enriched": 10000,
    ...
  },
  "date_range": {
    "from": "2024-01-01",
    "to": "2025-12-31"
  }
}
```

#### `GET /xbrl/files/{head_item_key}/statistics`
特定ファイルの統計情報

**レスポンス:**
```json
{
  "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
  "item_counts": {
    "ix_non_fraction_enriched": 237,
    "ix_non_numeric_enriched": 90,
    ...
  },
  "link_counts": {
    "calculation_links": 50,
    "definition_links": 30,
    "presentation_links": 40,
    "label_links": 200
  },
  "note": "リンク情報は統合データ（ix_non_fraction_enriched、ix_non_numeric_enriched）に含まれています"
}
```

---

### 7. エクスポート

#### `GET /xbrl/files/{head_item_key}/export`
データをエクスポート

**クエリパラメータ:**
- `format` (string, required): エクスポート形式 (`json`, `csv`, `xlsx`)
- `categories` (string[], optional): エクスポートするカテゴリ

**レスポンス:**
- JSON: JSON形式のデータ
- CSV: CSVファイル（ダウンロード）
- XLSX: Excelファイル（ダウンロード）

---

## エラーレスポンス

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
- `401 Unauthorized`: 認証が必要
- `403 Forbidden`: アクセス権限がない
- `404 Not Found`: リソースが見つからない
- `422 Unprocessable Entity`: バリデーションエラー
- `500 Internal Server Error`: サーバーエラー
- `503 Service Unavailable`: サービスが利用不可

---

## レート制限

- 認証済みユーザー: 1000リクエスト/時間
- 匿名ユーザー: 100リクエスト/時間

レスポンスヘッダー:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## ページネーション

ページネーション対応エンドポイントは以下の形式：

**リクエスト:**
```
GET /api/v1/xbrl/files?page=2&limit=20
```

**レスポンス:**
```json
{
  "total": 100,
  "page": 2,
  "limit": 20,
  "pages": 5,
  "has_next": true,
  "has_prev": true,
  "data": [...]
}
```

---

## バージョニング

APIバージョンはURLパスに含まれます：
- `/api/v1/...` - バージョン1（現在）

将来のバージョンは `/api/v2/...` として提供されます。
