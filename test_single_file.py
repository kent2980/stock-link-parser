#!/usr/bin/env python3

import os
import sys

# プロジェクトのルートディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.api.ix.insert import Insert

if __name__ == "__main__":
    output_path = "/Users/user/Vscode/app/stock-link-parser/output"
    api_base_url = "http://localhost:8000"

    # 単一ファイルでテスト
    test_file = (
        "/Volumes/SharedFolder/tdnet/2025年/07月/20250709/081220250704508543.zip"
    )

    if os.path.exists(test_file):
        print(f"テストファイル: {test_file}")
        insert = Insert(output_path, api_base_url)
        insert.insert_xbrl_zip(test_file)
    else:
        print("テストファイルが見つかりません")
