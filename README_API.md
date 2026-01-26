# FastAPI REST API

このプロジェクトには、XBRLデータを配信するためのFastAPIアプリケーションが含まれています。

## クイックスタート

### Docker Composeを使用（推奨）

```bash
# APIコンテナをビルド
make build-api

# APIコンテナを起動
make up-api

# ログを確認
make logs-api
```

APIは `http://localhost:8000` で利用可能です。

### ローカルで起動

```bash
# 依存関係をインストール
uv pip install -e .

# FastAPIアプリケーションを起動
uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

## APIドキュメント

起動後、以下のURLでAPIドキュメントにアクセスできます：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 主要エンドポイント

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

### XBRLファイル一覧

```bash
curl http://localhost:8000/api/v1/xbrl/files
```

### 特定ファイルのデータ取得

```bash
# head_item_keyを指定してデータを取得
curl http://localhost:8000/api/v1/xbrl/files/{head_item_key}/data
```

詳細な使用方法は [docs/API_USAGE.md](docs/API_USAGE.md) を参照してください。

## テスト

JSON出力テストを実行：

```bash
# ローカルで実行
.venv/bin/python src/tests/test_xbrl_json_output.py

# Dockerで実行
docker-compose run --rm stock-link-parser python src/tests/test_xbrl_json_output.py
```

テスト結果は `src/tests/output/` に保存されます。

## トラブルシューティング

### APIが起動しない

1. ポート8000が使用されていないか確認
2. ログを確認: `make logs-api`
3. コンテナの状態を確認: `docker-compose ps`

### データが見つからない

1. `XBRL_DATA_PATH` 環境変数が正しく設定されているか確認
2. データディレクトリにzipファイルが存在するか確認
