import json
from pathlib import Path


def load_json(filename):
    """从JSON文件加载数据，文件不存在时返回空列表"""
    path = Path(filename)
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data


def save_json(data, filename):
    """将数据保存到JSON文件"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def find_by_id(items, item_id):
    """在列表中按ID查找项"""
    for item in items:
        if item["id"] == item_id:
            return item
    return None
