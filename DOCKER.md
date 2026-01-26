# Docker セットアップガイド

このプロジェクトをDockerコンテナで実行するためのガイドです。

## 前提条件

- Docker 20.10以上
- Docker Compose 2.0以上

## クイックスタート

### 1. 環境変数の設定

`.env`ファイルを作成し、必要な環境変数を設定します。

```bash
cp .env.example .env
# .envファイルを編集して必要な設定を追加
```

### 2. イメージのビルド

```bash
# 本番環境用
docker-compose build

# 開発環境用
docker-compose -f docker-compose.dev.yml build
```

### 3. コンテナの起動

```bash
# 本番環境用
docker-compose up -d

# 開発環境用
docker-compose -f docker-compose.dev.yml up -d
```

### 4. ログの確認

```bash
docker-compose logs -f
```

## 使用方法

### 基本的な実行

```bash
# コンテナ内でメインスクリプトを実行
docker-compose run --rm stock-link-parser python src/main.py /path/to/xbrl/data

# または、環境変数でデータパスを指定
docker-compose run --rm stock-link-parser
```

### 開発環境での使用

```bash
# 開発コンテナに入る
docker-compose -f docker-compose.dev.yml exec stock-link-parser-dev bash

# コンテナ内でテストを実行
docker-compose -f docker-compose.dev.yml run --rm stock-link-parser-dev pytest src/tests/

# コンテナ内でPythonインタラクティブシェルを起動
docker-compose -f docker-compose.dev.yml run --rm stock-link-parser-dev python
```

### カスタムコマンドの実行

```bash
# 任意のPythonスクリプトを実行
docker-compose run --rm stock-link-parser python src/insert_month.py arg1 arg2

# シェルコマンドを実行
docker-compose run --rm stock-link-parser bash -c "ls -la /app"
```

## ボリュームマウント

以下のディレクトリがマウントされています：

- `./data` → `/app/data` (読み取り専用): XBRLファイルなどの入力データ
- `./output` → `/app/output`: 処理結果の出力先
- `./logs` → `/app/logs`: ログファイル

## 環境変数

主要な環境変数：

- `XBRL_ENVIRONMENT`: 実行環境 (development, staging, production)
- `XBRL_API_BASE_URL`: APIのベースURL
- `XBRL_XBRL_DATA_PATH`: XBRLファイルのディレクトリパス
- `XBRL_OUTPUT_PATH`: 出力ディレクトリ
- `XBRL_LOG_LEVEL`: ログレベル (DEBUG, INFO, WARNING, ERROR)

詳細は`.env.example`を参照してください。

## トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker-compose logs stock-link-parser

# コンテナの状態を確認
docker-compose ps
```

### 依存関係のエラー

```bash
# イメージを再ビルド
docker-compose build --no-cache
```

### 権限エラー

```bash
# 出力ディレクトリの権限を確認
ls -la output/
# 必要に応じて権限を変更
chmod -R 777 output/
```

### ネットワークエラー

```bash
# ネットワークを再作成
docker-compose down
docker-compose up -d
```

## 本番環境へのデプロイ

### イメージのタグ付け

```bash
docker build -t stock-link-parser:latest .
docker tag stock-link-parser:latest your-registry/stock-link-parser:v1.0.0
```

### イメージのプッシュ

```bash
docker push your-registry/stock-link-parser:v1.0.0
```

### 本番環境での実行

```bash
# 環境変数を設定
export XBRL_ENVIRONMENT=production
export XBRL_API_BASE_URL=https://api.example.com

# コンテナを起動
docker run -d \
  --name stock-link-parser \
  --env-file .env.production \
  -v /path/to/data:/app/data:ro \
  -v /path/to/output:/app/output \
  -v /path/to/logs:/app/logs \
  stock-link-parser:latest
```

## 開発環境のセットアップ

開発環境では、ホットリロード対応のため、ソースコードが直接マウントされます。

```bash
# 開発コンテナを起動
docker-compose -f docker-compose.dev.yml up -d

# コンテナに入る
docker-compose -f docker-compose.dev.yml exec stock-link-parser-dev bash

# コンテナ内で開発作業
cd /app
python src/main.py
```

## リソース制限

デフォルトのリソース制限：

- CPU: 最大2コア、最小1コア
- メモリ: 最大4GB、最小2GB

`docker-compose.yml`で調整可能です。

## ヘルスチェック

コンテナのヘルスチェックが30秒間隔で実行されます。

```bash
# ヘルスステータスを確認
docker inspect --format='{{.State.Health.Status}}' stock-link-parser
```
