"""公共工具函数"""

import json
from pathlib import Path


def load_json(filename):
    """从JSON文件加载数据
    
    Args:
        filename: JSON文件名
        
    Returns:
        list: 加载的数据，如果文件不存在则返回空列表
    """
    path = Path(filename)
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data


def save_json(data, filename):
    """将数据保存到JSON文件
    
    Args:
        data: 要保存的数据
        filename: JSON文件名
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def find_by_id(items, item_id, id_key="id"):
    """根据ID在列表中查找项目
    
    Args:
        items: 项目列表
        item_id: 要查找的ID
        id_key: ID字段名，默认为"id"
        
    Returns:
        dict|None: 找到的项目，未找到则返回None
    """
    for item in items:
        if item.get(id_key) == item_id:
            return item
    return None
