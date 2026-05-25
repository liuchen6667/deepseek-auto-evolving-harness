"""文件搜索：按 glob 模式匹配文件路径"""

from tools.safe_path import get_workdir

SCHEMA = {
    "type": "function",
    "function": {
        "name": "glob",
        "description": "按 glob 模式搜索文件。返回匹配的文件路径列表。例如 '**/*.py' 搜索所有 Python 文件。",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "glob 模式，如 '*.py'、'src/**/*.ts'、'**/*.md'"},
            },
            "required": ["pattern"],
        },
    },
}

MAX_RESULTS = 100


def handle(pattern: str) -> str:
    workdir = get_workdir()
    matches = sorted(workdir.glob(pattern))
    matches = [
        m for m in matches
        if not any(part.startswith(".") for part in m.relative_to(workdir).parts)
        and "node_modules" not in m.parts
        and "__pycache__" not in m.parts
    ]

    if not matches:
        return f"未找到匹配 '{pattern}' 的文件"

    total = len(matches)
    display = matches[:MAX_RESULTS]
    lines = [str(m.relative_to(workdir)) for m in display]

    result = "\n".join(lines)
    if total > MAX_RESULTS:
        result += f"\n... 共 {total} 个文件，仅显示前 {MAX_RESULTS} 个"
    return result
