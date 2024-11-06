import os
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
        zip_path = "/home/kent2980/doc/tdnet/20241106"
        insert = Insert(outputPath)
        insert.insert_xbrl_dir(zip_path)

    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
