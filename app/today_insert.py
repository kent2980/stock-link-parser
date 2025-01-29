import os
import sys
from datetime import datetime

from app.api.ix.insert import Insert

# ロックファイルのパスを指定
lock_file = "/home/kent2980/docker_cont/stock-link-parser/script.lock"

if __name__ == "__main__":
    # ロックファイルが存在するか確認
    if os.path.exists(lock_file):
        print("前回のプロセスがまだ実行中です。終了します。")
        sys.exit(0)  # 実行をスキップ

    # ロックファイルを作成
    with open(lock_file, "w") as f:
        f.write("")

    try:
        outputPath = "/home/kent2980/docker_cont/stock-link-parser/output"
        today = datetime.now().strftime("%Y%m%d")  # 出力例: 20210601
        targetDir = f"/home/kent2980/doc/tdnet/{today}"
        api_base_url = "https://api.fs-stock.net"
        insert = Insert(outputPath, api_base_url)
        insert.insert_xbrl_dir(targetDir)

    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
