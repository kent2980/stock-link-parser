#!/bin/bash
set -e

# 環境変数の確認
echo "=== 環境変数の確認 ==="
echo "XBRL_ENVIRONMENT: ${XBRL_ENVIRONMENT:-development}"
echo "XBRL_LOG_LEVEL: ${XBRL_LOG_LEVEL:-INFO}"
echo "XBRL_API_BASE_URL: ${XBRL_API_BASE_URL:-not set}"
echo "======================"

# 必要なディレクトリを作成
mkdir -p /app/output /app/logs /app/data

# ロックファイルのパスを確認
if [ -n "$XBRL_LOCK_FILE_PATH" ]; then
    LOCK_DIR=$(dirname "$XBRL_LOCK_FILE_PATH")
    mkdir -p "$LOCK_DIR"
fi

# コマンドを実行
exec "$@"
