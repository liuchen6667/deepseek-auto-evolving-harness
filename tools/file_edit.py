"""编辑文件：字符串替换（带路径安全检查）"""

from tools.safe_path import safe_path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_edit",
        "description": "通过字符串替换来编辑文件。将 old_string 替换为 new_string。old_string 必须在文件中唯一匹配。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "old_string": {"type": "string", "description": "要被替换的原始文本（必须精确匹配）"},
                "new_string": {"type": "string", "description": "替换后的新文本"},
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
}


def handle(path: str, old_string: str, new_string: str) -> str:
    p = safe_path(path)
    if not p.exists():
        return f"错误：文件不存在 '{path}'"

    text = p.read_text(encoding="utf-8")
    count = text.count(old_string)

    if count == 0:
        return "错误：未找到匹配的文本"
    if count > 1:
        return f"错误：找到 {count} 处匹配，old_string 必须唯一"

    p.write_text(text.replace(old_string, new_string, 1), encoding="utf-8")
    return f"已编辑 {p}（替换了 1 处）"
