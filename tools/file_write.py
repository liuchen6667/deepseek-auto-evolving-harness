"""写入文件（带路径安全检查）"""

from tools.safe_path import safe_path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_write",
        "description": "将内容写入指定文件。如果文件不存在则创建，存在则覆盖。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "要写入的完整内容"},
            },
            "required": ["path", "content"],
        },
    },
}


def handle(path: str, content: str) -> str:
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    lines = content.count("\n") + 1
    return f"已写入 {p} ({lines} 行, {len(content)} 字节)"
