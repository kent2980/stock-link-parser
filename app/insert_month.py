import datetime
import os
import re
import sys

from app.api.insert import Insert

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
        month = 202411
        # 10月のDate型をループで取得
        for i in range(1, 32).__reversed__():
            date = datetime.date(month, i)
            date_str = date.strftime("%Y%m%d")
            targetDir = f"/home/kent2980/doc/tdnet/{date_str}"
            api_base_url = "https://api.fs-stock.net"
            insert = Insert(outputPath, api_base_url)
            insert.insert_xbrl_dir(targetDir)
    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
