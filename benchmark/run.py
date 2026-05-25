"""
Benchmark 评测入口
加载场景 → 准备工作区 → headless 执行 agent → 转换 trace → 评分 → 输出报告
"""

import sys
import re
import json
import shutil
import inspect
import argparse
import threading
import importlib.util
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 让 import 能找到项目根目录和 benchmark 目录（harness 包）
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BENCHMARK_ROOT))

import yaml
import config
import llm
import tools
import prompts

BENCHMARK_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BENCHMARK_DIR / "scenarios"
CUSTOM_CHECKS_DIR = BENCHMARK_DIR / "custom_checks"
RESULTS_DIR = BENCHMARK_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

MAX_ITERATIONS = 20
TIMEOUT_SECONDS = 200


def load_scenarios(filter_id: str = None) -> list[dict]:
    scenarios = []
    for f in sorted(SCENARIOS_DIR.glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        if filter_id and data.get("id") != filter_id:
            continue
        scenarios.append(data)
    return scenarios


def seed_workspace(scenario: dict, workspace: Path):
    """将场景的 fixture 文件写入工作区"""
    for wf in scenario.get("workspace_files", []):
        p = workspace / wf["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(wf["content"], encoding="utf-8")

    seed_dir = scenario.get("workspace_seed_dir")
    if seed_dir:
        src = (SCENARIOS_DIR / scenario.get("_source_file", "")).parent / seed_dir
        if not src.exists():
            src = BENCHMARK_DIR / seed_dir.lstrip("./").lstrip("../").replace("../../", "")
        if not src.exists():
            src = BENCHMARK_DIR / "datasets" / "/".join(seed_dir.replace("../../datasets/", "").split("/"))
        if src.exists():
            for item in src.iterdir():
                dest = workspace / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                else:
                    shutil.copytree(item, dest)


def run_agent_headless(prompt: str, workspace: Path) -> list[dict]:
    """
    Headless 执行 agent：不做流式输出，直接收集 messages。
    使用线程本地存储设置工作区，支持并发执行。
    内置超时保护（300s），超时直接终止不重试。
    """
    import time
    from tools.safe_path import set_workdir
    start_time = time.time()

    set_workdir(workspace)

    messages = []
    messages.append({"role": "user", "content": prompt})
    tool_defs = tools.get_definitions()
    base_prompt = (
        f"你是一个精确高效的命令行助手。默认工作区：{workspace}\n"
        f"安全约束：所有文件操作和命令执行必须限制在工作区 {workspace} 内，"
        f"禁止访问工作区外的文件或执行危险命令（rm -rf /、sudo 等）。\n\n"
        f"执行原则：\n"
        f"1. 当任务要求创建文件时，必须使用 file_write 工具实际创建，不要只在回复中描述内容\n"
        f"2. 输出文件的字段名、结构、格式必须严格匹配任务要求，不要自行发挥\n"
        f"3. 保持简洁高效：分析文字控制在几句话内，把详细推理结论直接写入输出文件\n"
        f"4. 时间有限，读完必要输入后尽快创建输出文件，避免反复验证或多余的中间步骤"
    )
    system = prompts.build_system_prompt(base_prompt, tool_defs)

    for _ in range(MAX_ITERATIONS):
        if time.time() - start_time > TIMEOUT_SECONDS:
            messages.append({"role": "assistant", "content": "[超时终止]"})
            break

        try:
            remaining = max(10, TIMEOUT_SECONDS - int(time.time() - start_time))
            response = _llm_call_with_timeout(system, messages, remaining)
        except Exception:
            messages.append({"role": "assistant", "content": "[LLM 调用超时]"})
            break

        parsed_calls = _parse_tool_calls(response.content)

        if not parsed_calls:
            if _has_malformed_tool_call(response.content):
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": prompts.TOOL_CALL_RETRY_HINT})
                continue
            messages.append({"role": "assistant", "content": response.content})
            break

        messages.append({"role": "assistant", "content": response.content})
        for tc in parsed_calls:
            if time.time() - start_time > TIMEOUT_SECONDS:
                break
            args = tc.args
            args.pop("name", None)
            result = tools.dispatch(tc.name, **args)
            messages.append({
                "role": "user",
                "content": prompts.format_tool_result(tc.name, result),
            })

    return messages


def _llm_call_with_timeout(system: str, messages: list[dict], timeout: int) -> llm.LLMResponse:
    """单次 LLM 调用，不重试，使用指定 timeout"""
    import requests as req
    payload = {
        "model": config.MODEL,
        "messages": [{"role": "system", "content": system}] + messages,
        "max_tokens": config.MAX_TOKENS,
        "temperature": config.TEMPERATURE,
        "stream": True,
    }
    response = llm.LLMResponse()
    with req.post(
        f"{config.BASE_URL}/chat/completions",
        headers=config.HEADERS,
        json=payload,
        stream=True,
        timeout=timeout,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            if not chunk.get("choices"):
                continue
            delta = chunk["choices"][0].get("delta", {})
            if delta.get("content"):
                response.content += delta["content"]
    return response


def _parse_tool_calls(text: str) -> list[llm.ToolCall]:
    import uuid
    cleaned_text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)
    pattern = r"<(?:tool_call|glocall)>\s*(.*?)\s*</(?:tool_call|glocall|file_call|tool_result)>"
    matches = re.findall(pattern, cleaned_text, re.DOTALL)
    results = []
    for match in matches:
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

    cleaned = re.sub(r"</(?:arguments|name)>\s*$", "", stripped).strip()
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    # 策略3：XML 变体格式
    name_match = re.search(r"<(?:name|command|tool_name)>\s*(.*?)\s*</(?:name|command|tool_name)>", stripped)
    args_match = re.search(r"<(?:arguments|args)>\s*(.*?)\s*</(?:arguments|args)>", stripped, re.DOTALL)
    if name_match and args_match:
        name = name_match.group(1)
        args = {}
        try:
            args = json.loads(args_match.group(1).strip())
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

    # 策略4：工具名作为 XML 标签
    tool_names = ["bash", "file_read", "file_write", "file_edit", "file_patch", "glob"]
    tool_typos = {"globb": "glob", "globs": "glob", "globl": "glob", "glm": "glob",
                  "gloc": "glob", "globbing": "glob", "file_raed": "file_read",
                  "flie_read": "file_read"}
    all_tool_patterns = tool_names + list(tool_typos.keys())
    for tname in all_tool_patterns:
        real_name = tool_typos.get(tname, tname)
        pattern = rf"<{tname}>\s*(.*?)\s*</{tname}>"
        m = re.search(pattern, stripped, re.DOTALL)
        if m:
            inner = m.group(1).strip()
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
        # 未闭合标签
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

    # 策略5：自闭合 XML 属性格式 <file_read path="x.txt" /> 或 <bash command="ls" />
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
                # 尝试 <bash command="..."> 无引号属性
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
    if re.search(r"<(?:tool_call|gloss|glocall|globs|globbing|glm|gloc|globl|request|disabled)\b", text):
        return True
    malformed_patterns = [r"<tool_call\b", r"<name>\w+</name>\s*<arguments>", r"<tool_name>"]
    return any(re.search(p, text, re.DOTALL) for p in malformed_patterns)


def messages_to_trace(messages: list[dict]) -> dict:
    """将 messages 列表转换为 ClawProBench trace 格式"""
    events = []
    for msg in messages:
        if msg["role"] == "assistant":
            content = msg["content"]
            # 提取工具调用
            tc_pattern = r"<tool_call>\s*(.*?)\s*</tool_call>"
            tc_matches = re.findall(tc_pattern, content, re.DOTALL)
            for match in tc_matches:
                try:
                    data = json.loads(match)
                    tool_name = data["name"]
                    # 映射工具名到 ClawProBench 格式
                    mapped = _map_tool_name(tool_name)
                    events.append({
                        "type": "tool_call",
                        "tool": mapped,
                        "args": data.get("arguments", {}),
                    })
                except (json.JSONDecodeError, KeyError):
                    pass
            # 提取纯文本（去掉 tool_call 标签）
            plain = re.sub(r"<tool_call>.*?</tool_call>", "", content, flags=re.DOTALL).strip()
            if plain:
                events.append({"type": "assistant_message", "text": plain})

        elif msg["role"] == "user" and "<tool_result>" in msg.get("content", ""):
            content = msg["content"]
            name_match = re.search(r"<name>(.*?)</name>", content)
            output_match = re.search(r"<output>\n?(.*?)\n?</output>", content, re.DOTALL)
            if name_match:
                events.append({
                    "type": "tool_result",
                    "tool": _map_tool_name(name_match.group(1)),
                    "result": output_match.group(1) if output_match else "",
                })

    return {"events": events}


def _map_tool_name(name: str) -> str:
    """映射我们的工具名到 ClawProBench 的工具名"""
    mapping = {
        "file_read": "read",
        "file_write": "write",
        "bash": "exec",
        "file_edit": "edit",
        "file_patch": "patch",
        "glob": "glob",
        "memory_save": "memory_save",
    }
    return mapping.get(name, name)


def extract_tool_calls(trace: dict) -> list[dict]:
    """从 trace 中提取工具调用列表"""
    return [e for e in trace.get("events", []) if e.get("type") == "tool_call"]


def load_custom_check(scenario: dict):
    """动态加载评分脚本"""
    check_file = scenario.get("custom_check")
    if not check_file:
        return None
    path = CUSTOM_CHECKS_DIR / check_file
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("custom_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_grade(module, workspace: Path, trace: dict, tool_calls: list[dict]) -> dict:
    """调用评分函数，自动适配不同签名"""
    sig = inspect.signature(module.grade)
    params = list(sig.parameters.keys())
    if len(params) >= 3:
        return module.grade(str(workspace), trace, tool_calls)
    else:
        return module.grade(str(workspace), trace)


def compute_score(result: dict) -> float:
    """从 checkpoints 计算总分"""
    checkpoints = result.get("checkpoints", {})
    earned = sum(cp.get("score", 0) for cp in checkpoints.values())
    maximum = sum(cp.get("max", 0) for cp in checkpoints.values())
    return earned / maximum if maximum > 0 else 0.0


def run_scenario(scenario: dict, run_dir: Path, verbose: bool = False, print_lock: threading.Lock = None) -> dict:
    """运行单个场景，返回评测结果"""
    sid = scenario["id"]

    def _print(*args, **kwargs):
        if print_lock:
            with print_lock:
                print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    _print(f"\n{'='*60}")
    _print(f"  场景: {sid}")
    _print(f"  维度: {scenario.get('dimension', '?')} | 难度: {scenario.get('difficulty', '?')}")
    _print(f"{'='*60}")

    # 每个场景的文件夹放在本次评测的总目录下
    session_dir = run_dir / sid
    workspace = session_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        seed_workspace(scenario, workspace)
        _print(f"  工作区: {workspace}")
        _print(f"  Prompt: {scenario['prompt'][:80]}...")
        _print(f"  执行中...")

        messages = run_agent_headless(scenario["prompt"], workspace)
        trace = messages_to_trace(messages)
        tool_calls = extract_tool_calls(trace)

        _print(f"  完成，共 {len(messages)} 条消息，{len(tool_calls)} 次工具调用")

        # 保存 session 轨迹
        session_path = session_dir / "session.json"
        session_path.write_text(
            json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 评分
        check_module = load_custom_check(scenario)
        if not check_module:
            _print(f"  [跳过] 未找到评分脚本: {scenario.get('custom_check')}")
            return {"id": sid, "score": None, "detail": "no custom_check"}

        result = run_grade(check_module, workspace, trace, tool_calls)
        score = compute_score(result)
        passed = score >= scenario.get("pass_threshold", 0.7)

        _print(f"  得分: {score:.2%} {'PASS' if passed else 'FAIL'}")
        if verbose:
            for name, cp in result.get("checkpoints", {}).items():
                status = "✓" if cp["score"] == cp["max"] else "✗"
                _print(f"    {status} {name}: {cp['score']}/{cp['max']}")

        # 保存评分结果到 session 目录
        score_path = session_dir / "score.json"
        score_path.write_text(json.dumps({
            "id": sid, "score": score, "passed": passed,
            "checkpoints": result.get("checkpoints", {}),
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "id": sid,
            "score": score,
            "passed": passed,
            "threshold": scenario.get("pass_threshold", 0.7),
            "checkpoints": result.get("checkpoints", {}),
            "safety_violations": result.get("safety_violations", []),
            "messages_count": len(messages),
            "tool_calls_count": len(tool_calls),
            "session_dir": str(session_dir),
        }

    except Exception as e:
        _print(f"  [异常] {type(e).__name__}: {e}")
        return {
            "id": sid,
            "score": 0.0,
            "passed": False,
            "error": str(e),
            "session_dir": str(session_dir),
        }


def main():
    from datetime import datetime

    parser = argparse.ArgumentParser(description="liuchen-best-cli benchmark runner")
    parser.add_argument("--scenario", type=str, help="运行指定场景 ID")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细评分")
    parser.add_argument("--parallel", "-p", type=int, default=3, help="并发执行场景数（默认 3）")
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenario)
    if not scenarios:
        print(f"未找到场景" + (f" '{args.scenario}'" if args.scenario else ""))
        sys.exit(1)

    # 本次评测的总文件夹
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / f"run_{run_ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nliuchen-best-cli Benchmark")
    print(f"模型: {config.MODEL}")
    print(f"场景数: {len(scenarios)}")
    print(f"并发数: {args.parallel}")
    print(f"输出目录: {run_dir}")

    print_lock = threading.Lock()

    def run_and_collect(scenario):
        result = run_scenario(scenario, run_dir=run_dir, verbose=args.verbose, print_lock=print_lock)
        return result

    results = []
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = {executor.submit(run_and_collect, s): s for s in scenarios}
        for future in as_completed(futures):
            results.append(future.result())

    # 按场景原始顺序排序结果
    scenario_order = {s["id"]: i for i, s in enumerate(scenarios)}
    results.sort(key=lambda r: scenario_order.get(r["id"], 0))

    # 汇总
    scored = [r for r in results if r["score"] is not None]
    if scored:
        print(f"\n{'='*60}")
        print(f"  汇总")
        print(f"{'='*60}")
        avg = sum(r["score"] for r in scored) / len(scored)
        passed = sum(1 for r in scored if r.get("passed"))
        print(f"  平均得分: {avg:.2%}")
        print(f"  通过率: {passed}/{len(scored)}")
        print()
        for r in scored:
            mark = "✓" if r.get("passed") else "✗"
            print(f"  {mark} {r['id']}: {r['score']:.2%}")

    # 保存汇总结果
    summary = {
        "model": config.MODEL,
        "total_scenarios": len(scenarios),
        "scored_scenarios": len(scored) if scored else 0,
        "average_score": round(avg, 4) if scored else None,
        "pass_count": passed if scored else 0,
        "pass_rate": f"{passed}/{len(scored)}" if scored else "0/0",
        "scenarios": results,
    }
    out_path = run_dir / "summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  结果已保存: {out_path}")


if __name__ == "__main__":
    main()
