"""
工具注册表
自动扫描当前目录下的工具模块，每个模块需导出 SCHEMA 和 handle 函数。
"""

import importlib
from pathlib import Path

# 工具注册表：{name: handle_function}
_handlers: dict[str, callable] = {}
# 工具定义列表（OpenAI function calling 格式）
_definitions: list[dict] = []


def _discover():
    """扫描 tools/ 目录，自动导入所有工具模块"""
    tools_dir = Path(__file__).parent
    for path in sorted(tools_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        module = importlib.import_module(f"tools.{path.stem}")
        schema = getattr(module, "SCHEMA", None)
        handler = getattr(module, "handle", None)
        if schema and handler:
            name = schema["function"]["name"]
            _handlers[name] = handler
            _definitions.append(schema)


def get_definitions() -> list[dict]:
    """返回所有工具的 OpenAI function 格式定义"""
    return _definitions


def dispatch(name: str, **kwargs) -> str:
    """执行指定工具，返回结果字符串"""
    handler = _handlers.get(name)
    if not handler:
        return f"错误：未知工具 '{name}'"
    try:
        return handler(**kwargs)
    except Exception as e:
        return f"工具执行出错：{e}"


# 模块加载时自动发现工具
_discover()
