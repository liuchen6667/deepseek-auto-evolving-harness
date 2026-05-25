# Self-Evolution 指南：基于 Benchmark 的 Agent 自我进化

## 核心理念

通过「检查结果 → 诊断问题 → 改造框架 → 全量验证」的闭环，让 agent 持续进化。每一轮进化都有据可查、有数据支撑，避免盲目修改。

## 进化流程

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   ① 检查 benchmark/results 中已有的结果             │
│        │                                            │
│        ├─ 有结果 → 分析失败任务的问题               │
│        └─ 无结果 → 先运行 benchmark/run.py          │
│        ↓                                            │
│   ② 诊断问题：哪些任务失败了？失败原因是什么？       │
│        ↓                                            │
│   ③ 对框架进行针对性改造                            │
│        ↓                                            │
│   ④ 运行 benchmark/run.py（全量评测）               │
│        │                                            │
│        ├─ 分数提升 → 本轮结束                       │
│        └─ 分数未提升 → 总结经验，回到 ③ 再改造      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 第一步：检查已有结果

查看 `benchmark/results/` 目录下是否有已经跑完的结果文件夹：

```bash
ls benchmark/results/
```

- **有结果**：直接进入第二步，分析已有结果中的问题
- **无结果**：先运行一次全量评测，生成基线数据

```bash
python benchmark/run.py
```

## 第二步：诊断问题

每次评测结果保存在 `benchmark/results/run_<时间戳>/` 下。逐个检查失败的场景：

```
benchmark/results/run_20260524_134052/
└── constraints_05_release_gate_live/
    ├── workspace/          ← agent 产出了什么文件？缺了什么？
    ├── session.json        ← 完整对话轨迹，逐条分析
    └── score.json          ← 哪些 checkpoint 失败了？
```

### 诊断清单

打开 `score.json`，找到 score=0 的 checkpoint，然后对照 `session.json` 回答：

| 问题 | 在哪里看 |
|------|----------|
| agent 是否理解了任务？ | session.json 第一条 assistant 消息 |
| agent 是否调用了正确的工具？ | session.json 中的 tool_call 标签 |
| 工具调用的参数对吗？ | tool_call 的 arguments 字段 |
| 工具返回了什么？ | tool_result 消息 |
| agent 是否正确处理了工具结果？ | 后续 assistant 消息 |
| 最终产出文件内容对吗？ | workspace/ 目录下的文件 |
| 是否超时终止了？ | session.json 最后一条是否为 `[超时终止]` |
| 执行链路是否过长？ | session.json 的消息条数 |

## 第三步：归类问题根因并改造框架

常见问题类型及对应改造方向：

### A. 工具调用失败

**症状**：agent 想做某件事但没有合适的工具，或工具参数不匹配。

**改造方向**：
- 在 `tools/` 下新增工具
- 修改现有工具的参数定义（SCHEMA）
- 增强工具的错误提示信息

### B. 执行链路过长 / 超时

**症状**：消息数 > 30，或以 `[超时终止]` 结束。

**改造方向**：
- 优化 system prompt，让模型一次性完成更多操作
- 在 `prompts.py` 的 `TOOL_USE_INSTRUCTION` 中加入效率指导
- 允许单次调用多个工具（如果模型支持）
- 调整 `MAX_ITERATIONS` 或 `TIMEOUT_SECONDS`

### C. 对任务理解错误

**症状**：agent 做了不相关的事情，或遗漏了关键约束。

**改造方向**：
- 优化 system prompt 中的角色定义
- 在 `config.py` 的 `SYSTEM_PROMPT` 中加入更明确的行为指导
- 考虑是否需要 few-shot 示例

### D. 格式/输出不符合要求

**症状**：agent 完成了任务但输出格式不对（JSON 格式错误、缺少字段等）。

**改造方向**：
- 在 system prompt 中加入格式遵循的指导
- 增加输出验证工具（让 agent 自检）
- 在 `prompts.py` 中加入格式示例

### E. 安全边界问题

**症状**：agent 泄露了敏感信息或执行了危险操作。

**改造方向**：
- 在 system prompt 中加入安全规则
- 在工具层面加入过滤（如 bash 工具拒绝危险命令）
- 在 `tools/file_read.py` 中加入敏感文件检测

### F. 工具结果处理错误

**症状**：工具返回了正确结果但 agent 解析/使用错误。

**改造方向**：
- 优化工具返回的格式，使其更易被模型理解
- 在 `prompts.py` 的 `TOOL_RESULT_TEMPLATE` 中加入更多结构化信息
- 调整工具输出的详细程度

### 改造原则

- **一次只改一个方向**，否则无法归因进步来自哪里
- **改造应该是通用的提升**，不要为了通过某一题而过度特化
- **保持简洁**，如无必要勿增实体

## 第四步：全量验证

改造完成后，直接运行全量评测：

```bash
python benchmark/run.py
```

**注意：一次全量评测大约需要 1 小时。**

对比本次结果与 `benchmark/results/` 中最新的评测结果（结果文件夹以时间戳命名，如 `run_20260524_134052`，取时间最新的那个作为参照基线）：

- **分数提升（相对最新结果）** → 本轮进化成功，停止
- **分数未提升或下降** → 总结经验教训，回到第三步重新改造

### 未提升时的处理

1. 分析为什么改造没有效果（是改错了方向？还是改得不够？）
2. 总结经验，调整改造策略
3. 重新改造框架
4. 再次运行 `python benchmark/run.py` 验证

重复此过程直到分数提升为止。

## 记录进化日志

在 `benchmark/evolution_log.md` 中记录每次进化：

```markdown
## 进化 #1 — 2026-05-24

### 问题
constraints_05_release_gate_live 得分 0%，agent 没有创建 release_decision.json。

### 诊断
查看 session.json 发现 agent 读取了所有文件，做了分析，但最终只用文字回复了结论，
没有调用 file_write 工具创建输出文件。

### 根因
System prompt 中没有强调「必须通过工具产出文件，而不是口头回答」。

### 改造
在 config.py 的 SYSTEM_PROMPT 中加入：
「当任务要求创建文件时，必须使用 file_write 工具实际创建，不要只在回复中描述内容。」

### 结果
- 全量评测总分：45% → 52%
- constraints_05: 0% → 66%
- 无回归

### 下一步
继续优化 constraints 维度，关注输出格式准确性。
```

## 可改造的文件清单

| 文件 | 改什么 | 影响范围 |
|------|--------|----------|
| `config.py` → SYSTEM_PROMPT | 角色定义、行为准则 | 全局 |
| `prompts.py` → TOOL_USE_INSTRUCTION | 工具调用方式指导 | 工具调用行为 |
| `prompts.py` → TOOL_RESULT_TEMPLATE | 结果回传格式 | 模型对结果的理解 |
| `tools/*.py` → SCHEMA | 工具描述和参数说明 | 模型选择工具的准确性 |
| `tools/*.py` → handle() | 工具执行逻辑 | 工具能力边界 |
| `tools/` → 新文件 | 新增工具 | 能力扩展 |
| `agent.py` → MAX_ITERATIONS | 最大迭代次数 | 复杂任务完成度 |
| `agent.py` → _compact_if_needed() | 上下文压缩策略 | 长对话质量 |
| `agent.py` → _has_malformed_tool_call() | 格式纠错检测 | 容错能力 |
| `llm.py` → MAX_TOKENS | 单次生成长度 | 复杂输出完整性 |

## 注意事项

1. **绝对不要作弊** — 不要修改评测题目、评分脚本、测试用例或预期答案。进化的目标是让框架本身变强，而不是让评测变简单。任何绕过评测逻辑、硬编码特定答案、针对评测数据做特殊处理的行为都是作弊，即使分数提升了也毫无意义。唯一正确的方式是改进 agent 框架的通用能力。
2. **关注通过率趋势而非单题得分** — 个别题目可能对特定模型天然困难
3. **保留历史评测结果** — `results/` 下的每次 run 都是进化的证据
4. **进化是渐进的** — 不要期望一次改造解决所有问题，每次提升 5-10% 就是好的迭代
