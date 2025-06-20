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

    if len(sys.argv) > 3:
        api_base_url = sys.argv[1]
        doc_dir = sys.argv[2]
        startYear = int(sys.argv[3])
    # ロックファイルが存在するか確認
    if os.path.exists(lock_file):
        print("前回のプロセスがまだ実行中です。終了します。")
        sys.exit(0)  # 実行をスキップ

    # ロックファイルを作成
    with open(lock_file, "w") as f:
        f.write("")

    # 今日の日付を取得
    today = datetime.date.today()

    try:
        for year in range(startYear, today.year + 1):
            for month in range(1, 12):
                loop = True
                # 指定された月の日付をループで取得
                for day in range(1, 31):
                    try:
                        date = datetime.date(year, month, day)
                        # 今日の日付よりも後の日付の場合処理を終了
                        if datetime.date(year, month, day) > today:
                            loop = False
                            break
                    except ValueError:
                        # 無効な日付（例：11月31日）をスキップ
                        continue

                    date_str = date.strftime("%Y%m%d")
                    target_dir = f"{doc_dir}/{date.strftime("%Y年")}/{date.strftime("%m月")}/{date_str}"
                    if os.path.exists(target_dir):
                        try:
                            insert = Insert(output_path, api_base_url)
                            insert.insert_xbrl_dir(target_dir)
                        except ApiInsertionException:
                            continue
                    else:
                        print(
                            f"指定されたディレクトリが存在しません: {target_dir}"
                        )
                        continue
                if not loop:
                    break
    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
