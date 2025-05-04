import datetime
import os
import sys

from app.api.ix.exceptions import ApiInsertionException
from app.api.ix.insert import Insert



if __name__ == "__main__":
    # ロックファイルのパスを指定
    currentPath = os.path.dirname(os.path.abspath(__file__))
    parentDir = os.path.dirname(currentPath)
    lock_file = f"{parentDir}/script.lock"
    output_path = f"{parentDir}/output"

    if len(sys.argv) > 2:
        api_base_url = sys.argv[1]
    # ロックファイルが存在するか確認
    if os.path.exists(lock_file):
        print("前回のプロセスがまだ実行中です。終了します。")
        sys.exit(0)  # 実行をスキップ

    # ロックファイルを作成
    with open(lock_file, "w") as f:
        f.write("")

    try:
        for i in range(2025, 2026):
            for j in range(1, 12):
                year = i
                month = j
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
                        target_dir = f"/home/kent2980/doc/tdnet/{date.strftime("%Y年")}/{date.strftime("%m月")}/{date_str}"
                        if os.path.exists(target_dir):
                            try:
                                insert = Insert(output_path, api_base_url)
                                insert.insert_xbrl_dir(target_dir)
                            except ApiInsertionException:
                                continue
                    if not loop:
                        break
    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
