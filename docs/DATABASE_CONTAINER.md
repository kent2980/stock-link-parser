# コンテナ内でのデータベース操作

PostgreSQLコンテナが起動している場合、コンテナ内からデータベース操作を実行することを推奨します。

## 前提条件

- PostgreSQLコンテナが起動していること
- `make up-db` または `docker-compose up -d postgres` でコンテナを起動

## コンテナ内でスキーマを再作成

```bash
make recreate-db-schema
```

このコマンドは、`stock-link-parser`コンテナ内でスクリプトを実行します。コンテナ内からは`postgres`ホスト名でPostgreSQLに接続できます。

## コンテナ内でデータをインポート

```bash
make import-to-db
```

このコマンドも、`stock-link-parser`コンテナ内でスクリプトを実行します。

## 手動でコンテナ内で実行

```bash
# スキーマ再作成
docker-compose run --rm stock-link-parser python src/scripts/create_database_schema.py --data-dir /app/data

# データインポート
docker-compose run --rm stock-link-parser python src/scripts/import_to_database.py
```

## トラブルシューティング

### コンテナが起動しない

```bash
# Docker Desktopが起動しているか確認
docker ps

# PostgreSQLコンテナのログを確認
make logs-db
```

### コンテナ内でPostgreSQLに接続できない

コンテナ内からは`postgres`ホスト名で接続できます。`.env`ファイルの設定を確認してください：

```env
XBRL_DB_HOST=postgres
```

コンテナ内では、このホスト名がDockerネットワーク内で解決されます。
