import shutil
import zipfile
from pathlib import Path
from uuid import uuid4

import pandas as pd

from app.constants.report_categories import ReportCategories
from app.exception import NotXbrlDirectoryException, NotXbrlTypeException
from app.utils.utils import Utils


class BaseXbrlModel:
    """XBRLファイルを扱うための基底クラス"""

    def __init__(self, xbrl_zip_path, output_path) -> None:
        # XBRLファイルのzipファイルのパスを指定
        self.__xbrl_zip_path = Path(xbrl_zip_path)
        self.__output_path = Path(output_path)
        # XBRLファイルを解凍したディレクトリのパスを取得
        self.__directory_path = self.__unzip_xbrl()
        self.__xbrl_category = self.__xbrl_category()
        self.__xbrl_id = str(
            Utils.string_to_uuid(Path(self.xbrl_zip_path).name)
        )

    @classmethod
    def xbrl_models(cls, xbrl_zip_dirs, output_path):
        """<p>XBRLファイルのzipファイルが格納されているディレクトリを指定してXBRLModelのインスタンスを生成するジェネレーター</p>
            <p>多数のXBRLファイルを一括で処理する際に使用してください。</p>
        <h3>Attributes:</h3>
            <p>xbrl_zip_dirs (str): XBRLファイルのzipファイルが格納されているディレクトリのパス</p>
            <p>output_path (str): スキーマでURLリンクされている、関係XMLファイルの出力先パス</p>
        """
        zip_files = Path(xbrl_zip_dirs).rglob("*.zip")
        # print(f"zip_files: {len(list(zip_files))}")
        for zip_file in zip_files:
            try:
                yield cls(zip_file.as_posix(), output_path)
            except NotXbrlDirectoryException as e:
                print(f"NotXbrlDirectoryException:{zip_file}, {e}")
                yield None

    @property
    def xbrl_id(self):
        return self.__xbrl_id

    def set_xbrl_id(self, xbrl_id):
        self.__xbrl_id = xbrl_id
        return self

    def _set_manager(self):
        raise NotImplementedError

    def __del__(self):
        directory_path = Path(self.directory_path)
        if directory_path.exists() and directory_path.is_dir():
            shutil.rmtree(directory_path.as_posix())

    @property
    def xbrl_zip_path(self):
        return self.__xbrl_zip_path.as_posix()

    @xbrl_zip_path.setter
    def xbrl_zip_path(self, xbrl_zip_path):
        self.__xbrl_zip_path = Path(xbrl_zip_path)

    @property
    def output_path(self):
        return self.__output_path.as_posix()

    @output_path.setter
    def output_path(self, output_path):
        self.__output_path = Path(output_path)

    @property
    def directory_path(self):
        return self.__directory_path

    @property
    def xbrl_category(self):
        return self.__xbrl_category

    # zipファイルを解凍するメソッドを追加して解凍したファイルのパスを返す
    def __unzip_xbrl(self) -> str:
        zip_path = Path(self.xbrl_zip_path)
        with zipfile.ZipFile(zip_path.as_posix(), "r") as z:
            # フォルダ名をランダムに生成
            dir_name = str(uuid4())
            # zipファイルを解凍するパスを指定
            unzip_path = zip_path.parent / dir_name
            z.extractall(unzip_path.as_posix())
        return unzip_path.as_posix()

    def __xbrl_category(self):
        """XBRLファイルの報告詳細区分を取得します。

        Returns:
            str: XBRLファイルの報告詳細区分

        Raises:
            NotXbrlDirectoryException: ixbrlファイルが存在しない場合
            NotXbrlDirectoryException: ixbrlファイルが複数存在する場合
            NotXbrlDirectoryException: ixbrlファイルが存在するが短信サマリーが
                存在しない場合
        """

        # レポートカテゴリーを取得
        report_categories = ReportCategories().field_values()
        # 決算短信報告書
        financial_reports = ReportCategories().financial_reports()
        # 修正報告書
        revision_reports = ReportCategories().revision_reports()
        # ディレクトリパスをPathオブジェクトに変換
        directory_path = Path(self.directory_path)
        # ファイルの末尾が「ixbrl.htm」のファイルを再起的に取得してリストに格納
        ixbrl_files = list(directory_path.rglob("*ixbrl.htm"))
        if len(ixbrl_files) == 0:
            raise NotXbrlDirectoryException(
                "ixbrlファイルが存在しません。"
            )
        else:
            first_file = ixbrl_files[0].as_posix()
            for category in report_categories:
                if category in first_file:
                    if category in financial_reports:
                        if len(ixbrl_files) > 1:
                            return category
                        else:
                            raise NotXbrlDirectoryException(
                                "財務諸表ファイルが存在しません。"
                            )
                    elif category in revision_reports:
                        if len(ixbrl_files) == 1:
                            return category
                        else:
                            raise NotXbrlDirectoryException(
                                "修正報告書ファイルが複数存在します。"
                            )
                    else:
                        raise NotXbrlDirectoryException(
                            "ixbrlファイルが存在するが短信サマリーが存在しません。"
                        )

    # ディレクトリ内を再帰的に検索して指定したキーワードがファイル末尾と一致するファイルが存在するかチェックするメソッド
    def __check_xbrl_files_in_dir(self, *keywords):
        directory_path = Path(self.directory_path)
        for keyword in keywords:
            # キーワードに一致するファイルが存在しない場合はFalseを返す
            if not list(directory_path.rglob(f"*{keyword}*")):
                return False
        # キーワードに一致するファイルが存在する場合はTrueを返す
        return True

    def _xbrl_category_check(self, xbrl_category, *keywords):
        if self.xbrl_category != xbrl_category:
            raise NotXbrlTypeException("XBRLファイルの種類が異なります。")
        if self.__check_xbrl_files_in_dir(*keywords):
            raise NotXbrlTypeException("XBRLファイルの構成が異なります。")

    def _get_doc_output_path(self, doc_type: str):
        output_path = self.__output_path / doc_type
        return output_path.as_posix()

    def _create_manager(self, manager_class, doc_type):
        """共通のマネージャー生成ロジック"""
        return manager_class(self.directory_path).set_output_path(
            self._get_doc_output_path(doc_type)
        )

    def _get_data_frames(self, manager, *methods):
        """指定されたマネージャーとメソッドからDataFrameを取得する"""
        return tuple(
            getattr(manager, method)().to_DataFrame() for method in methods
        )

    def _get_xbrl_id(self, tuple):
        """tuple内のDataFrameにxbrl_idを追加する"""
        for df in tuple:
            if isinstance(df, pd.DataFrame):
                df["xbrl_id"] = self.xbrl_id

        return tuple
