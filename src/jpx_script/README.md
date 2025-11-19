# 東京証券取引所の公式サイトから情報を取得します

## 1. StockInfoクラス

### 33業種及び関連情報の取得を行うクラスです

東京証券取引所の公式サイトより東証上場銘柄一覧(エクセル)をダウンロードして、各種フォーマットで取得します。この情報は毎月第3営業日の午前9時以降に前月末データが更新されます。

#### 使い方

```
# ローカルのパスを設定
save_path = "/Users/user/Vscode/XBRL_Parse_Project/stock-link-parser/output/excel/data_j.xls"
# クラスのインスタンス化
stock_info = StockInfo(save_path)
# DataFrame形式でデータを取得
df =stock_info.get_info_to_df()
# JSON形式でデータを取得
json_data = stock_info.get_info_to_json()
```

ローカルにエクセルファイルを保存して、指定した形式でデータを取得できます。
