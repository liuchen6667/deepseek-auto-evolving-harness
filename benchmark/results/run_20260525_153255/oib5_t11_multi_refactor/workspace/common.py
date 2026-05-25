"""公共工具函数"""

import json
from pathlib import Path


def load_json(filename):
    """从JSON文件加载数据"""
    path = Path(filename)
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data


def save_json(data, filename):
    """保存数据到JSON文件"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def find_by_id(items, item_id):
    """在列表中根据ID查找项目"""
    for item in items:
        if item["id"] == item_id:
            return item
    return None