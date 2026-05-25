"""
会话日志
每次对话自动保存到 sessions/ 目录，记录完整的消息历史和工具调用。
文件名格式：YYYY-MM-DD_HH-MM-SS.json
"""

import json
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path(__file__).parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


class SessionLogger:
    """管理单次会话的日志记录"""

    def __init__(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.path = SESSIONS_DIR / f"{ts}.json"
        self.data = {
            "start_time": ts,
            "messages": [],
        }

    def log(self, messages: list[dict]):
        """保存当前完整消息历史（每轮交互后调用）"""
        self.data["messages"] = messages
        self.data["end_time"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
