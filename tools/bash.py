"""执行 Shell 命令"""

import subprocess
from tools.safe_path import get_workdir

SCHEMA = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "在工作区目录中执行 shell 命令，返回 stdout 和 stderr。适用于运行程序、查看目录、安装依赖等操作。命令的工作目录为当前工作区。",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 shell 命令",
                }
            },
            "required": ["command"],
        },
    },
}


def handle(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(get_workdir()),
    )
    output = ""
    if result.stdout:
        output += result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    if result.returncode != 0:
        output += f"\n[exit code: {result.returncode}]"
    return output.strip() or "(无输出)"
