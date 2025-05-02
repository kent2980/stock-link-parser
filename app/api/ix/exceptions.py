class NotXbrlDirectoryException(Exception):
    """XBRLディレクトリではない場合に発生する例外"""

    def __init__(
        self, message="指定されたディレクトリはXBRL形式ではありません。"
    ):
        self.message = message
        super().__init__(self.message)


class ApiInsertionException(Exception):
    """APIへのデータ挿入中にエラーが発生した場合に発生する例外"""

    def __init__(
        self,
        endpoint,
        status_code,
        message="APIへのデータ挿入中にエラーが発生しました。",
    ):
        self.endpoint = endpoint
        self.status_code = status_code
        self.message = f"{message} エンドポイント: {endpoint}, ステータスコード: {status_code}"
        super().__init__(self.message)
