"""Webアプリ向けデータ構造への変換ユーティリティ

XBRLデータをWebアプリで扱いやすい形式に変換します。
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional


def format_numeric_value(
    numeric: Optional[str],
    scale: Optional[str] = None,
    decimals: Optional[str] = None,
    unit_ref: Optional[str] = None,
    display_numeric: Optional[str] = None,
    display_scale: Optional[str] = None,
) -> Dict[str, Any]:
    """数値をWebアプリ向けにフォーマットする

    Args:
        numeric: 数値文字列
        scale: スケール
        decimals: 小数点位置
        unit_ref: 単位参照
        display_numeric: 表示用数値
        display_scale: 表示用スケール

    Returns:
        フォーマットされた数値情報
    """
    # 生の数値を計算
    raw_value = None
    if numeric:
        try:
            # 数値をパース
            num = Decimal(str(numeric))
            # スケールを適用
            if scale:
                scale_int = int(scale)
                num = num * (10 ** scale_int)
            raw_value = int(num)
        except (ValueError, TypeError):
            raw_value = None

    # フォーマット済み文字列
    formatted = display_numeric or numeric or "0"
    
    # 単位
    unit = display_scale or (f"{10**int(scale)}円" if scale else "円")
    
    # 通貨単位
    currency = unit_ref or "JPY"
    
    # 完全な表示文字列
    display_text = f"{formatted}{unit}" if formatted and unit else formatted

    return {
        "raw": raw_value,
        "formatted": formatted,
        "unit": unit,
        "currency": currency,
        "display": display_text,
        "decimals": int(decimals) if decimals else None,
        "scale": int(scale) if scale else None,
    }


def extract_primary_label(labels: List[Dict[str, Any]]) -> Dict[str, Any]:
    """主要ラベルを抽出する

    優先順位:
    1. 日本語のverboseLabel
    2. 日本語のstandardLabel
    3. 最初の日本語ラベル
    4. 最初のラベル

    Args:
        labels: ラベルリスト

    Returns:
        主要ラベル情報
    """
    if not labels:
        return {
            "primary": None,
            "short": None,
            "english": None,
            "lang": None,
            "all": [],
        }

    # 優先順位でラベルを検索
    primary_label = None
    short_label = None
    english_label = None

    for label in labels:
        role = label.get("role", "")
        lang = label.get("lang", "")
        text = label.get("label", "")

        # 日本語のverboseLabelを優先
        if lang == "ja" and "verboseLabel" in role and not primary_label:
            primary_label = text

        # 日本語のstandardLabel
        if lang == "ja" and "standardLabel" in role and not short_label:
            short_label = text

        # 英語ラベル
        if lang == "en" and not english_label:
            english_label = text

    # フォールバック
    if not primary_label:
        # 最初の日本語ラベル
        ja_labels = [l for l in labels if l.get("lang") == "ja"]
        if ja_labels:
            primary_label = ja_labels[0].get("label")
        else:
            # 最初のラベル
            primary_label = labels[0].get("label") if labels else None

    if not short_label:
        short_label = primary_label

    return {
        "primary": primary_label,
        "short": short_label,
        "english": english_label,
        "lang": "ja" if primary_label else (labels[0].get("lang") if labels else None),
        "all": labels,
    }


def expand_context(
    context_id: Optional[str], context_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """コンテキスト情報を展開する

    Args:
        context_id: コンテキストID（配列の最初の要素）
        context_data: ix_contextデータ（オプション）

    Returns:
        展開されたコンテキスト情報
    """
    if not context_id:
        return {"id": None, "period": None, "entity": None}

    # context_idが配列の場合は最初の要素を取得
    if isinstance(context_id, list):
        context_id = context_id[0] if context_id else None

    if not context_id:
        return {"id": None, "period": None, "entity": None}

    # context_dataから詳細情報を取得
    period_info = None
    entity_info = None

    if context_data:
        for ctx in context_data:
            if isinstance(ctx, dict):
                ctx_id = ctx.get("context_id") or ctx.get("id")
                if ctx_id == context_id:
                    # 期間情報を抽出
                    period_start = ctx.get("period_start") or ctx.get("start_date")
                    period_end = ctx.get("period_end") or ctx.get("end_date")
                    period_type = ctx.get("period_type") or ctx.get("type")

                    if period_start or period_end:
                        period_info = {
                            "type": period_type,
                            "start": period_start,
                            "end": period_end,
                        }

                    # エンティティ情報を抽出
                    entity_id = ctx.get("entity_identifier") or ctx.get("entity_id")
                    entity_scheme = ctx.get("entity_scheme") or ctx.get("scheme")

                    if entity_id:
                        entity_info = {
                            "identifier": entity_id,
                            "scheme": entity_scheme,
                        }

                    break

    return {
        "id": context_id,
        "period": period_info,
        "entity": entity_info,
    }


def format_for_web_app(
    item: Dict[str, Any],
    context_data: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """XBRLアイテムをWebアプリ向けにフォーマットする

    Args:
        item: XBRLアイテム（ix_non_fraction_enrichedまたはix_non_numeric_enriched）
        context_data: ix_contextデータ（オプション）

    Returns:
        Webアプリ向けに最適化されたデータ構造
    """
    # 基本情報
    result = {
        "id": item.get("item_key"),
        "element_name": item.get("name"),
        "metadata": {
            "source_file_id": item.get("source_file_id"),
            "head_item_key": item.get("head_item_key"),
            "format": item.get("format"),
            "decimals": int(item.get("decimals")) if item.get("decimals") else None,
            "scale": int(item.get("scale")) if item.get("scale") else None,
            "xbrl_type": item.get("xbrl_type"),
            "report_type": item.get("report_type"),
            "ixbrl_role": item.get("ixbrl_role"),
        },
    }

    # ラベル情報
    labels = item.get("labels", [])
    result["label"] = extract_primary_label(labels)

    # 数値情報（ix_non_fractionの場合）
    if "numeric" in item:
        result["value"] = format_numeric_value(
            numeric=item.get("numeric"),
            scale=item.get("scale"),
            decimals=item.get("decimals"),
            unit_ref=item.get("unit_ref"),
            display_numeric=item.get("display_numeric"),
            display_scale=item.get("display_scale"),
        )
        result["is_numeric"] = True
    else:
        # 非数値の場合
        result["value"] = {
            "text": item.get("value"),
            "formatted": item.get("value"),
        }
        result["is_numeric"] = False

    # コンテキスト情報
    context_id = item.get("context")
    result["context"] = expand_context(context_id, context_data)

    # 関係情報
    result["relationships"] = {
        "calculation": item.get("calculation_links", []),
        "definition": item.get("definition_links", []),
        "presentation": item.get("presentation_links", []),
    }

    # レポート情報
    result["report"] = {
        "type": item.get("report_type"),
        "role": item.get("ixbrl_role"),
        "category": item.get("xbrl_type"),
    }

    return result


def format_list_for_web_app(
    items: List[Dict[str, Any]],
    context_data: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """XBRLアイテムリストをWebアプリ向けにフォーマットする

    Args:
        items: XBRLアイテムリスト
        context_data: ix_contextデータ（オプション）

    Returns:
        Webアプリ向けに最適化されたデータ構造のリスト
    """
    return [format_for_web_app(item, context_data) for item in items]
