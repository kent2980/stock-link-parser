import re
from typing import List, Optional

from app.exception import XbrlListEmptyError
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
        self, directory_path, xbrl_id: Optional[str] = None
    ) -> None:
        """
        IxbrlManagerクラスのコンストラクタです。

        Parameters:
            directory_path (str): XBRLファイルが格納されているディレクトリのパス

        Returns:
            None
        """
        super().__init__(directory_path, xbrl_id=xbrl_id)
        self._set_htmlbase_files("ixbrl")

        if len(self.related_files) == 0:
            raise XbrlListEmptyError("ixbrlファイルが見つかりません。")

        # プロパティの初期化
        self.__ix_non_fraction = None
        self.__ix_non_numeric = None
        self.__ix_context = None
        self.__ix_header = None
        self.__ix_stock_infos = None

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
                    row["xlink_href"], xbrl_id=self.xbrl_id
                )
                parsers.append(parser)
            except DocumentNameTagNotFoundError:
                # 後でエラーログを出力する処理を追加するために注釈を追加
                # logger.error(f"DocumentNameタグが見つかりません。[xbrl_id]: {self.xbrl_id}")
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

        # region 変数を初期化
        company_name = None  # 会社名
        securities_code = None  # 証券コード
        document_name = None  # 書類名
        reporting_date = None  # 提出日
        current_period = None  # 期間
        listed_market = None  # 上場市場
        market_section = None  # 上場区分
        url = None  # URL
        is_bs = False  # 貸借対照表の存在フラグ
        is_pl = False  # 損益計算書の存在フラグ
        is_cf = False  # キャッシュフロー計算書の存在フラグ
        is_ci = False  # 包括利益計算書の存在フラグ
        is_sce = False  # 株主資本変動計算書の存在フラグ
        is_sfp = False  # 財政状態計算書の存在フラグ
        fiscal_year_end = None  # 決算期
        tel = None  # 電話番号
        xbrl_id = None  # XBRL ID
        report_type = None  # 提出種別
        is_dividend_revision = None  # 配当の修正
        dividend_increase_rate = None  # 増配率
        is_earnings_forecast_revision = None  # 業績予想の修正
        forecast_ordinary_income_growth_rate = None  # 予想経常利益増益率
        # endregion

        # ix_non_numericがNoneの場合は、ix_non_numericを設定する
        if self.ix_non_numeric is None:
            self.__set_ix_non_numeric()

        for item in [
            item for items in self.ix_non_numeric for item in items
        ]:
            company_name = IxHeadRegex.assign_if_match(
                item, IxHeadRegex.CompanyName
            )  # 会社名
            securities_code = IxHeadRegex.assign_if_match(
                item, IxHeadRegex.SecuritiesCode
            )  # 証券コード
            document_name = IxHeadRegex.assign_if_match(
                item, IxHeadRegex.DocumentName
            )  # 書類名
            reporting_date = IxHeadRegex.assign_if_match(
                item, IxHeadRegex.ReportingDate
            )  # 提出日
            current_period = IxHeadRegex.assign_if_match(
                item, IxHeadRegex.CurrentPeriod
            )  # 期間
            url = IxHeadRegex.assign_if_match(item, IxHeadRegex.URL)  # URL
            is_bs = IxHeadRegex.is_if_match(
                item, IxHeadRegex.IsBS
            )  # 貸借対照表の存在フラグ
            is_pl = IxHeadRegex.is_if_match(
                item, IxHeadRegex.IsPL
            )  # 損益計算書の存在フラグ
            is_cf = IxHeadRegex.is_if_match(
                item, IxHeadRegex.IsCF
            )  # キャッシュフロー計算書の存在フラグ
            is_ci = IxHeadRegex.is_if_match(
                item, IxHeadRegex.IsCI
            )  # 包括利益計算書の存在フラグ
            is_sce = IxHeadRegex.is_if_match(
                item, IxHeadRegex.IsSCE
            )  # 株主資本変動計算書の存在フラグ
            is_sfp = IxHeadRegex.is_if_match(
                item, IxHeadRegex.IsSFP
            )  # 財政状態計算書の存在フラグ
            fiscal_year_end = IxHeadRegex.assign_if_match(
                item, IxHeadRegex.FiscalYearEnd
            )  # 決算期
            tel = IxHeadRegex.assign_if_match(
                item, IxHeadRegex.Tel
            )  # 電話番号

            # 東証の上場市場と上場区分を取得
            if re.search(IxHeadRegex.ListedMarket, item.name):  # 上場市場
                if item.format == "booleantrue" or item.value == "true":
                    listed_market = "東京証券取引所"
            elif re.search(
                IxHeadRegex.MarketSection, item.name
            ):  # 上場区分
                if item.format == "booleantrue" or item.value == "true":
                    market_section = item.name

            xbrl_id = item.xbrl_id  # XBRL ID
            report_type = item.report_type  # 提出種別

        ix_header = IxHeader(
            company_name=company_name,  # 会社名
            securities_code=securities_code,  # 証券コード
            document_name=document_name,  # 書類名
            reporting_date=reporting_date,  # 提出日
            current_period=current_period,  # 期間
            xbrl_id=xbrl_id,  # XBRL ID
            report_type=report_type,  # 提出種別
            listed_market=listed_market,  # 上場市場
            market_section=market_section,  # 上場区分
            url=url,  # URL
            is_bs=is_bs,  # 貸借対照表の存在フラグ
            is_pl=is_pl,  # 損益計算書の存在フラグ
            is_cf=is_cf,  # キャッシュフロー計算書の存在フラグ
            is_ci=is_ci,  # 包括利益計算書の存在フラグ
            is_sce=is_sce,  # 株主資本変動計算書の存在フラグ
            is_sfp=is_sfp,  # 財政状態計算書の存在フラグ
            fiscal_year_end=fiscal_year_end,  # 決算期
            tel=tel,  # 電話番号
            is_dividend_revision=is_dividend_revision,  # 配当の修正
            dividend_increase_rate=dividend_increase_rate,  # 増配率
            is_earnings_forecast_revision=is_earnings_forecast_revision,  # 業績予想の修正
            forecast_ordinary_income_growth_rate=forecast_ordinary_income_growth_rate,  # 予想経常利益増益率
        )

        header = ix_header

        self.__ix_header = header

        self._set_items(
            id=ix_header.xbrl_id,
            key="ix_head_title",
            items=header,
            sort_position=0,
        )


class IxHeadRegex:
    """iXBRLのヘッダー情報を取得するための正規表現を格納するクラス"""

    CompanyName = re.compile(r"CompanyName|AssetManagerREIT")  # 会社名
    SecuritiesCode = re.compile(r"Securit.*Code$")  # 証券コード
    DocumentName = re.compile(r"DocumentName")  # 書類名
    ReportingDate = re.compile(
        r"_FilingDate$|_ReportingDateOf.*Correction.*"
    )  # 提出日
    CurrentPeriod = re.compile(r"TypeOfCurrentPeriod")  # 期間
    ListedMarket = re.compile(r"TokyoStockExchange$")  # 上場市場
    MarketSection = re.compile(r"TokyoStockExchange(?!$)")  # 上場区分
    URL = re.compile(r".*URL.*")  # URL
    IsBS = re.compile(
        r".*BalanceSheet.*TextBlock$"
    )  # 貸借対照表の存在フラグ
    IsPL = re.compile(
        r"(.*StatementOfIncome|.*StatementOfProfitOrLoss).*TextBlock$"
    )  # 損益計算書の存在フラグ
    IsCF = re.compile(
        r".*StatementOfCashFlows.*TextBlock$"
    )  # キャッシュフロー計算書の存在フラグ
    IsCI = re.compile(
        r".*StatementOfComprehensiveIncome.*TextBlock$"
    )  # 包括利益計算書の存在フラグ
    IsSCE = re.compile(
        r".*StatementOfChangesInEquity.*TextBlock$"
    )  # 株主資本変動計算書の存在フラグ
    IsSFP = re.compile(
        r".*StatementOfFinancialPositionI.*TextBlock$"
    )  # 財政状態計算書の存在フラグ
    FiscalYearEnd = re.compile(r".*FiscalYearEnd$")  # 決算期
    Tel = re.compile(r".*Tel$")  # 電話番号
    DividendRevision = re.compile(r".*DividendRevision$")  # 配当の修正
    DividendIncreaseRate = re.compile(r".*DividendIncreaseRate$")  # 増配率
    EarningsForecastRevision = re.compile(
        r".*EarningsForecastRevision$"
    )  # 業績予想の修正
    ForecastOrdinaryIncomeGrowthRate = re.compile(
        r".*ForecastOrdinaryIncomeGrowthRate$"
    )  # 予想経常利益増益率

    def assign_if_match(
        cls, item: IxNonFraction, pattern: re.Pattern
    ) -> Optional[any]:
        if re.search(pattern, item.name):
            return item.value
        return None

    def is_if_match(cls, item: IxNonFraction, pattern: re.Pattern) -> bool:
        return re.search(pattern, item.name)
