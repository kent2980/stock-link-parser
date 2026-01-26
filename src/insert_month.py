"""月次バッチ処理スクリプト

指定された年から現在までのXBRLファイルを処理します。
設定は環境変数または.envファイルから読み込まれます。
"""

import datetime
import sys
from pathlib import Path
from typing import Optional

from src.api.ix.exceptions import ApiInsertionException
from src.api.ix.insert import Insert
from src.config import settings
from src.utils.logging_config import get_logger, setup_logging

# ロギングの初期化
setup_logging(
    log_dir=str(settings.resolved_log_dir),
    log_level=settings.log_level,
    log_to_console=settings.log_to_console,
    log_to_file=settings.log_to_file,
)
logger = get_logger(__name__)


def run_monthly_batch(
    doc_dir: str,
    start_year: int,
    api_base_url: Optional[str] = None,
    output_path: Optional[str] = None,
) -> int:
    """月次バッチ処理を実行する

    Args:
        doc_dir: XBRLドキュメントのベースディレクトリ
        start_year: 処理を開始する年
        api_base_url: APIのベースURL（省略時は設定から取得）
        output_path: 出力ディレクトリ（省略時は設定から取得）

    Returns:
        終了コード（0: 成功、1: エラー）
    """
    # 設定から値を取得
    lock_file = settings.resolved_lock_file_path
    _output_path = Path(output_path) if output_path else settings.resolved_output_path
    _api_base_url = api_base_url or settings.api_base_url

    # 必要なディレクトリを作成
    settings.ensure_directories()

    # ロックファイルが存在するか確認
    if lock_file.exists():
        logger.warning("前回のプロセスがまだ実行中です。終了します。")
        return 0

    # ロックファイルを作成
    lock_file.touch()

    # 今日の日付を取得
    today = datetime.date.today()
    logger.info(f"月次バッチ処理を開始します (start_year={start_year}, doc_dir={doc_dir})")

    processed_count = 0
    error_count = 0

    try:
        for year in range(start_year, today.year + 1):
            for month in range(1, 13):  # 12月まで処理
                loop = True
                # 指定された月の日付をループで取得
                for day in range(1, 32):
                    try:
                        date = datetime.date(year, month, day)
                        # 今日の日付よりも後の日付の場合処理を終了
                        if date > today:
                            loop = False
                            break
                    except ValueError:
                        # 無効な日付（例：11月31日）をスキップ
                        continue

                    date_str = date.strftime("%Y%m%d")
                    target_dir = Path(doc_dir) / date.strftime("%Y年") / date.strftime("%m月") / date_str

                    if target_dir.exists():
                        try:
                            insert = Insert(str(_output_path), _api_base_url)
                            insert.insert_xbrl_dir(str(target_dir))
                            processed_count += 1
                            logger.debug(f"処理完了: {target_dir}")
                        except ApiInsertionException as e:
                            error_count += 1
                            logger.warning(f"API挿入エラー ({target_dir}): {e}")
                            continue
                        except Exception as e:
                            error_count += 1
                            logger.error(f"予期しないエラー ({target_dir}): {e}", exc_info=True)
                            continue
                    else:
                        logger.debug(f"ディレクトリが存在しません: {target_dir}")
                        continue

                if not loop:
                    break
            if not loop:
                break

        logger.info(f"月次バッチ処理が完了しました (処理数={processed_count}, エラー数={error_count})")
        return 0 if error_count == 0 else 1

    except Exception as e:
        logger.error(f"月次バッチ処理中に致命的なエラーが発生しました: {e}", exc_info=True)
        return 1

    finally:
        # 処理が終了したらロックファイルを削除
        if lock_file.exists():
            lock_file.unlink()
            logger.debug("ロックファイルを削除しました")


if __name__ == "__main__":
    # コマンドライン引数を処理
    # 使用方法: python insert_month.py [api_base_url] <doc_dir> <start_year>
    if len(sys.argv) >= 3:
        if len(sys.argv) >= 4:
            # 旧形式: api_base_url, doc_dir, start_year
            api_url = sys.argv[1]
            doc_directory = sys.argv[2]
            year = int(sys.argv[3])
        else:
            # 新形式: doc_dir, start_year（api_urlは設定から）
            api_url = None
            doc_directory = sys.argv[1]
            year = int(sys.argv[2])

        exit_code = run_monthly_batch(
            doc_dir=doc_directory,
            start_year=year,
            api_base_url=api_url,
        )
        sys.exit(exit_code)
    else:
        logger.error("引数が不足しています")
        print("使用方法:")
        print("  python insert_month.py <doc_dir> <start_year>")
        print("  python insert_month.py <api_base_url> <doc_dir> <start_year>")
        sys.exit(1)
