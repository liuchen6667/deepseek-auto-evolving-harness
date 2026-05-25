"""记忆工具：将用户要求记住的信息持久化为 md 文件。"""

from datetime import datetime
from config import MEMORY_DIR

SCHEMA = {
    "type": "function",
    "function": {
        "name": "memory_save",
        "description": "将一条信息保存到长期记忆中。当用户要求记住某些信息时使用此工具。",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "记忆标题，简短"},
                "content": {"type": "string", "description": "要记住的完整内容"},
            },
            "required": ["title", "content"],
        },
    },
}


def handle(title: str, content: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:40]
    filename = f"{ts}_{safe_title}.md"
    path = MEMORY_DIR / filename

    text = f"# {title}\n\n{content}\n"
    path.write_text(text, encoding="utf-8")
    return f"已记住：{title}"
