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
        message="APIへのデータ挿入中にエラーが発生しました。",
    ):
        self.message = f"{message}"
        super().__init__(self.message)
