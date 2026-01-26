import os
import re
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

from src.exception.xbrl_parser_exception import DocumentNameTagNotFoundError
from src.ix_tag import IxContext, IxNonFraction, IxNonNumeric
from src.utils import Utils

from . import BaseXBRLParser


class IxbrlParser(BaseXBRLParser):
    """iXBRLを解析するクラス"""

    def __init__(
        self,
        xbrl_url: str,
        output_path: Optional[str] = None,
        head_item_key: Optional[str] = None,
    ) -> None:
        super().__init__(xbrl_url, output_path, head_item_key)

        # ファイル名を検証
        self._assert_valid_basename("ixbrl.htm")

        # プロパティの初期化
        self.__report_type: Optional[str] = None
        self.__ixbrl_role: Optional[Dict[str, str]] = None
        self.__ix_non_fraction: Optional[List[IxNonFraction]] = None
        self.__ix_non_numeric: Optional[List[IxNonNumeric]] = None
        self.__ix_context: Optional[List[IxContext]] = None

        # 初期化処理
        self.__init_parser()

    @property
    def report_type(self) -> Optional[str]:
        return self.__report_type

    @property
    def ixbrl_role(self) -> Optional[Dict[str, str]]:
        return self.__ixbrl_role

    @property
    def ix_non_fraction(self) -> Optional[List[IxNonFraction]]:
        return self.__ix_non_fraction

    @property
    def ix_non_numeric(self) -> Optional[List[IxNonNumeric]]:
        return self.__ix_non_numeric

    @property
    def ix_context(self) -> Optional[List[IxContext]]:
        return self.__ix_context

    def __set_report_type(self, xbrl_url: str) -> Optional[str]:
        """レポートの種類を設定する"""
        types = [
            "edjp",
            "edus",
            "edif",
            "edit",
            "rvdf",
            "rvfc",
            "rejp",
            "rrdf",
            "rrfc",
            "efjp",
        ]
        if xbrl_url.startswith("http"):
            parse_url = urlparse(xbrl_url)
            file_name = os.path.basename(parse_url.path)
        else:
            file_name = os.path.basename(xbrl_url)
        for type in types:
            if type in file_name:
                return type
        return None

    def __set_ixbrl_role(self) -> Dict[str, str]:
        """ドキュメントの要素を設定する"""
        file_name = self.basename
        ixbrl_type = file_name.split("-")[1]
        role: Dict[str, str] = {}
        if "fr" not in file_name:
            role = {
                "type": "summary",
                "jp_label": "短信サマリー",
                "en_label": "DocumentEntityInformation",
            }
        else:
            try:
                en_label_tag = self.soup.find(
                    name="ix:nonNumeric",
                    attrs={"name": re.compile(r"^.*TextBlock$")},
                )
                en_label = (
                    en_label_tag.get("name").split(":")[-1].replace("TextBlock", "")
                )
            except AttributeError:
                raise DocumentNameTagNotFoundError(self.basename)
            role = {
                "type": ixbrl_type,
                # "jp_label": const["document_name"][ixbrl_type],
                "en_label": en_label,
            }
        return role

    def __init_parser(self) -> None:
        self.__report_type = self.__set_report_type(self.xbrl_url)
        self.__ixbrl_role = self.__set_ixbrl_role()

    def set_ix_non_numeric(self) -> "IxbrlParser":
        """iXBRLの非数値情報を取得する

        Returns:
            IxbrlParser: 自身のインスタンス
        """

        if self.__ix_non_numeric:
            self._set_data(self.__ix_non_numeric)
            return self

        lists: List[IxNonNumeric] = []

        tags = self.soup.find_all(name="ix:nonNumeric")

        for tag in tags:
            # _____attr[contextRef]
            context = str(tag.get("contextRef")).split("_")

            # _____attr[xsi:nil]
            xsi_nil = True if tag.get("xsi:nil") == "true" else False

            # _____attr[escape]
            escape = True if tag.get("escape") == "true" else False

            # _____attr[name]
            name = tag.get("name").replace(":", "_")

            # _____attr[text]
            if escape is False:
                # text属性が存在する場合は取得
                text = tag.text.replace("　", "").replace(" ", "")
                # textの数字を半角に変換
                text = re.sub(
                    r"[０-９]",
                    lambda x: chr(ord(x.group(0)) - 0xFEE0),
                    text,
                )
                # textの全角文字を半角に変換
                text = Utils.normalize_text(text)
            else:
                text = None

            format_str = tag.get("format").split(":")[-1] if tag.get("format") else None

            # textが日付文字列の場合はフォーマットを統一
            if format_str:
                text, format_str = Utils.date_str_to_format(
                    text, format_str
                )  # pragma: no cover

            # textが証券コードの場合は4文字に統一
            if any(item in name for item in ["SecuritiesCode", "SecurityCode"]):
                text = text[0:4]  # pragma: no cover

            # textが空白の場合はNoneに変換
            if text == "":
                text = None

            # format_strがbooleantrueの場合はtrueに変換
            text = "true" if format_str == "booleantrue" else text
            # format_strがbooleanfalseの場合はfalseに変換
            text = "false" if format_str == "booleanfalse" else text

            # _____attr[format_str]
            # textがtrueまたはfalseの場合はformat_strをbooleanに変換
            if text:
                format_str = "string" if text else format_str
                format_str = "number" if re.search(r"^\d+$", text) else format_str
                format_str = "decimal" if re.search(r"^\d+\.\d+$", text) else format_str
                format_str = "boolean" if text in ["true", "false"] else format_str
                format_str = (
                    "dateyearmonthday"
                    if re.search(r"^\d{4}-\d{2}-\d{2}$", text)
                    else format_str
                )
                format_str = (
                    "telephone"
                    if re.search(r"^\(?\d{2,4}\)?-?\d{2,4}-?\d{4}$", text)
                    else format_str
                )
                format_str = (
                    "url"
                    if re.search(r"^https?://[\w/:%#\$&\?\(\)~\.=\+\-]+$", text)
                    else format_str
                )

            # 辞書に追加
            inn = IxNonNumeric(
                head_item_key=self.head_item_key,
                context=context,
                name=name,
                xsi_nil=xsi_nil,
                escape=escape,
                format=format_str,
                value=text,
                report_type=self.report_type,
                ixbrl_role=self.ixbrl_role["en_label"],
                source_file_id=self.source_file_id,
                xbrl_type=self.xbrl_type,
            )
            lists.append(inn)

        self._set_data(lists)

        self.__ix_non_numeric = lists

        return self

    def set_ix_non_fraction(self) -> "IxbrlParser":
        """iXBRLの非分数情報を取得する

        Returns:
            IxbrlParser: 自身のインスタンス
        """
        # ix_non_fractionが存在する場合はそのまま返す

        if self.__ix_non_fraction:
            self._set_data(self.__ix_non_fraction)
            return self

        lists: List[IxNonFraction] = []
        tags = self.soup.find_all(name="ix:nonFraction")
        for tag in tags:
            # _____attr[format]
            format_str = tag.get("format").split(":")[-1] if tag.get("format") else None

            # _____attr[contextRef]
            context = str(tag.get("contextRef")).split("_")

            # _____attr[decimals]
            decimals = tag.get("decimals")

            # _____attr[name]
            name = tag.get("name").replace(":", "_")

            # _____attr[scale]
            scale = tag.get("scale")

            # _____attr[sign]
            sign = tag.get("sign")

            # _____attr[unitRef]
            unit_ref = tag.get("unitRef")

            # _____attr[xsi:nil]
            xsi_nil = True if tag.get("xsi:nil") == "true" else False

            # _____attr[numeric]
            numeric: Optional[Union[str, Decimal]] = tag.text

            if numeric is not None or numeric != "":
                if len(numeric) > 0:
                    try:
                        # xx円xx銭の場合は、xx.xxに変換
                        numeric = numeric.replace("円", ".").replace("銭", "")

                        # numericのカンマを削除
                        numeric = numeric.replace(",", "")
                        # numericをDecimalに変換
                        numeric = Decimal(numeric)
                        # sign属性が存在する場合は符号を反映
                        numeric = numeric * -1 if sign == "-" else numeric
                        # numericを文字列に変換
                        # numeric = str(numeric)

                    # 数値変換に失敗した場合はそのまま文字列として取得
                    except (ValueError, InvalidOperation, TypeError):
                        numeric = (
                            str(numeric) if isinstance(numeric, Decimal) else numeric
                        )

            # numericが空白の場合はNoneに変換
            if numeric == "":
                numeric = None

            # _____attr[display_numeric]
            display_numeric: Optional[str] = None
            if numeric:
                if sign == "-":
                    display_numeric = f"△{str(tag.text)}"
                else:
                    display_numeric = str(tag.text)

            # _____attr[display_scale]
            display_scale: Optional[str] = None
            if scale:
                # 日本円の場合
                if "JPY" in unit_ref:
                    if scale == "6":
                        display_scale = "百万円"
                    elif scale == "3":
                        display_scale = "千円"
                    elif scale == "0":
                        display_scale = "円"
                # 米ドルの場合
                elif "USD" in unit_ref:
                    if scale == "6":
                        display_scale = "百万ドル"
                    elif scale == "3":
                        display_scale = "千ドル"
                    elif scale == "0":
                        display_scale = "ドル"
                # パーセントの場合
                elif "Pure" in unit_ref:
                    if scale == "-2":
                        display_scale = "%"
                # 株式の場合
                elif unit_ref == "Shares":
                    display_scale = "株"

            inn = IxNonFraction(
                head_item_key=self.head_item_key,
                context=context,
                decimals=decimals,
                format=format_str,
                name=name,
                scale=scale,
                unit_ref=unit_ref,
                xsi_nil=xsi_nil,
                numeric=numeric,
                report_type=self.report_type,
                ixbrl_role=self.ixbrl_role["en_label"],
                source_file_id=self.source_file_id,
                xbrl_type=self.xbrl_type,
                sign=sign,
                display_numeric=display_numeric,
                display_scale=display_scale,
            )
            lists.append(inn)

        self._set_data(lists)

        self.__ix_non_fraction = lists

        return self

    def set_ix_context(self) -> "IxbrlParser":
        if self.__ix_context:
            self._set_data(self.__ix_context)
            return self

        lists: List[IxContext] = []
        tags = self.soup.find_all(name="xbrli:context")
        for tag in tags:
            # _____attr[id]
            context_id = tag.get("id")
            period: Dict[str, Optional[str]] = {
                "start": None,
                "end": None,
                "instant": None,
            }
            for period_tag in tag.find_all(name="xbrli:period"):
                start, end, instant = None, None, None
                # _____attr[start]
                if period_tag.find(name="xbrli:startDate") is not None:
                    start = period_tag.find(name="xbrli:startDate").text
                # _____attr[end]
                if period_tag.find(name="xbrli:endDate") is not None:
                    end = period_tag.find(name="xbrli:endDate").text
                # _____attr[instant]
                if period_tag.find(name="xbrli:instant") is not None:
                    instant = period_tag.find(name="xbrli:instant").text
                period = {"start": start, "end": end, "instant": instant}

            scenario: List[Dict[str, str]] = []
            for value in tag.find_all(name="xbrli:scenario"):
                for explicit_member in value.find_all(name="xbrldi:explicitMember"):
                    dimension = explicit_member.get("dimension").replace(":", "_")
                    scenario_value = explicit_member.text.replace(":", "_")
                    scenario.append({"dimension": dimension, "value": scenario_value})

            inn = IxContext(
                head_item_key=self.head_item_key,
                context_id=context_id,
                period=period,
                scenario=scenario,
                source_file_id=self.source_file_id,
            )
            lists.append(inn)

        self._set_data(lists)

        self.__ix_context = lists

        return self
