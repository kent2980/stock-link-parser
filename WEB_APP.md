# Webアプリケーション（React.js + TypeScript）

XBRL財務諸表ビューアのWebアプリケーションです。React.js（TypeScript）で構築されています。

## 機能

- **銘柄一覧**: XBRLファイルの一覧を表示し、ページネーション対応
- **銘柄詳細**: 各銘柄の財務諸表、定性情報等を閲覧
  - **基本情報タブ**: 会社名、証券コード、報告日などの基本情報
  - **財務諸表タブ**: 財務データの一覧表示
  - **定性情報タブ**: 定性情報の階層構造表示（{title: content}形式）

## 起動方法

### Docker Composeを使用（推奨）

```bash
# Webアプリケーションのみ起動
make up-web

# または、すべてのサービスを起動
docker-compose up -d

# ログを確認
make logs-web
```

Webアプリケーションは `http://localhost:3000` でアクセスできます。

### ローカル環境で起動

```bash
cd frontend
npm install
npm start
```

## ビルド

```bash
# Dockerイメージをビルド
make build-web

# または
docker-compose build web
```

## 開発

### コンテナ内でシェルを起動

```bash
make shell-web
```

### ファイル構造

```
frontend/
├── public/              # 静的ファイル
│   └── index.html
├── src/
│   ├── components/     # 再利用可能なコンポーネント
│   │   ├── Header.tsx
│   │   └── Header.css
│   ├── pages/          # ページコンポーネント
│   │   ├── StockList.tsx      # 銘柄一覧ページ
│   │   ├── StockList.css
│   │   ├── StockDetail.tsx    # 銘柄詳細ページ
│   │   └── StockDetail.css
│   ├── services/       # APIクライアント
│   │   └── api.ts
│   ├── types/         # TypeScript型定義
│   │   └── index.ts
│   ├── App.tsx         # メインアプリケーション
│   ├── App.css
│   ├── index.tsx        # エントリーポイント
│   └── index.css
├── package.json
├── tsconfig.json
└── README.md
```

## API連携

Webアプリケーションは以下のAPIエンドポイントを使用します：

- `GET /api/v1/xbrl/files` - XBRLファイル一覧
- `GET /api/v1/xbrl/files/{head_item_key}` - ファイル情報
- `GET /api/v1/xbrl/files/{head_item_key}/data/{category}` - カテゴリ別データ
  - `qualitative_info` - 定性情報（階層構造）
  - `ix_non_fraction_enriched` - 財務データ

## 環境変数

- `REACT_APP_API_URL`: APIのベースURL（デフォルト: `http://localhost:8000`）

## トラブルシューティング

### コンテナが起動しない場合

```bash
# ログを確認
make logs-web

# コンテナを再ビルド
make build-web
docker-compose up -d web
```

### APIに接続できない場合

1. APIコンテナが起動しているか確認
   ```bash
   docker-compose ps api
   ```

2. CORS設定を確認（FastAPI側で既に設定済み）

3. 環境変数 `REACT_APP_API_URL` を確認

### ホットリロードが動作しない場合

Docker環境では、`CHOKIDAR_USEPOLLING=true` と `WATCHPACK_POLLING=true` が設定されています。
これにより、ファイル変更が検出されるようになります。
