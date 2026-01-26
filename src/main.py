"""XBRL処理メインスクリプト

XBRLファイルを解析し、APIにデータを挿入します。
設定は環境変数または.envファイルから読み込まれます。
"""

import sys
from pathlib import Path

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


def main(xbrl_data_path: str = None) -> int:
    """メイン処理

    Args:
        xbrl_data_path: XBRLファイルのディレクトリパス（省略時は設定から取得）

    Returns:
        終了コード（0: 成功、1: エラー）
    """
    # 設定から値を取得
    lock_file = settings.resolved_lock_file_path
    output_path = settings.resolved_output_path
    api_base_url = settings.api_base_url
    data_path = xbrl_data_path or settings.xbrl_data_path

    if not data_path:
        logger.error("XBRLデータパスが指定されていません。XBRL_XBRL_DATA_PATH環境変数を設定してください。")
        return 1

    # 必要なディレクトリを作成
    settings.ensure_directories()

    # ロックファイルが存在するか確認
    if lock_file.exists():
        logger.warning("前回のプロセスがまだ実行中です。終了します。")
        return 0

    # ロックファイルを作成
    lock_file.touch()

    logger.info(f"XBRL処理を開始します (data_path={data_path})")

    try:
        insert = Insert(str(output_path), api_base_url)
        insert.insert_xbrl_dir(data_path)
        logger.info("XBRL処理が完了しました")
        return 0

    except Exception as e:
        logger.error(f"XBRL処理中にエラーが発生しました: {e}", exc_info=True)
        return 1

    finally:
        # 処理が終了したらロックファイルを削除
        if lock_file.exists():
            lock_file.unlink()
            logger.debug("ロックファイルを削除しました")


if __name__ == "__main__":
    # コマンドライン引数からXBRLデータパスを取得
    xbrl_path = sys.argv[1] if len(sys.argv) > 1 else None
    exit_code = main(xbrl_path)
    sys.exit(exit_code)
