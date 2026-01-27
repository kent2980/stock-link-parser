#!/bin/bash
# コンテナ内でデータベーススキーマを作成するスクリプト

set -e

# コンテナ名
CONTAINER_NAME="stock-link-parser"

# データディレクトリからサンプルzipファイルを検索
DATA_DIR="/app/data"
SAMPLE_ZIP=$(find "$DATA_DIR" -name "*.zip" | head -1)

if [ -z "$SAMPLE_ZIP" ]; then
    echo "エラー: サンプルzipファイルが見つかりません: $DATA_DIR"
    exit 1
fi

echo "サンプルzipファイル: $SAMPLE_ZIP"

# Pythonスクリプトを実行
python /app/src/scripts/create_database_schema.py \
    --sample-zip "$SAMPLE_ZIP" \
    --output-path /app/output
