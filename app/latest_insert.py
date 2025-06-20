import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from app.api.ix.exceptions import ApiInsertionException
from app.api.ix.insert import Insert

# ロックファイルのパスを指定
currentPath = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(currentPath)
lock_file = f"{parentDir}/script.lock"
outputPath = f"{parentDir}/output"

if __name__ == "__main__":
    # ロックファイルが存在するか確認
    if os.path.exists(lock_file):
        print("前回のプロセスがまだ実行中です。終了します。")
        sys.exit(0)  # 実行をスキップ

    # ロックファイルを作成
    with open(lock_file, "w") as f:
        f.write("")

    # コマンドライン引数を取得
    if len(sys.argv) < 3:
        print("引数が不足しています。以下の形式で指定してください:")
        print(
            "python latest_insert.py <targetDir> <api_base_url> [select_date]"
        )
        sys.exit(1)  # 実行をスキップ

    target = sys.argv[1]
    api_base_url = sys.argv[2]
    if len(sys.argv) >= 4:
        select_date = sys.argv[3]
    else:
        select_date = datetime.now().strftime("%Y-%m-%d")

    print(f"引数を取得しました:")
    print(f"outputPath: {outputPath}")
    print(f"target: {target}")
    print(f"api_base_url: {api_base_url}")
    print(f"select_date: {select_date}")

    try:
        # 日付を遡るループ
        today = datetime.strptime(select_date, "%Y-%m-%d")
        yesterday = today - timedelta(days=1)

        while True:
            try:
                print(f"処理中の日付: {today.strftime('%Y-%m-%d')}")
                insert = Insert(outputPath, api_base_url)
                targetDir = Path.joinpath(
                    Path(target),
                    Path(today.strftime("%Y年")),
                    Path(today.strftime("%m月")),
                    Path(today.strftime("%Y%m%d")),
                )

                # 昨日までのデータを取得
                if today < yesterday:
                    print(
                        "指定された日付よりも前の日付です。処理を終了します。"
                    )
                    break

                insert.insert_xbrl_dir(targetDir.as_posix())
                today -= timedelta(days=1)
            except ApiInsertionException as e:
                today -= timedelta(days=1)
                continue

    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
