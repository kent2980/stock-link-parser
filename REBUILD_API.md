# FastAPIコンテナの再ビルド手順

コードを修正した後、Dockerコンテナを再ビルドする必要があります。

## 再ビルド手順

### 1. コンテナを停止

```bash
docker-compose down api
```

### 2. イメージを再ビルド

```bash
docker-compose build api
```

### 3. コンテナを起動

```bash
docker-compose up -d api
```

### 4. ログを確認

```bash
docker-compose logs -f api
```

## 一括実行

```bash
# 停止 → 再ビルド → 起動
docker-compose down api && docker-compose build api && docker-compose up -d api
```

## Makefileを使用

```bash
make restart-api
```

ただし、`restart-api`は再ビルドを含まないため、完全に再ビルドする場合は：

```bash
make down-api
make build-api
make up-api
```

## トラブルシューティング

### キャッシュを無視して再ビルド

```bash
docker-compose build --no-cache api
```

### コンテナとイメージを完全に削除してから再ビルド

```bash
docker-compose down api
docker rmi stock-link-parser-api:latest
docker-compose build api
docker-compose up -d api
```
