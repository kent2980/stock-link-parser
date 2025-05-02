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
            "python latest_insert.py <outputPath> <today> <targetDir> <api_base_url> <days>"
        )
        sys.exit(1)  # 実行をスキップ

    target = sys.argv[1]
    api_base_url = sys.argv[2]

    print(f"引数を取得しました:")
    print(f"outputPath: {outputPath}")
    print(f"target: {target}")
    print(f"api_base_url: {api_base_url}")

    try:
        # 日付を遡るループ
        today = datetime.now()

        while True:
            try:
                print(f"処理中の日付: {today.strftime('%Y-%m-%d')}")
                insert = Insert(outputPath, api_base_url)
                targetDir = Path.joinpath(
                    Path(target), Path(today.strftime("%Y%m%d"))
                )

                # targetDirが存在するか確認
                if not targetDir.exists():
                    print(f"対象ディレクトリが存在しません: {targetDir}")
                    print("処理を中断します。")
                    break

                insert.insert_xbrl_dir(targetDir.as_posix())
                today -= timedelta(days=1)
            except ApiInsertionException as e:
                print(f"エラーが発生しました: {e}")
                print("処理を中断します。")
                break

    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
