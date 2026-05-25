"""
按行编辑文件：支持删除指定行、插入新行、替换指定行范围。
比字符串替换更高效，模型只需描述差异而非重写整个文件。
"""

from tools.safe_path import safe_path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_patch",
        "description": "按行号编辑文件。支持三种操作：delete（删除行）、insert（在某行后插入）、replace（替换行范围）。可在一次调用中执行多个操作。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "operations": {
                    "type": "array",
                    "description": "编辑操作列表，按从后往前的顺序执行以保持行号稳定",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["delete", "insert", "replace"],
                                "description": "操作类型",
                            },
                            "start": {"type": "integer", "description": "起始行号（从 1 开始）"},
                            "end": {"type": "integer", "description": "结束行号（含），仅 delete 和 replace 需要"},
                            "content": {"type": "string", "description": "要插入或替换的内容（多行用换行分隔），仅 insert 和 replace 需要"},
                        },
                        "required": ["action", "start"],
                    },
                },
            },
            "required": ["path", "operations"],
        },
    },
}


def handle(path: str, operations: list[dict]) -> str:
    p = safe_path(path)
    if not p.exists():
        return f"错误：文件不存在 '{path}'"

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    # 确保最后一行有换行符
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    # 按 start 行号从大到小排序，从后往前操作以保持行号稳定
    ops = sorted(operations, key=lambda o: o.get("start", 0), reverse=True)
    changes = []

    for op in ops:
        action = op["action"]
        start = op["start"]
        end = op.get("end", start)
        content = op.get("content", "")

        # 行号转索引（1-based → 0-based）
        si = start - 1
        ei = end

        if si < 0 or ei > len(lines):
            return f"错误：行号超出范围（文件共 {len(lines)} 行，操作指定 {start}-{end}）"

        if action == "delete":
            del lines[si:ei]
            changes.append(f"删除第 {start}-{end} 行")

        elif action == "insert":
            new_lines = _to_lines(content)
            lines[si:si] = new_lines
            changes.append(f"在第 {start} 行后插入 {len(new_lines)} 行")

        elif action == "replace":
            new_lines = _to_lines(content)
            lines[si:ei] = new_lines
            changes.append(f"替换第 {start}-{end} 行为 {len(new_lines)} 行")

    p.write_text("".join(lines), encoding="utf-8")
    total = len(lines)
    summary = "；".join(reversed(changes))
    return f"已编辑 {p.name}（{summary}），当前共 {total} 行"


def _to_lines(content: str) -> list[str]:
    """将内容字符串转为带换行符的行列表"""
    if not content:
        return []
    result = content.splitlines(keepends=True)
    if result and not result[-1].endswith("\n"):
        result[-1] += "\n"
    return result
