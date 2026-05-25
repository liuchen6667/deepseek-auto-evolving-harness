#!/usr/bin/env python3

import os
import subprocess

TOOLS = [{
    "name": "bash",
    "description": "运行shell命令",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    },
}]


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "错误：危险命令已被阻止"
    
    try:
        result = subprocess.run(command, shell=True, cwd=os.getcwd(),
                               capture_output=True, text=True, timeout=120)
        output = (result.stdout + result.stderr).strip()
        return output[:50000] if output else "(无输出)"
    except subprocess.TimeoutExpired:
        return "错误：超时(120秒)"
    except (FileNotFoundError, OSError) as e:
        return f"错误：{e}"


class SimpleAgent:
    def __init__(self, system_prompt=None):
        self.system_prompt = system_prompt or f"你是一个编码助手，当前目录：{os.getcwd()}。使用bash解决问题。直接行动，不要解释。"
        
    def simulate_llm_call(self, messages, tools):
        last_message = messages[-1]["content"] if messages else ""
        
        if "ls" in last_message.lower():
            return {
                "stop_reason": "tool_use",
                "content": [{
                    "type": "tool_use",
                    "id": "tool_001",
                    "name": "bash",
                    "input": {"command": "ls -la"}
                }]
            }
        elif "pwd" in last_message.lower():
            return {
                "stop_reason": "tool_use",
                "content": [{
                    "type": "tool_use",
                    "id": "tool_002",
                    "name": "bash",
                    "input": {"command": "pwd"}
                }]
            }
        else:
            return {
                "stop_reason": "end_turn",
                "content": [{
                    "type": "text",
                    "text": "这是一个模拟的文本响应。在实际应用中，这里会调用真正的LLM API。"
                }]
            }
    
    def agent_loop(self, messages):
        
        while True:
            response = self.simulate_llm_call(messages, TOOLS)
            
            messages.append({"role": "assistant", "content": response["content"]})
            
            if response["stop_reason"] != "tool_use":
                return
            
            results = []
            for block in response["content"]:
                if block.get("type") == "tool_use":
                    tool_name = block.get("name")
                    tool_id = block.get("id")
                    tool_input = block.get("input", {})
                    
                    
                    if tool_name == "bash":
                        output = run_bash(tool_input.get("command", ""))
                        results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": output,
                        })
            
            if results:
                messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    
    agent = SimpleAgent()
    
    test_messages = []
    
    test_messages.append({"role": "user", "content": "请列出当前目录的内容"})
    agent.agent_loop(test_messages)
    
    test_messages.append({"role": "user", "content": "我在哪个目录下？"})
    agent.agent_loop(test_messages)
    
    test_messages.append({"role": "user", "content": "你好，请介绍一下自己"})
    agent.agent_loop(test_messages)
    

def real_agent_loop(messages):
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet",
            system=system_prompt,
            messages=messages,
            tools=TOOLS,
            max_tokens=8000,
        )
        
        messages.append({"role": "assistant", "content": response.content})
        
        if response.stop_reason != "tool_use":
            return
        
""")
