"""通用工具函数"""

import json
from pathlib import Path


def load_json(filename):
    """从 JSON 文件加载数据，如果文件不存在返回空列表"""
    path = Path(filename)
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data


def save_json(data, filename):
    """将数据保存到 JSON 文件"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def find_by_id(items, item_id):
    """在列表中根据 ID 查找对象"""
    for item in items:
        if item["id"] == item_id:
            return item
    return None
