"""读取文件内容（带路径安全检查）"""

from tools.safe_path import safe_path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_read",
        "description": "读取指定文件的内容。支持指定起始行和行数限制。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径（相对或绝对路径）"},
                "offset": {"type": "integer", "description": "起始行号（从 1 开始），默认为 1"},
                "limit": {"type": "integer", "description": "读取的最大行数，默认为 200"},
            },
            "required": ["path"],
        },
    },
}


def handle(path: str, offset: int = 1, limit: int = 200) -> str:
    p = safe_path(path)
    if not p.exists():
        return f"错误：文件不存在 '{path}'"
    if not p.is_file():
        return f"错误：'{path}' 不是文件"

    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    total = len(lines)
    start = max(0, int(offset) - 1)
    end = start + int(limit)
    selected = lines[start:end]

    numbered = [f"{i + start + 1:4d} | {line}" for i, line in enumerate(selected)]
    header = f"[{p.name}] 共 {total} 行，显示第 {start + 1}-{min(end, total)} 行"
    return header + "\n" + "\n".join(numbered)
