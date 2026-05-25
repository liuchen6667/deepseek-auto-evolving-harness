#!/usr/bin/env python3
"""
liuchen-best-cli — 简洁优雅的命令行 Agent
一个极简但功能完整的 AI 编程助手，支持工具调用和流式输出。
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

import agent
import tools
from config import WORKSPACE
from session_logger import SessionLogger

console = Console()


def main():
    tool_names = " · ".join(d["function"]["name"] for d in tools.get_definitions())
    welcome = f"""
# liuchen-best-cli

一个简洁优雅的命令行 Agent。由 liuchen 制作。

**可用工具：** {tool_names}

**命令：** `/new` 新会话 · `/exit` 退出
"""
    console.print(Markdown(welcome))
    console.print(Panel(
        f"工作区: {WORKSPACE}",
        border_style="dim",
    ))

    messages: list[dict] = []
    logger = SessionLogger()

    while True:
        try:
            user_input = console.input("\n[bold green]❯[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n再见 👋")
            break

        if not user_input:
            continue
        if user_input.lower() == "/exit":
            console.print("再见 👋")
            break
        if user_input.lower() == "/new":
            messages.clear()
            logger = SessionLogger()
            console.print("[dim]── 新会话已开始 ──[/dim]")
            continue

        agent.run(user_input, messages)
        logger.log(messages)


if __name__ == "__main__":
    main()
