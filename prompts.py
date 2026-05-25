"""
工具调用提示词模板
当模型不支持原生 function calling 时，通过 prompt 注入让任意模型具备工具调用能力。
修改此文件可自定义工具调用的行为和格式。
"""

import json

# ─────────────────────────────────────────────
# 工具调用格式说明（注入到 system prompt 中）
# 模型需要按此格式输出工具调用，agent 会解析并执行
# ─────────────────────────────────────────────
TOOL_USE_INSTRUCTION = """
# 工具使用

你可以通过工具来完成用户的请求。当你需要使用工具时，请用以下 XML 格式输出：

<tool_call>
{"name": "工具名称", "arguments": {"参数名": "参数值"}}
</tool_call>

规则：
1. 每次可以调用一个或多个工具，每个工具调用用单独的 <tool_call> 标签包裹
2. arguments 必须是合法的 JSON 对象
3. 调用工具时不要输出其他多余内容，直接输出 <tool_call> 标签
4. 工具执行结果会在下一轮消息中以 <tool_result> 标签返回给你
5. 收到工具结果后，继续根据结果回答用户，或继续调用工具
6. 当任务完成时，直接用自然语言回复用户，不要输出 <tool_call> 标签
""".strip()

# ─────────────────────────────────────────────
# 工具结果回传格式（作为 user 消息发送给模型）
# ─────────────────────────────────────────────
TOOL_RESULT_TEMPLATE = """<tool_result>
<name>{name}</name>
<output>
{output}
</output>
</tool_result>"""

# ─────────────────────────────────────────────
# 工具调用格式纠错提示
# 当模型输出了格式错误的工具调用时，发送此消息要求重试
# ─────────────────────────────────────────────
TOOL_CALL_RETRY_HINT = """你的工具调用格式有误。请严格使用以下格式，标签内必须是合法的 JSON：

<tool_call>
{"name": "工具名", "arguments": {"参数名": "参数值"}}
</tool_call>

请重新输出你的工具调用。"""


def format_tool_definitions(tool_defs: list[dict]) -> str:
    """
    将工具定义列表格式化为可读的文本描述。
    输入格式为 OpenAI function calling schema。
    """
    lines = ["## 可用工具\n"]
    for tool in tool_defs:
        func = tool["function"]
        name = func["name"]
        desc = func["description"]
        params = func.get("parameters", {}).get("properties", {})
        required = func.get("parameters", {}).get("required", [])

        lines.append(f"### {name}")
        lines.append(f"{desc}\n")
        if params:
            lines.append("参数：")
            for pname, pinfo in params.items():
                req_mark = "（必填）" if pname in required else "（可选）"
                pdesc = pinfo.get("description", "")
                ptype = pinfo.get("type", "string")
                lines.append(f"- `{pname}` ({ptype}): {pdesc} {req_mark}")
            lines.append("")

    return "\n".join(lines)


def build_system_prompt(base_prompt: str, tool_defs: list[dict]) -> str:
    """
    构建完整的 system prompt：基础 prompt + 工具定义 + 调用格式说明。
    这是 prompt 模式的核心——通过提示词让任意模型学会调用工具。
    """
    tool_docs = format_tool_definitions(tool_defs)
    return f"{base_prompt}\n\n{tool_docs}\n{TOOL_USE_INSTRUCTION}"


def format_tool_result(name: str, output: str) -> str:
    """格式化工具执行结果，用于回传给模型"""
    return TOOL_RESULT_TEMPLATE.format(name=name, output=output)
