# XBRL財務諸表ビューア - フロントエンド

React.js（TypeScript）で構築されたXBRL財務諸表ビューアのフロントエンドアプリケーションです。

## 機能

- **銘柄一覧**: XBRLファイルの一覧を表示
- **銘柄詳細**: 各銘柄の財務諸表、定性情報等を閲覧
  - 基本情報タブ: 会社名、証券コード、報告日などの基本情報
  - 財務諸表タブ: 財務データの一覧表示
  - 定性情報タブ: 定性情報の階層構造表示

## 技術スタック

- React 18.2
- TypeScript 5.3
- React Router 6.21
- Axios 1.6
- CSS3

## 開発環境のセットアップ

### ローカル環境

```bash
cd frontend
npm install
npm start
```

アプリケーションは `http://localhost:3000` で起動します。

### Docker環境

```bash
# docker-composeで起動
docker-compose up web

# または、個別にビルド・起動
docker build -f Dockerfile.web -t stock-link-parser-web .
docker run -p 3000:3000 stock-link-parser-web
```

## 環境変数

- `REACT_APP_API_URL`: APIのベースURL（デフォルト: `http://localhost:8000`）

## プロジェクト構造

```
frontend/
├── public/           # 静的ファイル
├── src/
│   ├── components/   # 再利用可能なコンポーネント
│   ├── pages/        # ページコンポーネント
│   ├── services/     # APIクライアント
│   ├── types/        # TypeScript型定義
│   ├── App.tsx       # メインアプリケーション
│   └── index.tsx     # エントリーポイント
├── package.json
└── tsconfig.json
```

## APIエンドポイント

このアプリケーションは以下のAPIエンドポイントを使用します：

- `GET /api/v1/xbrl/files` - XBRLファイル一覧
- `GET /api/v1/xbrl/files/{head_item_key}` - ファイル情報
- `GET /api/v1/xbrl/files/{head_item_key}/data` - 全データ
- `GET /api/v1/xbrl/files/{head_item_key}/data/{category}` - カテゴリ別データ

## ビルド

```bash
npm run build
```

ビルドされたファイルは `build/` ディレクトリに出力されます。
