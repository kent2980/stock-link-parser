# Webアプリ向けデータ構造の評価と改善案

## 現在のデータ構造の問題点

### 1. 数値が文字列型
```json
{
  "numeric": "40110",  // 文字列 → 計算に使いにくい
  "display_numeric": "40,110",
  "display_scale": "千円"
}
```
**問題**: 数値計算やソートに不便

### 2. コンテキストが配列形式
```json
{
  "context": ["Prior1InterimDuration"]  // 配列 → 扱いにくい
}
```
**問題**: コンテキスト情報が別途`ix_context`から取得する必要がある

### 3. ラベルが配列で優先順位が不明確
```json
{
  "labels": [
    {
      "label": "中間純損失（△）",
      "role": "http://.../negativeLabel",
      "lang": "ja"
    }
  ]
}
```
**問題**: 主要なラベルを選ぶ必要がある

### 4. 技術的な要素名
```json
{
  "name": "jppfs_cor_ProfitLoss"  // 技術的な名前
}
```
**問題**: 人間が読みにくい

### 5. 表示用データが分散
```json
{
  "numeric": "40110",
  "display_numeric": "40,110",
  "display_scale": "千円",
  "unit_ref": "JPY"
}
```
**問題**: 表示用の値が複数のフィールドに分散

## 改善案：Webアプリ向けの最適化されたデータ構造

### 提案1: 数値の正規化

```json
{
  "value": {
    "raw": 40110000,           // 元の数値（整数、単位なし）
    "formatted": "40,110",     // フォーマット済み文字列
    "scale": "千円",           // 単位
    "unit": "JPY",             // 通貨単位
    "decimals": -3             // 小数点位置
  }
}
```

### 提案2: コンテキスト情報の展開

```json
{
  "context": {
    "id": "Prior1InterimDuration",
    "period": {
      "type": "prior",
      "start_date": "2024-04-01",
      "end_date": "2024-09-30",
      "duration": "interim"
    },
    "entity": {
      "identifier": "1234",
      "scheme": "TSE"
    }
  }
}
```

### 提案3: 主要ラベルの抽出

```json
{
  "label": {
    "primary": "中間純損失（△）",      // 主要ラベル（日本語、verboseLabel優先）
    "short": "中間純損失",            // 短縮ラベル
    "english": "Interim Net Loss",    // 英語ラベル（あれば）
    "all": [                          // 全ラベル（必要に応じて）
      {
        "text": "中間純損失（△）",
        "role": "negativeLabel",
        "lang": "ja"
      }
    ]
  }
}
```

### 提案4: 表示用データの統合

```json
{
  "display": {
    "value": "40,110",
    "unit": "千円",
    "formatted": "40,110千円",
    "sign": null,
    "is_negative": false
  }
}
```

### 提案5: 階層構造の追加（計算リンクから）

```json
{
  "hierarchy": {
    "parent": null,                    // 親要素
    "children": [                      // 子要素
      {
        "name": "IncomeTaxes_2",
        "weight": -1.0,
        "order": 2.0
      }
    ],
    "level": 0                         // 階層レベル
  }
}
```

## 推奨される最適化されたデータ構造

```json
{
  "id": "5457b3f2-20e3-548e-ae87-e54219c3f138",
  "element_name": "jppfs_cor_ProfitLoss",
  "label": {
    "primary": "中間純損失（△）",
    "short": "中間純損失",
    "lang": "ja"
  },
  "value": {
    "raw": 40110000,
    "formatted": "40,110",
    "unit": "千円",
    "currency": "JPY"
  },
  "context": {
    "period": {
      "type": "prior_interim",
      "start": "2024-04-01",
      "end": "2024-09-30"
    },
    "entity": {
      "code": "1234",
      "scheme": "TSE"
    }
  },
  "report": {
    "type": "edjp",
    "role": "Type1SemiAnnualConsolidatedStatementOfComprehensiveIncome",
    "category": "fr"
  },
  "relationships": {
    "calculation": [
      {
        "to": "IncomeTaxes_2",
        "weight": -1.0,
        "order": 2.0
      }
    ],
    "definition": [],
    "presentation": []
  },
  "metadata": {
    "source_file_id": "139d7233-b2ef-b3b3-d555-366d78e22c92",
    "head_item_key": "3454ba2c-fdea-12f3-a27a-083f6447e3b2",
    "format": "numdotdecimal",
    "decimals": -3,
    "scale": 3
  }
}
```

## Webアプリでの利点

1. **数値計算が容易**: `value.raw`を直接使用可能
2. **表示が簡単**: `value.formatted`と`value.unit`で即座に表示可能
3. **検索・フィルタが容易**: フラットな構造でクエリが簡単
4. **ソートが容易**: 数値型でソート可能
5. **階層構造の可視化**: `relationships`で親子関係を把握
6. **多言語対応**: `label`に言語情報を含む

## 実装方法

データ変換レイヤーを追加して、既存のデータ構造から最適化された構造に変換する。
