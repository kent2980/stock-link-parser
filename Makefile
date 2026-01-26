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
