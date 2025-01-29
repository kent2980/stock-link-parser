import datetime
import os
import sys

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
        output_path = "/home/kent2980/docker_cont/stock-link-parser/output"
        year = 2024
        month = 10
        loop = True
        for _month in range(month, 0, -1):
            # 指定された月の日付をループで取得
            for day in range(31, 0, -1):
                try:
                    date = datetime.date(year, _month, day)
                except ValueError:
                    # 無効な日付（例：11月31日）をスキップ
                    continue

                date_str = date.strftime("%Y%m%d")
                target_dir = f"/home/kent2980/doc/tdnet/{date_str}"
                api_base_url = "https://api.fs-stock.net"
                insert = Insert(output_path, api_base_url)
                insert.insert_xbrl_dir(target_dir)
            if not loop:
                break
    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
