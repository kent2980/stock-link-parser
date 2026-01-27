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

up-db: ## PostgreSQLコンテナのみを起動
	docker-compose up -d postgres

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

import-to-db: ## データベースにXBRLデータをインポート（コンテナ内で実行）
	@echo "データベースにXBRLデータをインポートします（コンテナ内で実行）..."
	@docker-compose run --rm stock-link-parser python src/scripts/import_to_database.py || \
	(.venv/bin/python src/scripts/import_to_database.py && echo "ローカル環境で実行しました")

import-to-db-limited: ## データベースにXBRLデータを制限付きでインポート（LIMITを指定、例: make import-to-db-limited LIMIT=20）
	@if [ -z "$(LIMIT)" ]; then \
		echo "Error: LIMIT must be specified. Usage: make import-to-db-limited LIMIT=20"; \
		exit 1; \
	fi
	@echo "データベースにXBRLデータを$(LIMIT)件インポートします（コンテナ内で実行）..."
	@docker-compose run --rm stock-link-parser python src/scripts/import_to_database.py --limit $(LIMIT) || \
	(.venv/bin/python src/scripts/import_to_database.py --limit $(LIMIT) && echo "ローカル環境で実行しました")

clear-and-import: ## データを削除して再インポート（LIMITを指定、例: make clear-and-import LIMIT=20）
	@if [ -z "$(LIMIT)" ]; then \
		echo "Error: LIMIT must be specified. Usage: make clear-and-import LIMIT=20"; \
		exit 1; \
	fi
	@echo "データベースのデータを削除して、$(LIMIT)件再インポートします..."
	@echo "ステップ1: データベーススキーマを再作成（コンテナ内で実行）..."
	@docker-compose run --rm stock-link-parser python src/scripts/create_database_schema.py --data-dir /app/data || \
	(.venv/bin/python src/scripts/create_database_schema.py --data-dir $$(.venv/bin/python -c "from src.config import settings; print(settings.project_root / 'data')") && echo "ローカル環境で実行しました")
	@echo "ステップ2: $(LIMIT)件のデータをインポート（コンテナ内で実行）..."
	@docker-compose run --rm stock-link-parser python src/scripts/import_to_database.py --limit $(LIMIT) || \
	(.venv/bin/python src/scripts/import_to_database.py --limit $(LIMIT) && echo "ローカル環境で実行しました")

import-to-db-single: ## 単一のzipファイルをデータベースにインポート（ZIP_FILEを指定）
	@if [ -z "$(ZIP_FILE)" ]; then \
		echo "Error: ZIP_FILE must be specified. Usage: make import-to-db-single ZIP_FILE=/path/to/file.zip"; \
		exit 1; \
	fi
	.venv/bin/python src/scripts/import_to_database.py --zip-file $(ZIP_FILE)

recreate-db-schema: ## データベーススキーマを再作成（コンテナ内で実行）
	@echo "データベーススキーマを再作成します（コンテナ内で実行）..."
	@docker-compose run --rm stock-link-parser python src/scripts/create_database_schema.py --data-dir /app/data || \
	(.venv/bin/python src/scripts/create_database_schema.py --data-dir $$(.venv/bin/python -c "from src.config import settings; print(settings.project_root / 'data')") && echo "ローカル環境で実行しました")

recreate-db-schema-sample: ## サンプルzipファイルを指定してデータベーススキーマを再作成（SAMPLE_ZIPを指定）
	@if [ -z "$(SAMPLE_ZIP)" ]; then \
		echo "Error: SAMPLE_ZIP must be specified. Usage: make recreate-db-schema-sample SAMPLE_ZIP=/path/to/file.zip"; \
		exit 1; \
	fi
	.venv/bin/python src/scripts/create_database_schema.py --sample-zip $(SAMPLE_ZIP)

logs-db: ## PostgreSQLコンテナのログを表示
	docker-compose logs -f postgres

shell-db: ## PostgreSQLコンテナ内でシェルを起動
	docker-compose exec postgres bash

psql: ## PostgreSQLに接続（psqlコマンド）
	docker-compose exec postgres psql -U ${XBRL_DB_USERNAME:-postgres} -d ${XBRL_DB_DATABASE:-xbrl}

up-web: ## Webアプリケーションコンテナを起動
	docker-compose up -d web

build-web: ## Webアプリケーションコンテナをビルド
	docker-compose build web

logs-web: ## Webアプリケーションコンテナのログを表示
	docker-compose logs -f web

shell-web: ## Webアプリケーションコンテナ内でシェルを起動
	docker-compose exec web sh
