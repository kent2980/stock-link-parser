# Docker トラブルシューティング

## ネットワークエラーの解決方法

### エラー: `network ... not found`

このエラーは、Dockerネットワークが削除されたか、Docker Desktopが再起動された際に発生します。

### 解決方法

#### 1. Docker Desktopを起動

まず、Docker Desktopが起動していることを確認してください。

#### 2. コンテナとネットワークをクリーンアップ

```bash
# すべてのコンテナを停止・削除
docker-compose down

# 未使用のネットワークを削除
docker network prune -f

# 必要に応じて、すべてのコンテナとネットワークを削除
docker-compose down -v
```

#### 3. 再起動

```bash
# APIコンテナを再起動
docker-compose up -d api

# または、すべてのサービスを起動
docker-compose up -d
```

#### 4. ログを確認

```bash
# APIコンテナのログを確認
docker-compose logs -f api
```

## 権限エラーの解決方法

### エラー: `permission denied while trying to connect to the Docker daemon socket`

このエラーは、Dockerデーモンに接続できないことを示しています。

### 解決方法

1. **Docker Desktopを起動**
   - Docker Desktopアプリケーションを起動してください
   - メニューバーにDockerアイコンが表示されていることを確認

2. **Docker Desktopの状態を確認**
   ```bash
   docker ps
   ```
   このコマンドが正常に実行できれば、Docker Desktopは正常に動作しています。

3. **権限の確認**
   - macOSの場合、Docker Desktopが起動していれば通常は問題ありません
   - Linuxの場合、ユーザーを`docker`グループに追加する必要がある場合があります

## コンテナが起動しない場合

### 1. イメージを再ビルド

```bash
# APIイメージを再ビルド
docker-compose build api

# コンテナを起動
docker-compose up -d api
```

### 2. キャッシュを無視して再ビルド

```bash
docker-compose build --no-cache api
docker-compose up -d api
```

### 3. 完全にクリーンアップして再ビルド

```bash
# コンテナとボリュームを削除
docker-compose down -v

# イメージを削除
docker rmi stock-link-parser-api:latest stock-link-parser:latest

# 再ビルド
docker-compose build
docker-compose up -d api
```

## ポートが既に使用されている場合

### エラー: `port 8000 is already allocated`

ポート8000が既に使用されている場合：

```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000

# または
netstat -an | grep 8000
```

解決方法：
1. 既存のプロセスを停止
2. `docker-compose.yml`でポート番号を変更

## よくある問題と解決方法

### 問題1: コンテナがすぐに停止する

```bash
# ログを確認
docker-compose logs api

# コンテナ内でコマンドを実行して確認
docker-compose exec api bash
```

### 問題2: ボリュームマウントが失敗する

- ホスト側のディレクトリが存在することを確認
- パスの権限を確認

### 問題3: 環境変数が読み込まれない

- `.env`ファイルが存在することを確認
- `.env`ファイルの形式が正しいことを確認

## ヘルスチェック

```bash
# APIのヘルスチェック
curl http://localhost:8000/health

# コンテナの状態を確認
docker-compose ps

# コンテナのリソース使用状況を確認
docker stats
```
