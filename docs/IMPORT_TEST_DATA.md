# テストデータのインポート

このドキュメントでは、テストで生成したJSONデータをインポートする方法を説明します。

## 概要

`src/tests/import_test_data.py`スクリプトを使用して、テストで生成したJSONファイルと対応するzipファイルをインポートできます。

## インポート先

### 1. データディレクトリ (`data_dir`)

テストデータのzipファイルを`data/`ディレクトリにコピーします。これにより、FastAPIアプリケーションやその他の処理でzipファイルを直接使用できます。

```bash
# Makefileを使用
make import-test-data

# または直接実行
.venv/bin/python src/tests/import_test_data.py --target data_dir
```

### 2. FastAPIキャッシュ (`fastapi_cache`)

テストデータをFastAPIアプリケーションのメモリキャッシュに直接読み込みます。これにより、API起動時にデータがすぐに利用可能になります。

```bash
# Makefileを使用
make import-test-data-fastapi

# または直接実行
.venv/bin/python src/tests/import_test_data.py --target fastapi_cache
```

**注意**: FastAPIキャッシュへのインポートは、FastAPIアプリケーションが起動している場合のみ有効です。

### 3. 両方 (`both`)

データディレクトリとFastAPIキャッシュの両方にインポートします。

```bash
# Makefileを使用
make import-test-data-both

# または直接実行
.venv/bin/python src/tests/import_test_data.py --target both
```

## オプション

### JSONディレクトリの指定

デフォルトでは`src/tests/output/`からJSONファイルを読み込みますが、別のディレクトリを指定できます。

```bash
.venv/bin/python src/tests/import_test_data.py \
    --target data_dir \
    --json-dir /path/to/json/files
```

### データディレクトリの指定

デフォルトでは`data/`ディレクトリ（または`XBRL_XBRL_DATA_PATH`環境変数で指定されたディレクトリ）にインポートしますが、別のディレクトリを指定できます。

```bash
.venv/bin/python src/tests/import_test_data.py \
    --target data_dir \
    --data-dir /path/to/data/directory
```

### zipファイルのコピーをスキップ

zipファイルをコピーせずに、JSONファイルの情報のみを処理します。

```bash
.venv/bin/python src/tests/import_test_data.py \
    --target data_dir \
    --no-copy-zip
```

## インポートされるファイル

以下のファイルがインポート対象です：

- `src/tests/output/*.json` - テストで生成されたJSONファイル
- `src/tests/data/*.zip` - 対応するzipファイル

**除外されるファイル**:
- `test_summary.json`
- `*_enriched.json`
- `key_*.json`
- `output_keys_*.json`
- `web_app_formatted_sample.json`

## インポート結果

インポートが完了すると、以下の情報が表示されます：

- 総ファイル数
- インポート成功件数
- スキップ件数
- エラー件数
- インポート成功ファイルの詳細（head_item_key、xbrl_categoryなど）

## 使用例

### 基本的な使用

```bash
# データディレクトリにインポート
make import-test-data
```

### FastAPIと連携

```bash
# 1. データディレクトリにインポート
make import-test-data

# 2. FastAPIを起動
make up-api

# 3. APIでデータを確認
curl http://localhost:8000/api/v1/xbrl/files
```

## トラブルシューティング

### zipファイルが見つからない

対応するzipファイルが`src/tests/data/`に存在しない場合、そのJSONファイルはスキップされます。

### head_item_keyが見つからない

JSONファイルに`head_item_key`が含まれていない場合、そのファイルはスキップされます。

### 既存ファイルの上書き

既にzipファイルが存在する場合、コピーはスキップされます（既存ファイルは保持されます）。
