# Python 3.12の公式イメージを使用
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uvをインストール（高速なPythonパッケージマネージャー）
RUN pip install --no-cache-dir uv

# プロジェクトファイルをコピー
COPY pyproject.toml ./
COPY uv.lock* ./

# 依存関係をインストール（uvを使用）
# uv.lockがある場合はそれを使用、ない場合はpyproject.tomlからインストール
RUN if [ -f uv.lock ]; then \
        uv pip install --system --locked -e .; \
    else \
        uv pip install --system -e .; \
    fi

# アプリケーションコードをコピー
COPY src/ ./src/
COPY docker/ ./docker/
COPY .env.example ./.env.example

# 必要なディレクトリを作成
RUN mkdir -p /app/output /app/logs /app/data

# エントリーポイントを設定
RUN chmod +x /app/docker/entrypoint.sh

# 環境変数を設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# エントリーポイントを設定
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# デフォルトのコマンド
CMD ["python", "src/main.py"]
