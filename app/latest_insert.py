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

    # コマンドライン引数を取得
    if len(sys.argv) < 3:
        print("引数が不足しています。以下の形式で指定してください:")
        print("python latest_insert.py <targetDir> <api_base_url> [select_date]")
        sys.exit(1)  # 実行をスキップ
        # finaryの処理を実行

    target = sys.argv[1]
    api_base_url = sys.argv[2]
    if len(sys.argv) >= 4:
        select_date = sys.argv[3]
        target_date = datetime.strptime(select_date, "%Y-%m-%d")
    else:
        # 引数が指定されていない場合は今日のみ処理
        target_date = datetime.now()
        select_date = target_date.strftime("%Y-%m-%d")

    print("引数を取得しました:")
    print(f"outputPath: {outputPath}")
    print(f"target: {target}")
    print(f"api_base_url: {api_base_url}")
    print(f"select_date: {select_date}")

    # ロックファイルを作成
    with open(lock_file, "w") as f:
        f.write("")

    try:
        # 今日から指定された日付まで遡って処理
        today = datetime.now()

        # 引数で日付が指定されていない場合は今日のみ処理
        if len(sys.argv) < 4:
            print(f"今日のデータのみ処理します: {today.strftime('%Y-%m-%d')}")
            insert = Insert(outputPath, api_base_url)
            targetDir = Path.joinpath(
                Path(target),
                Path(today.strftime("%Y年")),
                Path(today.strftime("%m月")),
                Path(today.strftime("%Y%m%d")),
            )

            try:
                if targetDir.exists():
                    insert.insert_xbrl_dir(targetDir.as_posix())
                    print(f"処理完了: {today.strftime('%Y-%m-%d')}")
                else:
                    print(f"ディレクトリが存在しません: {targetDir}")
            except ApiInsertionException as e:
                print(f"API挿入エラー: {e}")
            except Exception as e:
                import traceback

                print(f"処理エラー: {e}")
                print(f"エラーの詳細:")
                print(traceback.format_exc())
        else:
            # 指定された日付まで遡って処理
            print(
                f"今日から指定日付まで処理します: {today.strftime('%Y-%m-%d')} → {target_date.strftime('%Y-%m-%d')}"
            )

            current_date = today
            while current_date >= target_date:
                try:
                    print(f"処理中の日付: {current_date.strftime('%Y-%m-%d')}")
                    insert = Insert(outputPath, api_base_url)
                    targetDir = Path.joinpath(
                        Path(target),
                        Path(current_date.strftime("%Y年")),
                        Path(current_date.strftime("%m月")),
                        Path(current_date.strftime("%Y%m%d")),
                    )

                    if targetDir.exists():
                        insert.insert_xbrl_dir(targetDir.as_posix())
                        print(f"処理完了: {current_date.strftime('%Y-%m-%d')}")
                    else:
                        print(f"ディレクトリが存在しません（スキップ）: {targetDir}")

                except ApiInsertionException as e:
                    print(
                        f"API挿入エラー（スキップ）: {current_date.strftime('%Y-%m-%d')} - {e}"
                    )
                except Exception as e:
                    import traceback

                    print(
                        f"処理エラー（スキップ）: {current_date.strftime('%Y-%m-%d')} - {e}"
                    )
                    print(f"エラーの詳細:")
                    print(traceback.format_exc())

                current_date -= timedelta(days=1)

    finally:
        # 処理が終了したらロックファイルを削除
        if os.path.exists(lock_file):
            os.remove(lock_file)
