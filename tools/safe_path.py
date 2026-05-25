"""
路径解析工具。
相对路径以 workspace 为基准，绝对路径直接使用。
支持多线程：每个线程可通过 set_workdir() 设置独立工作区。
"""

import threading
from pathlib import Path
from config import WORKSPACE

WORKDIR = WORKSPACE.resolve()

_thread_local = threading.local()


def set_workdir(path: Path):
    """设置当前线程的工作区路径"""
    _thread_local.workdir = path.resolve()


def get_workdir() -> Path:
    """获取当前线程的工作区路径，未设置则返回全局 WORKDIR"""
    return getattr(_thread_local, "workdir", WORKDIR)


def safe_path(p: str) -> Path:
    """
    解析路径：相对路径基于 workspace，绝对路径直接使用。
    """
    path = Path(p).expanduser()
    if not path.is_absolute():
        path = get_workdir() / path
    return path.resolve()
