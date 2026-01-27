import re
from typing import List, Optional

from src.exception import XbrlListEmptyError
from src.exception.base_exception import DataProcessingError, ParserInitError
from src.exception.error_handler import ErrorContext, get_logger
from src.exception.xbrl_parser_exception import DocumentNameTagNotFoundError
from src.ix_manager import BaseXbrlManager
from src.ix_parser import IxbrlParser
from src.ix_tag import IxContext, IxHeader, IxNonFraction, IxNonNumeric

# モジュールレベルのロガーを取得
logger = get_logger(__name__)


class IXBRLManager(BaseXbrlManager[IxbrlParser]):
    """iXBRLデータの解析を行うクラス

    raise   - XbrlListEmptyError("ixbrlファイルが見つかりません。")
    """

    # クラスレベルの定数として定義
    HEADER_PATTERNS = {
        'company_name': r"CompanyName|AssetManagerREIT",
        'securities_code': r"Securit.*Code|SecurityCode",
        'document_name': r"DocumentName",
        'reporting_date': r"FilingDate|ReportingDateOf.*Correction",
        'current_period': r"TypeOfCurrentPeriod|CurrentFiscalYearEndDate",
        'url': r".*URL.*",
        'fiscal_year_end': r"FiscalYearEnd",
        'tel': r".*Tel$",
        'specific_business': r"SpecificBusiness",
        'listed_market': r"TokyoStockExchange$|JapanSecuritiesDealersAssociation",
        'market_section': r"TokyoStockExchange(?!$)",
        'is_bs': r".*BalanceSheet.*TextBlock$",
        'is_pl': r"(.*StatementOfIncome|.*StatementOfProfitOrLoss).*TextBlock$",
        'is_cf': r".*StatementOfCashFlows.*TextBlock$",
        'is_ci': r".*StatementOfComprehensiveIncome.*TextBlock$",
        'is_sce': r".*StatementOfChangesInEquity.*TextBlock$",
        'is_sfp': r".*StatementOfFinancialPositionI.*TextBlock$",
    }

    def __init__(
        self, directory_path: str, head_item_key: Optional[str] = None
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
        self._ix_non_fraction: Optional[IxNonFraction] = None
        self._ix_non_numeric: Optional[IxNonNumeric] = None
        self._ix_context: Optional[IxContext] = None
        self._ix_header: Optional[IxHeader] = None

        # 初期化メソッドを実行
        self._init_parser()
        self._init_manager()
        self._set_source_file_ids()

    @property
    def ix_non_fraction(self) -> Optional[IxNonFraction]:
        return self._ix_non_fraction

    @property
    def ix_non_numeric(self) -> Optional[IxNonNumeric]:
        return self._ix_non_numeric

    @property
    def ix_context(self) -> Optional[IxContext]:
        return self._ix_context

    @property
    def ix_header(self) -> Optional[IxHeader]:
        return self._ix_header

    def _process_parser_data(
        self,
        parser_method_name: str,
        item_key: str,
        property_name: str
    ) -> List[List]:
        """parserのデータを処理します。

        Parameters:
            parser_method_name (str): parserのメソッド名
            item_key (str): アイテムのキー
            property_name (str): プロパティの名前

        Returns:
            処理されたデータのリスト、または失敗時はNone
        """
        # 既に設定されている場合は早期リターン
        if getattr(self, property_name, None) is not None:
            return None

        rows: List[List] = []
        error_count = 0

        for parser in self.parsers:
            source_file_id = getattr(parser, 'source_file_id', 'unknown')

            with ErrorContext(
                f"{parser_method_name}の処理",
                DataProcessingError,
                reraise=False,
                logger=logger,
            ) as ctx:
                parser_method = getattr(parser, parser_method_name)
                parser_method()

                data = parser.data
                rows.append(data)

                self._set_items(id=source_file_id, key=item_key, items=data)

            if not ctx.success:
                error_count += 1
                logger.debug(
                    f"{parser_method_name}の処理をスキップ "
                    f"(source_file_id={source_file_id}): {ctx.error}"
                )

        if error_count > 0:
            logger.warning(
                f"{parser_method_name}で{error_count}件のエラーが発生しました"
            )

        setattr(self, property_name, rows)
        return rows

    def _init_parser(self) -> None:
        """parserを初期化します。"""
        parsers: List[IxbrlParser] = []
        skipped_files: List[str] = []

        for _, row in self.related_files.iterrows():
            xlink_href = row.get("xlink_href", "unknown")

            with ErrorContext(
                f"パーサーの初期化 ({xlink_href})",
                ParserInitError,
                reraise=False,
                logger=logger,
            ) as ctx:
                parser = IxbrlParser(
                    row["xlink_href"], head_item_key=self.head_item_key
                )
                parsers.append(parser)

            if not ctx.success:
                skipped_files.append(xlink_href)

        if skipped_files:
            logger.info(
                f"{len(skipped_files)}個のファイルをスキップしました "
                f"(head_item_key={self.head_item_key})"
            )

        self.parsers = parsers

    def _init_manager(self) -> None:
        """managerを初期化します。"""
        self._ix_non_fraction = self._get_ix_non_fraction()  # 他のメソッドを呼び出す前に呼び出す
        self.set_source_file(self.parsers, class_name="ix")
        self._ix_non_numeric = self._get_ix_non_numeric()  # _get_ix_header()の前に呼び出す必要がある
        self._ix_header = self._get_ix_header()  # ix_non_numericが必要なため、後に呼び出す
        self._ix_context = self._get_ix_context()

        self.items.sort(key=lambda x: x.sort_position)

    def _get_ix_non_fraction(self) -> List[List[IxNonFraction]]:
        """
        ix_non_fraction属性を設定します。
        非分数のIXBRLデータを取得します。

        Yields:
            dict: 非分数のIXBRLデータ
        """
        return self._process_parser_data(
            parser_method_name="set_ix_non_fraction",
            item_key="ix_non_fraction",
            property_name="_IXBRLManager_ix_non_fraction"
        )

    def _get_ix_non_numeric(self) -> List[List[IxNonNumeric]]:
        """
        ix_non_numeric属性を設定します。
        非数値のIXBRLデータを取得します。

        Yields:
            dict: 非数値のIXBRLデータ
        """
        return self._process_parser_data(
            parser_method_name="set_ix_non_numeric",
            item_key="ix_non_numeric",
            property_name="_IXBRLManager_ix_non_numeric"
        )
    def _get_ix_context(self) -> List[List[IxContext]]:
        """
        ix_context属性を設定します。
        iXBRLのコンテキスト情報を取得します。

        Yields:
            dict: iXBRLのコンテキスト情報
        """
        return self._process_parser_data(
            parser_method_name="set_ix_context",
            item_key="ix_context",
            property_name="_IXBRLManager_ix_context"
        )

    def _get_ix_header(self):
        """ix_header属性を設定します。"""

        # ここに機能を追加する手順を記述します。
        # 新しい機能を追加する際は、変数名を定義して初期化してください。
        # 例: company_name = None
        # 次にitem_listのループ処理を行い、item.nameに対して正規表現を使用して値を取得します。
        # 例: if re.search(r"CompanyName", item.name): company_name = item.value
        # IXheaderクラスの定義に移動して、新しい変数を追加してください。
        # 最後にIxHeaderクラスのインスタンスを作成し、ix_headerに新しい変数を代入します。
        # 例: ix_header = IxHeader(company_name=company_name)


        # 早期リターンチェックを追加
        if self._ix_header is not None:
            return None

        # 初期値を辞書で管理
        header_data = {
            'company_name': None,
            'securities_code': None,
            'document_name': None,
            'reporting_date': None,
            'current_period': None,
            'listed_market': None,
            'market_section': None,
            'url': None,
            'is_bs': False,
            'is_pl': False,
            'is_cf': False,
            'is_ci': False,
            'is_sce': False,
            'is_sfp': False,
            'fy_year_end': None,  # IxHeaderのフィールド名に合わせて修正
            'tel': None,
            'report_type': None,
            'specific_business': None,
        }

        # 非数値データを取得
        non_numeric_lists: List[List[IxNonNumeric]] = self.ix_non_numeric
        if non_numeric_lists is None:
            non_numeric_lists = []
        non_numeric_list = [item for items in non_numeric_lists for item in items]

        # パターンマッチングで値を抽出
        for item in non_numeric_list:
            header_data['report_type'] = item.report_type

            # 各フィールドをパターンマッチング
            self._extract_header_field(item, header_data)

        # IxHeaderインスタンスを作成
        ix_header = IxHeader(
            item_key=self.head_item_key,
            **header_data
        )

        self._set_items(
            id=self.head_item_key,
            key="ix_head_title",
            items=[ix_header],
            sort_position=0,
        )

        return ix_header

    def _extract_header_field(self, item: IxNonNumeric, header_data: dict) -> None:
        """アイテムから該当するヘッダーフィールドを抽出"""

        # 文字列フィールドの処理
        string_fields = [
            'company_name', 'securities_code', 'document_name',
            'reporting_date', 'current_period', 'url',
            'fy_year_end', 'tel'  # IxHeaderのフィールド名に合わせて修正
        ]

        for field in string_fields:
            # HEADER_PATTERNSのキーとheader_dataのキーが異なる場合のマッピング
            pattern_key = field
            if field == 'fy_year_end':
                pattern_key = 'fiscal_year_end'  # HEADER_PATTERNSではfiscal_year_endを使用
            if re.search(self.HEADER_PATTERNS[pattern_key], item.name):
                header_data[field] = item.value
                return

        # ブール値フィールドの処理
        if re.search(self.HEADER_PATTERNS['specific_business'], item.name):
            header_data['specific_business'] = item.value == "true"
            return

        # 取引所情報の処理
        if re.search(self.HEADER_PATTERNS['listed_market'], item.name):
            if item.format == "booleantrue" or item.value == "true":
                header_data['listed_market'] = "東京証券取引所"
                return

        if re.search(self.HEADER_PATTERNS['market_section'], item.name):
            if item.format == "booleantrue" or item.value == "true":
                header_data['market_section'] = item.name
                return

        # 財務諸表フラグの処理
        statement_flags = {
            'is_bs': 'is_bs',
            'is_pl': 'is_pl',
            'is_cf': 'is_cf',
            'is_ci': 'is_ci',
            'is_sce': 'is_sce',
            'is_sfp': 'is_sfp',
        }

        for flag_key, flag_name in statement_flags.items():
            if re.search(self.HEADER_PATTERNS[flag_key], item.name):
                header_data[flag_name] = True
                return
