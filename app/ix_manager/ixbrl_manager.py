import re
from typing import List, Optional

from app.exception import XbrlListEmptyError
from app.exception.xbrl_model_exception import NotXbrlDirectoryException
from app.exception.xbrl_parser_exception import (
    DocumentNameTagNotFoundError,
)
from app.ix_manager import BaseXbrlManager
from app.ix_parser import IxbrlParser
from app.ix_tag import IxContext, IxHeader, IxNonFraction, IxNonNumeric


class IXBRLManager(BaseXbrlManager):
    """iXBRLデータの解析を行うクラス

    raise   - XbrlListEmptyError("ixbrlファイルが見つかりません。")
    """

    def __init__(
        self, directory_path, head_item_key: Optional[str] = None
    ) -> None:
        """
        IxbrlManagerクラスのコンストラクタです。

        Parameters:
            directory_path (str): XBRLファイルが格納されているディレクトリのパス

        Returns:
            None
        """
        super().__init__(directory_path, head_item_key=head_item_key)
        self._set_htmlbase_files("ixbrl")

        if len(self.related_files) == 0:
            raise XbrlListEmptyError("ixbrlファイルが見つかりません。")

        # プロパティの初期化
        self.__ix_non_fraction = None
        self.__ix_non_numeric = None
        self.__ix_context = None
        self.__ix_header = None

        # 初期化メソッドを実行
        self.__init_parser()
        self.__init_manager()
        self._set_source_file_ids()

    @property
    def ix_non_fraction(self):
        return self.__ix_non_fraction

    @property
    def ix_non_numeric(self):
        return self.__ix_non_numeric

    @property
    def ix_context(self):
        return self.__ix_context

    @property
    def ix_header(self):
        return self.__ix_header

    def __init_parser(self):
        """parserを初期化します。"""
        parsers: List[IxbrlParser] = []
        for _, row in self.related_files.iterrows():
            try:
                parser = IxbrlParser(
                    row["xlink_href"], head_item_key=self.head_item_key
                )
                parsers.append(parser)
            except DocumentNameTagNotFoundError:
                # 後でエラーログを出力する処理を追加するために注釈を追加
                # logger.error(f"DocumentNameタグが見つかりません。[head_item_key]: {self.head_item_key}")
                pass

        self._set_parsers(parsers)

    def __init_manager(self):
        """managerを初期化します。"""
        self.__set_ix_header()
        self.set_source_file(self.parsers, class_name="ix")
        self.__set_ix_non_fraction()
        self.__set_ix_non_numeric()
        self.__set_ix_context()

        self.items.sort(key=lambda x: x["sort_position"])

    def __set_ix_non_fraction(self):
        """
        ix_non_fraction属性を設定します。
        非分数のIXBRLデータを取得します。

        Yields:
            dict: 非分数のIXBRLデータ
        """

        rows: List[List[IxNonFraction]] = []

        for parser in self.parsers:

            id = parser.source_file_id

            parser: IxbrlParser = parser.set_ix_non_fraction()

            data = parser.data

            rows.append(data)

            self._set_items(id=id, key="ix_non_fraction", items=data)

        self.__ix_non_fraction = rows

    def __set_ix_non_numeric(self):
        """
        ix_non_numeric属性を設定します。
        非数値のIXBRLデータを取得します。

        Yields:
            dict: 非数値のIXBRLデータ
        """

        # ix_non_numericが設定されている場合は、何もしない
        if self.ix_non_numeric:
            return None

        rows: List[List[IxNonNumeric]] = []

        for parser in self.parsers:

            id = parser.source_file_id

            data = parser.set_ix_non_numeric()

            data = parser.data

            rows.append(data)

            self._set_items(id=id, key="ix_non_numeric", items=data)

        self.__ix_non_numeric = rows

    def __set_ix_context(self):
        """
        ix_context属性を設定します。
        iXBRLのコンテキスト情報を取得します。

        Yields:
            dict: iXBRLのコンテキスト情報
        """

        rows: List[List[IxContext]] = []

        for parser in self.parsers:

            id = parser.source_file_id

            parser = parser.set_ix_context()

            data = parser.data

            rows.append(data)

            self._set_items(id=id, key="ix_context", items=data)

        self.__ix_context = rows

    def __set_ix_header(self):
        """ix_header属性を設定します。"""

        # ここに機能を追加する手順を記述します。
        # 新しい機能を追加する際は、変数名を定義して初期化してください。
        # 例: company_name = None
        # 次にitem_listのループ処理を行い、item.nameに対して正規表現を使用して値を取得します。
        # 例: if re.search(r"CompanyName", item.name): company_name = item.value
        # IXheaderクラスの定義に移動して、新しい変数を追加してください。
        # 最後にIxHeaderクラスのインスタンスを作成し、ix_headerに新しい変数を代入します。
        # 例: ix_header = IxHeader(company_name=company_name)

        # region 変数を初期化
        company_name = None
        securities_code = None
        document_name = None
        reporting_date = None
        current_period = None
        listed_market = None
        market_section = None
        url = None
        is_bs = False
        is_pl = False
        is_cf = False
        is_ci = False
        is_sce = False
        is_sfp = False
        fiscal_year_end = None
        tel = None
        report_type = None
        specific_business = None
        # endregion

        # ix_non_numericがNoneの場合は、ix_non_numericを設定する
        if self.ix_non_numeric is None:
            self.__set_ix_non_numeric()

        # ix_non_numericからデータを取得
        non_numeric_lists: List[List[IxNonNumeric]] = self.ix_non_numeric
        non_numeric_list = [
            item for items in non_numeric_lists for item in items
        ]

        # 非数値情報からマッピングとデータ取得処理を行う
        for item in non_numeric_list:
            # 機能を追加する際は、ここにマッピングとデータ取得処理を追加してください。

            # region 基本情報の取得
            report_type = item.report_type  # 提出種別
            # endregion

            # region 会社情報の取得
            if re.search(  # 会社名
                r"CompanyName|AssetManagerREIT", item.name
            ):
                company_name = item.value
            elif re.search(r"Securit.*Code$", item.name):  # 証券コード
                securities_code = item.value
            elif re.search(r"DocumentName", item.name):  # 書類名
                document_name = item.value
            elif re.search(  # 提出日
                r"_FilingDate$|_ReportingDateOf.*Correction.*",
                item.name,
            ):
                reporting_date = item.value
            elif re.search(r"TypeOfCurrentPeriod", item.name):  # 期末
                current_period = item.value
            elif re.search(r".*URL.*", item.name):  # URL
                url = item.value
            elif re.search(
                r"(?=.*\_FiscalYearEnd.*)", item.name
            ):  # 決算期
                fiscal_year_end = item.value
            elif re.search(r".*Tel$", item.name):  # 電話番号
                tel = item.value
            elif re.search(r"SpecificBusiness", item.name):  # 特定事業
                specific_business = item.value == "true"
            # endregion

            # region 取引所情報の取得
            elif re.search(r"TokyoStockExchange$", item.name):  # 上場市場
                if item.format == "booleantrue" or item.value == "true":
                    listed_market = "東京証券取引所"
            elif re.search(  # 上場区分
                r"TokyoStockExchange(?!$)", item.name
            ):
                if item.format == "booleantrue" or item.value == "true":
                    market_section = item.name
            # endregion

            # region 各財務諸表有無の取得
            elif re.search(
                r".*BalanceSheet.*TextBlock$", item.name
            ):  # 貸借対照表の有無
                is_bs = True
            elif re.search(  # 損益計算書の有無
                r"(.*StatementOfIncome|.*StatementOfProfitOrLoss).*TextBlock$",
                item.name,
            ):
                is_pl = True
            elif re.search(  # キャッシュフロー計算書の有無
                r".*StatementOfCashFlows.*TextBlock$", item.name
            ):
                is_cf = True
            elif re.search(  # 総合利益計算書の有無
                r".*StatementOfComprehensiveIncome.*TextBlock$",
                item.name,
            ):
                is_ci = True
            elif re.search(  # 株主資本変動計算書の有無
                r".*StatementOfChangesInEquity.*TextBlock$", item.name
            ):
                is_sce = True
            elif re.search(  # 財務状態計算書の有無
                r".*StatementOfFinancialPositionI.*TextBlock$",
                item.name,
            ):
                is_sfp = True
            # endregion

        ix_header = IxHeader(
            item_key=self.head_item_key,
            company_name=company_name,
            securities_code=securities_code,
            document_name=document_name,
            reporting_date=reporting_date,
            current_period=current_period,
            report_type=report_type,
            listed_market=listed_market,
            market_section=market_section,
            url=url,
            is_bs=is_bs,
            is_pl=is_pl,
            is_cf=is_cf,
            is_ci=is_ci,
            is_sce=is_sce,
            is_sfp=is_sfp,
            fy_year_end=fiscal_year_end,
            tel=tel,
            specific_business=specific_business,
            # ...機能を追加する際は、ここに新しい変数を追加してください。
        )

        header = ix_header

        self.__ix_header = header

        self._set_items(
            id=self.head_item_key,
            key="ix_head_title",
            items=header,
            sort_position=0,
        )
