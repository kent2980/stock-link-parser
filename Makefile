.PHONY: help build up down logs shell test clean

help: ## このヘルプメッセージを表示
	@echo "利用可能なコマンド:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Dockerイメージをビルド
	docker-compose build

build-dev: ## 開発環境用のDockerイメージをビルド
	docker-compose -f docker-compose.dev.yml build

up: ## コンテナを起動
	docker-compose up -d

up-dev: ## 開発環境のコンテナを起動
	docker-compose -f docker-compose.dev.yml up -d

down: ## コンテナを停止
	docker-compose down

down-dev: ## 開発環境のコンテナを停止
	docker-compose -f docker-compose.dev.yml down

logs: ## ログを表示
	docker-compose logs -f

logs-dev: ## 開発環境のログを表示
	docker-compose -f docker-compose.dev.yml logs -f

shell: ## コンテナ内でシェルを起動
	docker-compose exec stock-link-parser bash

shell-dev: ## 開発環境のコンテナ内でシェルを起動
	docker-compose -f docker-compose.dev.yml exec stock-link-parser-dev bash

run: ## メインスクリプトを実行
	docker-compose run --rm stock-link-parser python src/main.py $(ARGS)

test: ## テストを実行
	docker-compose run --rm stock-link-parser pytest src/tests/

test-dev: ## 開発環境でテストを実行
	docker-compose -f docker-compose.dev.yml run --rm stock-link-parser-dev pytest src/tests/

clean: ## コンテナとイメージを削除
	docker-compose down -v
	docker rmi stock-link-parser:latest || true

clean-dev: ## 開発環境のコンテナとイメージを削除
	docker-compose -f docker-compose.dev.yml down -v
	docker rmi stock-link-parser:dev || true

rebuild: clean build ## イメージを再ビルド

rebuild-dev: clean-dev build-dev ## 開発環境のイメージを再ビルド

build-api: ## APIコンテナのイメージをビルド
	docker-compose build api

up-api: ## APIコンテナを起動
	docker-compose up -d api

down-api: ## APIコンテナを停止
	docker-compose stop api

logs-api: ## APIコンテナのログを表示
	docker-compose logs -f api

shell-api: ## APIコンテナ内でシェルを起動
	docker-compose exec api bash

restart-api: down-api up-api ## APIコンテナを再起動

import-test-data: ## テストデータをインポート
	.venv/bin/python src/tests/import_test_data.py --target data_dir

import-test-data-fastapi: ## テストデータをFastAPIキャッシュにインポート
	.venv/bin/python src/tests/import_test_data.py --target fastapi_cache

import-test-data-both: ## テストデータを両方にインポート
	.venv/bin/python src/tests/import_test_data.py --target both

import-data: ## 指定ディレクトリからzipファイルをインポート（XBRL_XBRL_DATA_PATHから）
	.venv/bin/python src/scripts/import_data_from_directory.py

import-data-from: ## 指定ディレクトリからzipファイルをインポート（SOURCE_DIRを指定）
	@if [ -z "$(SOURCE_DIR)" ]; then \
		echo "Error: SOURCE_DIR must be specified. Usage: make import-data-from SOURCE_DIR=/path/to/directory"; \
		exit 1; \
	fi
	.venv/bin/python src/scripts/import_data_from_directory.py --source-dir $(SOURCE_DIR)

clean-docker: ## Dockerコンテナとネットワークをクリーンアップ
	docker-compose down -v
	docker network prune -f

rebuild-api-clean: clean-docker build-api up-api ## APIを完全にクリーンアップして再ビルド
