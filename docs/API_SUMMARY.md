# REST API エンドポイント サマリー

## 提供されるデータカテゴリ

### 統合データ（推奨）
- `ix_non_fraction_enriched` - 非分数データ（ラベル・計算・定義・表示リンク統合済み）
- `ix_non_numeric_enriched` - 非数値データ（ラベル・計算・定義・表示リンク統合済み）

### 基本データ
- `ix_context` - iXBRLコンテキスト情報
- `ix_head_title` - iXBRLヘッダータイトル
- `ix_file_path` - iXBRLファイルパス
- `ix_source_file` - iXBRLソースファイル情報

### その他
- `qualitative_info` - 定性情報
- `qualitative_source_file` - 定性情報ソースファイル
- `href_master` - リンクマスター情報

## 提供されないデータカテゴリ

以下のカテゴリは統合データに含まれているため、個別には提供されません：

### 統合元データ（削除）
- `ix_non_fraction` → `ix_non_fraction_enriched`に統合
- `ix_non_numeric` → `ix_non_numeric_enriched`に統合

### リンクデータ（削除）
- `cal_*` (計算リンク) → 統合データの`calculation_links`に含まれる
- `def_*` (定義リンク) → 統合データの`definition_links`に含まれる
- `pre_*` (表示リンク) → 統合データの`presentation_links`に含まれる
- `lab_*` (ラベルリンク) → 統合データの`labels`に含まれる

### スキーマ情報（削除）
- `sc_elements` - XBRLスキーマの要素定義（通常のデータ取得では不要）
- `sc_import` - XBRLスキーマのインポート情報（通常のデータ取得では不要）
- `sc_linkbase_ref` - XBRLスキーマのリンクベース参照（通常のデータ取得では不要）
- `sc_source_file` - XBRLスキーマのソースファイル情報（通常のデータ取得では不要）

## データカテゴリ数

- **提供されるカテゴリ**: 9個
- **削除されたカテゴリ**: 22個
  - 統合元データ: 2個
  - リンクデータ: 16個
  - スキーマ情報: 4個
- **合計**: 31個（統合データ2個を含む）

## 推奨される使用方法

1. **統合データを使用**: `ix_non_fraction_enriched`と`ix_non_numeric_enriched`を使用することで、ラベルやリンク情報を個別に取得する必要がありません。

2. **必要な情報のみ取得**: `categories`パラメータを使用して、必要なカテゴリのみを取得することで、レスポンスサイズを削減できます。

3. **ページネーション**: 大量のデータを取得する場合は、ページネーションを使用してください。
