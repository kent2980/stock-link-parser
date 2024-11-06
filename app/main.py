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
        output_oath = "/Users/user/Vscode/XBRL_Parse_Project/stock-link-parser/output"
        zip_path = "/Users/user/Documents/tdnet/xbrl/20241031"
        insert = Insert(output_oath)
        insert.insert_xbrl_dir(zip_path)

    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
