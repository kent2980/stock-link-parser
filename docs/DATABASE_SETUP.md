# データベースセットアップガイド

## 概要

このプロジェクトでは、PostgreSQLをDockerコンテナで実行する構成になっています。

## 構成

- **PostgreSQLコンテナ**: `postgres`サービスとして定義
- **データ永続化**: Dockerボリューム `postgres_data` を使用
- **ネットワーク**: `stock-link-network` 内で他のサービスと通信

## セットアップ手順

### 1. 環境変数の設定

`.env`ファイルにデータベース設定を追加してください：

```env
# データベースホスト（コンテナ実行時はpostgres、ローカル実行時はlocalhost）
XBRL_DB_HOST=postgres

# データベースポート
XBRL_DB_PORT=5432

# データベース名
XBRL_DB_DATABASE=xbrl

# データベースユーザー名
XBRL_DB_USERNAME=postgres

# データベースパスワード
XBRL_DB_PASSWORD=postgres
```

**注意**: 
- コンテナ内から接続する場合: `XBRL_DB_HOST=postgres`
- ローカル（ホスト）から接続する場合: `XBRL_DB_HOST=localhost`

### 2. PostgreSQLコンテナの起動

```bash
# PostgreSQLコンテナのみを起動
make up-db

# または、すべてのコンテナを起動
make up
```

### 3. データベーススキーマの作成

```bash
# サンプルzipファイルからスキーマを自動生成
make recreate-db-schema

# または、特定のzipファイルを指定
make recreate-db-schema-sample SAMPLE_ZIP=/path/to/file.zip
```

### 4. データのインポート

```bash
# データディレクトリ内のすべてのzipファイルをインポート
make import-to-db

# または、単一ファイルをインポート
make import-to-db-single ZIP_FILE=/path/to/file.zip
```

## 便利なコマンド

### PostgreSQLコンテナの操作

```bash
# PostgreSQLコンテナのログを表示
make logs-db

# PostgreSQLコンテナ内でシェルを起動
make shell-db

# PostgreSQLに接続（psql）
make psql
```

### データベースの確認

```bash
# psqlで接続してテーブル一覧を確認
make psql
# 接続後:
\dt

# 特定のテーブルのデータを確認
SELECT * FROM ix_head_title LIMIT 10;
```

## トラブルシューティング

### 接続エラーが発生する場合

1. **コンテナが起動しているか確認**:
   ```bash
   docker-compose ps
   ```

2. **PostgreSQLのログを確認**:
   ```bash
   make logs-db
   ```

3. **ホスト名の確認**:
   - コンテナ内から: `XBRL_DB_HOST=postgres`
   - ローカルから: `XBRL_DB_HOST=localhost`

### データベースをリセットする場合

```bash
# コンテナとボリュームを削除
docker-compose down -v

# 再起動
make up-db

# スキーマを再作成
make recreate-db-schema
```

## データベースボリューム

データはDockerボリューム `postgres_data` に保存されます。このボリュームを削除すると、すべてのデータが失われます。

```bash
# ボリュームを確認
docker volume ls | grep postgres

# ボリュームを削除（注意: すべてのデータが削除されます）
docker volume rm stock-link-parser_postgres_data
```
