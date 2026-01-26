# Webアプリ向けデータ構造の評価

## 現在のデータ構造の評価

### ✅ 良い点

1. **統合データが提供されている**
   - ラベル、計算リンク、定義リンク、表示リンクが統合済み
   - 追加のAPI呼び出しが不要

2. **表示用データが含まれている**
   - `display_numeric`: "40,110"
   - `display_scale`: "千円"
   - そのまま表示可能

3. **メタデータが豊富**
   - ソースファイル情報、レポートタイプ、ロール情報など

### ⚠️ 改善が必要な点

1. **数値が文字列型**
   - `numeric: "40110"` → 計算に不便
   - ソートが文字列ソートになる

2. **コンテキスト情報が不完全**
   - `context: ["Prior1InterimDuration"]` → 期間情報が別途必要
   - `ix_context`から取得する必要がある

3. **ラベルが配列**
   - 主要ラベルを選ぶ必要がある
   - 優先順位が不明確

4. **データがフラットでない**
   - 表示用データが複数フィールドに分散
   - 構造化されていない

## 改善案の実装

### Webアプリ向けフォーマッター

`src/utils/web_app_formatter.py`を実装しました。

**主な機能:**
1. **数値の正規化**: 文字列 → 数値型に変換
2. **主要ラベルの抽出**: 優先順位に基づいて主要ラベルを選択
3. **コンテキスト情報の展開**: 期間・エンティティ情報を構造化
4. **表示データの統合**: 表示用データを1つのオブジェクトに統合

### 使用例

```python
from src.utils.web_app_formatter import format_for_web_app

# 元のデータ
item = {
    "item_key": "...",
    "name": "jppfs_cor_ProfitLoss",
    "numeric": "40110",
    "display_numeric": "40,110",
    "display_scale": "千円",
    "labels": [...],
    ...
}

# Webアプリ向けにフォーマット
formatted = format_for_web_app(item, context_data)

# 結果:
# {
#   "id": "...",
#   "element_name": "jppfs_cor_ProfitLoss",
#   "label": {
#     "primary": "中間純損失（△）",
#     "short": "中間純損失",
#     "lang": "ja"
#   },
#   "value": {
#     "raw": 40110000,        # 数値型で計算可能
#     "formatted": "40,110",
#     "unit": "千円",
#     "display": "40,110千円"
#   },
#   ...
# }
```

## Webアプリでの扱いやすさ

### 改善前（現在の構造）

```javascript
// 数値計算
const value = parseFloat(item.numeric) * Math.pow(10, parseInt(item.scale));
// 表示
const display = `${item.display_numeric}${item.display_scale}`;
// ラベル取得
const label = item.labels.find(l => l.lang === 'ja')?.label || item.labels[0]?.label;
```

### 改善後（フォーマット済み）

```javascript
// 数値計算
const value = item.value.raw;  // 直接使用可能
// 表示
const display = item.value.display;  // そのまま表示
// ラベル取得
const label = item.label.primary;  // 主要ラベルを直接取得
```

## 推奨事項

### 1. APIエンドポイントにフォーマットオプションを追加

```python
@app.get("/xbrl/files/{head_item_key}/data")
async def get_xbrl_data(
    head_item_key: str,
    format: str = Query("standard", regex="^(standard|web_app)$")
):
    if format == "web_app":
        # Webアプリ向けフォーマットを適用
        from src.utils.web_app_formatter import format_list_for_web_app
        formatted_data = format_list_for_web_app(data, context_data)
        return formatted_data
    else:
        return data
```

### 2. フロントエンドでの変換

フロントエンドで変換する場合は、`web_app_formatter.py`のロジックをJavaScriptに移植。

### 3. キャッシュ戦略

フォーマット済みデータをキャッシュすることで、パフォーマンスを向上。

## 結論

**現在の構造**: Webアプリで扱うには改善の余地あり
- 数値が文字列型
- コンテキスト情報が不完全
- ラベル選択が必要

**改善後**: Webアプリで扱いやすい
- 数値型で計算可能
- 構造化されたデータ
- 主要ラベルが明確
- 表示用データが統合

**推奨**: `web_app_formatter.py`を使用して、APIレスポンス時にフォーマットを適用することを推奨します。
