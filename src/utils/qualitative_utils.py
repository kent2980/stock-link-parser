"""qualitative_infoデータの変換ユーティリティ"""

from typing import Dict, List, Any


def format_qualitative_info_hierarchical(qualitative_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """qualitative_infoを親子関係に基づいて階層構造に変換
    
    Args:
        qualitative_data: qualitative_infoのデータリスト
        
    Returns:
        階層構造化されたデータ [{title: str, content: List[str]}, ...]
    """
    if not qualitative_data:
        return []
    
    # currentIdをキーとした辞書を作成（高速検索用）
    items_by_id: Dict[str, Dict[str, Any]] = {}
    for item in qualitative_data:
        current_id = item.get("currentId")
        if current_id:
            items_by_id[current_id] = item
    
    def collect_children_content(parent_id: str) -> List[str]:
        """親IDに紐づくすべてのコンテンツを再帰的に収集"""
        contents = []
        
        # 直接の子要素を取得
        child_items = [
            item for item in qualitative_data 
            if item.get("parentId") == parent_id
        ]
        child_items.sort(key=lambda x: x.get("order", 0))
        
        for child_item in child_items:
            child_type = child_item.get("type", "")
            child_content = child_item.get("content", "")
            child_id = child_item.get("currentId")
            
            if child_type == "content":
                # contentタイプの場合はそのまま追加
                contents.append(child_content)
            elif child_type in ["sub_title", "heading"]:
                # sub_titleやheadingの場合は、そのコンテンツも含めて、さらに子要素を再帰的に収集
                contents.append(child_content)
                # 子要素を再帰的に収集
                contents.extend(collect_children_content(child_id))
            else:
                # その他のタイプも再帰的に収集
                contents.extend(collect_children_content(child_id))
        
        return contents
    
    # ルート要素（parentIdがNone、typeがtitle）を探す
    root_items = [
        item for item in qualitative_data 
        if item.get("parentId") is None and item.get("type") == "title"
    ]
    
    # orderでソート
    root_items.sort(key=lambda x: x.get("order", 0))
    
    result: List[Dict[str, Any]] = []
    
    for root_item in root_items:
        title = root_item.get("content", "")
        current_id = root_item.get("currentId")
        
        # 子要素のコンテンツを再帰的に収集
        content_list = collect_children_content(current_id)
        
        result.append({
            "title": title,
            "content": content_list if content_list else []
        })
    
    return result
