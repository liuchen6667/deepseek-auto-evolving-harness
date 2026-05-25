"""
Agent 核心循环
调用 LLM → 解析 tool_calls → 执行工具 → 回传结果 → 循环
内置上下文压缩：自动压缩旧的工具结果，防止对话过长。
"""

import re
import json
import uuid
from rich.console import Console
from rich.panel import Panel
import llm
import tools
import prompts
from config import SYSTEM_PROMPT, MEMORY_DIR

console = Console()
MAX_ITERATIONS = 20
COMPACT_THRESHOLD = 30
KEEP_RECENT = 6
RESULT_DISPLAY_LIMIT = 500


def _load_memories() -> str:
    """加载 memory/ 目录下所有 md 文件，拼接为上下文"""
    files = sorted(MEMORY_DIR.glob("*.md"))
    if not files:
        return ""
    parts = []
    for f in files:
        parts.append(f.read_text(encoding="utf-8").strip())
    return "\n\n---\n\n".join(parts)  # 工具结果最多显示字符数


class _StreamFilter:
    """
    流式输出过滤器：拦截 <tool_call>...</tool_call> 标签内容，不显示给用户。
    只输出标签外的正常文本。
    """

    def __init__(self):
        self._buf = ""
        self._inside_tag = False

    def feed(self, text: str):
        for ch in text:
            self._buf += ch
            if not self._inside_tag:
                if self._buf.endswith("<tool_call>"):
                    # 进入标签，回删已输出的 "<tool_call>"
                    visible = self._buf[:-len("<tool_call>")]
                    if visible:
                        console.print(visible, end="", highlight=False)
                    self._buf = ""
                    self._inside_tag = True
                elif len(self._buf) > 20:
                    # 安全输出缓冲区前部（保留尾部以检测标签起始）
                    safe = self._buf[:-11]
                    console.print(safe, end="", highlight=False)
                    self._buf = self._buf[-11:]
            else:
                if self._buf.endswith("</tool_call>"):
                    self._buf = ""
                    self._inside_tag = False

    def flush(self):
        if not self._inside_tag and self._buf:
            console.print(self._buf, end="", highlight=False)
            self._buf = ""


def run(user_input: str, messages: list[dict]) -> str:
    """
    执行一轮完整的 agent 交互。
    messages 列表会被原地修改（追加本轮所有消息）。
    """
    messages.append({"role": "user", "content": user_input})
    tool_defs = tools.get_definitions()
    system = prompts.build_system_prompt(SYSTEM_PROMPT, tool_defs)

    # 注入长期记忆
    memories = _load_memories()
    if memories:
        system += f"\n\n# 长期记忆\n以下是你之前被要求记住的信息：\n\n{memories}"

    for _ in range(MAX_ITERATIONS):
        # 上下文压缩：将旧的工具结果替换为摘要
        _compact_if_needed(messages)

        console.print()
        streamer = _StreamFilter()
        response = llm.stream_chat(
            messages=[{"role": "system", "content": system}] + messages,
            on_delta=streamer.feed,
        )
        streamer.flush()

        # 解析工具调用
        parsed_calls = _parse_tool_calls(response.content)

        if not parsed_calls:
            # 检测是否有格式错误的工具调用意图
            if _has_malformed_tool_call(response.content):
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": prompts.TOOL_CALL_RETRY_HINT,
                })
                console.print("\n[dim]（工具调用格式有误，要求模型重试）[/dim]")
                continue

            if response.content:
                console.print()
            messages.append({"role": "assistant", "content": response.content})
            return response.content

        # 追加 assistant 消息，执行工具
        messages.append({"role": "assistant", "content": response.content})
        console.print()
        for tc in parsed_calls:
            result = _execute_tool(tc)
            messages.append({
                "role": "user",
                "content": prompts.format_tool_result(tc.name, result),
            })

    return "[达到最大迭代次数]"


# ─────────────────────────────────────────────
# 上下文压缩
# ─────────────────────────────────────────────

def _compact_if_needed(messages: list[dict]):
    """
    当消息过多时，将旧的工具结果压缩为占位符。
    保留最近 KEEP_RECENT 条消息不动，只压缩更早的。
    这是最廉价的上下文管理策略——不调用 LLM，只做文本替换。
    """
    if len(messages) <= COMPACT_THRESHOLD:
        return

    boundary = len(messages) - KEEP_RECENT
    for i in range(boundary):
        msg = messages[i]
        content = msg.get("content", "")
        # 压缩工具结果消息（包含 <tool_result> 标签且内容较长）
        if "<tool_result>" in content and len(content) > 200:
            # 提取工具名，保留摘要
            name_match = re.search(r"<name>(.*?)</name>", content)
            name = name_match.group(1) if name_match else "tool"
            messages[i] = {
                "role": msg["role"],
                "content": f"[已压缩: {name} 的执行结果，如需重新查看请再次调用工具]",
            }


# ─────────────────────────────────────────────
# 工具调用解析
# ─────────────────────────────────────────────

def _parse_tool_calls(text: str) -> list[llm.ToolCall]:
    """从模型输出文本中解析 <tool_call>...</tool_call> 标签，容忍常见变体格式"""
    # 先去掉 <thinking>...</thinking> 块，避免干扰解析
    cleaned_text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)
    # 匹配 <tool_call>...</tool_call> 及其变体闭合标签
    pattern = r"<(?:tool_call|glocall)>\s*(.*?)\s*</(?:tool_call|glocall|file_call|tool_result)>"
    matches = re.findall(pattern, cleaned_text, re.DOTALL)
    results = []
    for match in matches:
        # 处理嵌套标签：只去掉纯容器标签（tool_call/glocall/request）
        inner = re.sub(r"</?(?:tool_call|glocall|request|tool_result)>", "", match).strip()
        data = _try_parse_tool_json(inner)
        if data and "name" in data:
            results.append(llm.ToolCall(
                id=f"call_{uuid.uuid4().hex[:8]}",
                name=data["name"],
                arguments=json.dumps(data.get("arguments", {}), ensure_ascii=False),
            ))
    return results


def _try_parse_tool_json(raw: str) -> dict | None:
    """尝试多种策略解析工具调用内容"""
    # 预处理：去掉 CDATA 包裹
    stripped = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", raw, flags=re.DOTALL).strip()
    # 预处理：去掉容器标签变体（包括常见的不匹配闭合标签）
    stripped = re.sub(r"</?(?:gloss|gl|glm|gloc|globl|globbing|disabled|insert|loc|file_content)>", "", stripped).strip()

    # 策略1：直接 JSON 解析
    try:
        return json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        pass

    # 策略1.5：修复无效 JSON 转义序列后重试
    fixed = _fix_json_escapes(stripped)
    if fixed != stripped:
        try:
            return json.loads(fixed)
        except (json.JSONDecodeError, ValueError):
            pass

    # 策略2：去掉尾部多余的 </arguments> 等标签后再解析
    cleaned = re.sub(r"</(?:arguments|name)>\s*$", "", stripped).strip()
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    # 策略3：XML 变体格式 <name>xxx</name><arguments>{...}</arguments>
    name_match = re.search(r"<(?:name|command|tool_name)>\s*(.*?)\s*</(?:name|command|tool_name)>", stripped)
    args_match = re.search(r"<(?:arguments|args)>\s*(.*?)\s*</(?:arguments|args)>", stripped, re.DOTALL)
    if name_match and args_match:
        name = name_match.group(1)
        args = {}
        try:
            args_content = args_match.group(1).strip()
            args = json.loads(args_content)
        except (json.JSONDecodeError, ValueError):
            fixed_args = _fix_json_escapes(args_match.group(1).strip())
            try:
                args = json.loads(fixed_args)
            except (json.JSONDecodeError, ValueError):
                for pm in re.finditer(r"<(\w+)>(.*?)</\1>", args_match.group(1), re.DOTALL):
                    args[pm.group(1)] = pm.group(2)
        if "name" in args and "arguments" in args:
            return args
        return {"name": name, "arguments": args}
    if args_match and not name_match:
        try:
            data = json.loads(args_match.group(1).strip())
            if "name" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass

    # 策略3.5：<command>...</command> 单独出现（无 <arguments>），视为 bash 命令
    if not args_match:
        cmd_match = re.search(r"<command>\s*(.*?)\s*</command>", stripped, re.DOTALL)
        if cmd_match:
            return {"name": "bash", "arguments": {"command": cmd_match.group(1)}}

    # 策略4：工具名作为 XML 标签 <bash><command>ls</command></bash>
    tool_names = ["bash", "file_read", "file_write", "file_edit", "file_patch", "glob"]
    tool_typos = {"globb": "glob", "globs": "glob", "globl": "glob", "glm": "glob",
                  "gloc": "glob", "globbing": "glob", "file_raed": "file_read",
                  "flie_read": "file_read"}
    all_tool_patterns = tool_names + list(tool_typos.keys())
    for tname in all_tool_patterns:
        real_name = tool_typos.get(tname, tname)
        # 匹配闭合标签
        pattern = rf"<{tname}>\s*(.*?)\s*</{tname}>"
        m = re.search(pattern, stripped, re.DOTALL)
        if m:
            inner = m.group(1).strip()
            # 去掉嵌套的重复标签
            inner = re.sub(rf"</?{tname}>", "", inner).strip()
            args = {}
            try:
                args = json.loads(inner)
            except (json.JSONDecodeError, ValueError):
                fixed_inner = _fix_json_escapes(inner)
                try:
                    args = json.loads(fixed_inner)
                except (json.JSONDecodeError, ValueError):
                    am = re.search(r"<(?:arguments|args)>\s*(.*?)\s*</(?:arguments|args)>", inner, re.DOTALL)
                    if am:
                        try:
                            args = json.loads(am.group(1))
                        except (json.JSONDecodeError, ValueError):
                            pass
                    if not args:
                        for pm in re.finditer(r"<(\w+)>(.*?)</\1>", inner, re.DOTALL):
                            args[pm.group(1)] = pm.group(2)
            if args:
                return {"name": real_name, "arguments": args}
        # 匹配未闭合标签 <bash>{...} (没有 </bash>)
        pattern_open = rf"<{tname}>\s*(.*)"
        m2 = re.search(pattern_open, stripped, re.DOTALL)
        if m2 and f"</{tname}>" not in stripped:
            inner = m2.group(1).strip()
            try:
                args = json.loads(inner)
                return {"name": real_name, "arguments": args}
            except (json.JSONDecodeError, ValueError):
                fixed_inner = _fix_json_escapes(inner)
                try:
                    return {"name": real_name, "arguments": json.loads(fixed_inner)}
                except (json.JSONDecodeError, ValueError):
                    am = re.search(r"<(?:arguments|args)>\s*(.*?)\s*</(?:arguments|args)>", inner, re.DOTALL)
                    if am:
                        try:
                            return {"name": real_name, "arguments": json.loads(am.group(1))}
                        except (json.JSONDecodeError, ValueError):
                            pass

    # 策略5：自闭合 XML 属性格式 <file_read path="x.txt" />
    self_close = re.search(r"<(\w+)\s+(.*?)\s*/?>", stripped, re.DOTALL)
    if self_close:
        tag_name = self_close.group(1)
        attrs_str = self_close.group(2)
        real_name = tool_typos.get(tag_name, tag_name)
        if real_name in tool_names:
            args = {}
            for am in re.finditer(r'(\w+)=["\']([^"\']*)["\']', attrs_str):
                args[am.group(1)] = am.group(2)
            if not args:
                eq_match = re.search(r'(\w+)=(.+)', attrs_str)
                if eq_match:
                    args[eq_match.group(1)] = eq_match.group(2).strip().rstrip('/')
            if args:
                return {"name": real_name, "arguments": args}

    return None


def _fix_json_escapes(s: str) -> str:
    """修复 JSON 中无效的转义序列（模型常见错误）"""
    valid_escapes = set('"\\/bfnrtu')
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            next_ch = s[i + 1]
            if next_ch in valid_escapes:
                result.append(s[i])
                result.append(next_ch)
                i += 2
            else:
                result.append('\\\\')
                result.append(next_ch)
                i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def _has_malformed_tool_call(text: str) -> bool:
    """检测文本中是否有格式错误的工具调用意图（有标签但解析失败）"""
    if re.search(r"<(?:tool_call|gloss|glocall|globs|globbing|glm|gloc|globl|request|disabled)\b", text):
        return True
    malformed_patterns = [
        r"<tool_call\b",
        r"<name>\w+</name>\s*<arguments>",
        r"<tool_name>",
    ]
    return any(re.search(p, text, re.DOTALL) for p in malformed_patterns)


# ─────────────────────────────────────────────
# 工具执行
# ─────────────────────────────────────────────

def _execute_tool(tc: llm.ToolCall) -> str:
    """执行单个工具调用，展示执行状态"""
    args = tc.args
    args.pop("name", None)
    # 简洁显示：工具名 + 关键参数
    brief_args = _brief_args(tc.name, args)
    console.print(f"  [cyan]▶ {tc.name}[/cyan] [dim]{brief_args}[/dim]")

    result = tools.dispatch(tc.name, **args)

    # 结果裁剪显示
    lines = result.splitlines()
    if len(result) > RESULT_DISPLAY_LIMIT or len(lines) > 10:
        preview = "\n".join(lines[:8])
        if len(preview) > RESULT_DISPLAY_LIMIT:
            preview = preview[:RESULT_DISPLAY_LIMIT]
        console.print(Panel(
            preview + f"\n[dim]... ({len(lines)} 行, {len(result)} 字符)[/dim]",
            title="📋 结果",
            border_style="green",
        ))
    else:
        console.print(Panel(result, title="📋 结果", border_style="green"))
    return result


def _brief_args(name: str, args: dict) -> str:
    """为工具调用生成参数摘要"""
    if name == "bash":
        return args.get("command", "")
    if name == "file_read":
        return args.get("path", "")
    if name == "file_write":
        path = args.get("path", "")
        size = len(args.get("content", ""))
        return f"{path} ({size} 字符)"
    if name == "file_edit":
        return args.get("path", "")
    if name == "glob":
        return args.get("pattern", "")
    return json.dumps(args, ensure_ascii=False)
