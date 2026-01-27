# データベースクイックスタートガイド

## 前提条件

- Docker Desktopが起動していること
- `.env`ファイルにデータベース設定が記述されていること

## クイックスタート

### 1. PostgreSQLコンテナの起動

```bash
make up-db
```

### 2. データベーススキーマの作成

```bash
make recreate-db-schema
```

このコマンドは以下を自動的に実行します：
- PostgreSQLコンテナの起動（未起動の場合）
- 既存テーブルの削除
- サンプルzipファイルからスキーマの自動生成

### 3. データのインポート

```bash
make import-to-db
```

このコマンドは以下を自動的に実行します：
- PostgreSQLコンテナの起動（未起動の場合）
- データディレクトリ内のすべてのzipファイルをデータベースにインポート

## 環境に応じた設定

### コンテナ環境で実行する場合

`.env`ファイルの設定：
```env
XBRL_DB_HOST=postgres
```

### ローカル環境で実行する場合

`.env`ファイルの設定：
```env
XBRL_DB_HOST=localhost
```

**注意**: スクリプトは自動的に`postgres`ホスト名が解決できない場合、`localhost`にフォールバックします。

## トラブルシューティング

### PostgreSQLコンテナが起動しない

```bash
# Docker Desktopが起動しているか確認
docker ps

# PostgreSQLコンテナのログを確認
make logs-db
```

### 接続エラーが発生する

1. **コンテナが起動しているか確認**:
   ```bash
   docker-compose ps postgres
   ```

2. **コンテナのログを確認**:
   ```bash
   make logs-db
   ```

3. **手動で接続テスト**:
   ```bash
   make psql
   ```

### データベースをリセットする

```bash
# コンテナとボリュームを削除
docker-compose down -v

# 再起動
make up-db

# スキーマを再作成
make recreate-db-schema
```
