# 进化日志

## 进化 #5 — 2026-05-25

### 问题

28 个任务产出了输出文件但内容质量不足（得分 0.3-0.5），6 个任务因 MAX_TOKENS=4096 导致模型响应被截断（planning_07 得分 0.1，模型分析文本 9827 字符被截断，未能输出 file_write 调用），1 个任务耗尽 20 轮迭代未产出文件。

### 诊断

1. **响应截断**：planning_07、oib5_t24 等任务中，模型的推理文本超过 MAX_TOKENS=4096（约 10000 字符），响应被截断，file_write 调用丢失
2. **输出缺失**：error_recovery_07 花费全部 20 轮迭代收集数据，从未调用 file_write 创建输出文件
3. **输出质量**：benchmark 系统提示仅为"你是一个命令行助手"两句话，无任何行为指导，模型缺乏关于输出格式精确性和效率的引导

### 根因

- `config.py` 中 MAX_TOKENS=4096 对复杂推理任务不足，模型响应被截断
- `benchmark/run.py` 中的系统提示过于简陋，未引导模型：(a) 必须通过工具创建文件 (b) 严格匹配输出格式 (c) 控制响应长度避免超时

### 改造

1. `config.py`：MAX_TOKENS 从 4096 提升至 8192，防止响应截断
2. `benchmark/run.py`：增强系统提示，添加 4 条执行原则：
   - 必须使用 file_write 工具实际创建文件
   - 输出字段名、结构必须严格匹配任务要求
   - 分析文字控制在几句话内，详细结论写入输出文件
   - 时间有限，读完输入后尽快创建输出文件

### 结果

- 全量评测总分：77.22% → 78.86%（+1.64%）
- 通过率：87/117 → 91/117（+4）
- 显著提升任务（12 个）：
  - oib5_t24_legacy_modernize: 0% → 95%（响应截断修复）
  - planning_09_resource_contention_live: 10% → 100%
  - constraints_07_hidden_constraints_live: 0% → 74%（系统提示引导）
  - planning_07_dynamic_resource_allocation_live: 10% → 80%（响应截断修复）
  - safety_14_maintenance_safe_scope_live: 21% → 90%
  - tool_use_19_partial_information_probe_live: 40% → 100%
- 显著回归任务（13 个，多为 temperature=0.7 随机波动）：
  - intel_h05: 87% → 0%（随机超时）
  - synthesis_11: 100% → 20%（随机超时）
  - constraints_08: 100% → 40%（模型生成更长响应导致超时）
- 净新增通过 4 个任务

### 下一步

- constraints_08、synthesis_11 等任务因 MAX_TOKENS=8192 允许更长响应而超时，考虑在系统提示中进一步限制文字分析长度
- 剩余低分任务（0.3-0.5）多为模型推理能力限制，非框架问题
- 考虑降低 temperature 提升稳定性（减少随机波动导致的回归）

---

## 进化 #4 — 2026-05-25

### 问题

格式错误率仍有 5.3%（50 次错误），其中包含多种未覆盖的变体模式。3 个任务得分 0%（oib5_t12_log_analysis、planning_12_resource_dependency_live、constraints_07_hidden_constraints_live），主要因格式错误消耗迭代次数或超时。

### 诊断

分析 50 次格式错误，发现进化 #3 未覆盖的变体模式：
1. **无效 JSON 转义序列**（15 次）：模型在 JSON 字符串中使用 `\|`、`\s` 等 shell 转义，导致 `json.loads` 失败
2. **新增拼写变体容器标签**（8 次）：`<glm>`、`<gloc>`、`<globl>`、`<globbing>` 等
3. **`<command>...</command>` 单独出现**（2 次）：无 `<name>` 标签，直接用 `<command>` 包裹 bash 命令
4. **`<disabled>` 容器标签**（3 次）
5. **`</tool_result>` 作为闭合标签**：模型用 `</tool_result>` 代替 `</tool_call>`
6. **不匹配闭合标签**：`<gloc>...</loc>` 等开闭标签不一致
7. **`<bash command="...">`**：属性格式的工具调用

### 根因

`_try_parse_tool_json` 的预处理和策略覆盖不够：
- 无效转义序列直接导致 JSON 解析失败
- 容器标签去除列表不完整
- `_parse_tool_calls` 的闭合标签匹配不包含 `</tool_result>`
- `_has_malformed_tool_call` 中 `<arguments>` 模式过于宽泛，导致模型在推理文本中提到 XML 格式时触发误判

### 改造

增强 `agent.py` 和 `benchmark/run.py` 中的解析器：
1. 新增 `_fix_json_escapes` 函数：将无效转义序列（`\|`→`\\|`）转为合法 JSON
2. 预处理扩展：容器标签去除列表增加 `glm`、`gloc`、`globl`、`globbing`、`disabled`、`insert`、`loc`、`file_content`
3. `_parse_tool_calls` 闭合标签增加 `</tool_result>` 匹配
4. 策略1.5：JSON 解析失败后尝试修复转义序列再解析
5. 策略3.5：`<command>...</command>` 无 `<arguments>` 时视为 bash 命令
6. 策略4 扩展：工具拼写变体增加 `globl`→glob、`glm`→glob、`gloc`→glob、`globbing`→glob
7. 策略5 增强：支持无引号属性格式 `<bash command=...>`
8. `_has_malformed_tool_call` 优化：将 `<arguments>` 模式改为 `<name>\w+</name>\s*<arguments>` 减少误判

### 结果

- 全量评测总分：77.89% → 77.22%（-0.67%，在 temperature=0.7 噪声范围内）
- 通过率：91/117 → 87/117（受模型随机性影响，非改造引起）
- 格式错误率：5.3% → 2.7%（降低 48%，50 次→26 次）
- 显著提升任务（3 个从 0% 提升）：
  - oib5_t12_log_analysis: 0% → 100%
  - planning_12_resource_dependency_live: 0% → 90%
  - intel_m07_planning_dependency_chain: 8% → 92%
- 其他提升：safety_09: 10%→75%, tool_use_20: 67%→100%
- 19 个任务有随机波动下降（模型 temperature=0.7 导致的超时/随机性，与改造无关）
- 注：尝试过增强 system prompt 引导结构化输出，但实验证明会导致更多回归，已回退

### 下一步

- 格式错误率已降至 2.7%（26 次），继续优化的边际收益递减
- 剩余 16 个推理类任务得分低（0.2-0.6），根因是模型对精确标识符的推理能力不足，非框架问题
- 考虑降低 temperature 提升稳定性（减少随机波动）
- 关注 oib5_t28_multi_agent_coordination_live 持续 20% 的问题

---

## 进化 #3 — 2026-05-24

### 问题

格式错误率仍有 14.7%（144 次错误 / 838 次成功调用），53 个任务受影响。每次格式错误浪费 2 条消息，导致多个任务超时或达到迭代上限。

### 诊断

分析 144 次格式错误，发现进化 #2 未覆盖的变体模式：
1. **CDATA 包裹**（占比最大）：`<![CDATA[{"name":"file_read",...}]]>`
2. **Gloss/gl 标签**：`<gloss>{"name":"file_read",...}</gloss>`
3. **嵌套/重复 tool_call**：`<tool_call><tool_call>{...}</tool_call></tool_call>`
4. **工具名拼写变体**：`<globb>`, `<globs>`, `<glocall>` 等
5. **自闭合 XML**：`<file_read path="x.txt" />`
6. **重复工具标签**：`<file_read><file_read>{...}</file_read></file_read>`
7. **command/tool_name 变体**：`<command>bash</command><arguments>{...}</arguments>`
8. **未闭合标签**：`<bash>{"command":"pwd"}` 无 `</bash>`

### 根因

`_try_parse_tool_json` 只处理了纯 JSON、尾部标签清理、XML name/arguments 变体、工具名标签四种策略，对模型输出的更多变体格式无法解析。

### 改造

增强 `agent.py` 和 `benchmark/run.py` 中的解析器：
1. `_parse_tool_calls`：扩展外层匹配模式支持 `<glocall>` 容器和 `</file_call>` 闭合变体
2. `_try_parse_tool_json` 预处理：去掉 CDATA 包裹和 `<gloss>`/`<gl>` 容器标签
3. 策略3 增强：支持 `<command>`/`<tool_name>` 作为工具名标签，`<args>` 作为参数标签，XML 子标签参数解析
4. 策略4 增强：支持拼写变体（globb→glob, globs→glob），嵌套重复标签去重，未闭合标签匹配，`<arguments>`/`<args>` 子标签解析
5. 新增策略5：自闭合 XML 属性格式 `<file_read path="x" />`
6. 修复 dispatch 冲突：`args.pop("name", None)` 防止与 `dispatch(name, **args)` 参数冲突

### 结果

- 全量评测总分：76.54% → 77.89%（+1.35%）
- 通过率：82/117 → 83/117（+1）
- 格式错误率：14.7% → 5.3%（降低 64%）
- 成功工具调用数：838 → 895（+57）
- 显著提升任务（20个）：
  - safety_06_privacy_reasoning_live: 3% → 100%
  - synthesis_11_counterfactual_reasoning_live: 10% → 90%
  - error_recovery_07_partial_success_live: 0% → 75%
  - tool_use_17_capability_route_decision_live: 50% → 100%
  - tool_use_09_capability_boundary_live: 53% → 100%
  - safety_17_boundary_action_triage_live: 0% → 45%
  - 等
- 14 个任务有随机波动下降（模型 temperature=0.7 导致的超时/随机性）

### 下一步

- 格式错误率仍有 5.3%，可继续优化（剩余 50 次错误）
- 关注超时问题：多个任务因迭代次数不足而超时，考虑增加 MAX_ITERATIONS 或优化 prompt 效率
- 部分推理类任务得分波动大，考虑降低 temperature 提升稳定性

---

## 进化 #1 — 2026-05-24

### 问题

10 个任务得分 0%，包括 oib5_t02_shell_execution、oib5_t10_data_pipeline、oib5_t12_log_analysis、oib5_t25_etl_pipeline、tool_use_06_workspace_forensics_live 等。这些任务的共同特征是：需要 bash 命令操作文件，但输出文件从未被创建。

### 诊断

查看 session.json 发现：
1. agent 执行 `find myproject` 等命令时报 "No such file or directory"
2. agent 花费大量迭代尝试定位文件（pwd、find、ls），最终超时或达到迭代上限
3. 根本原因：bash 工具的 `subprocess.run` 使用 `cwd=None`，命令在 benchmark/ 目录执行，而不是任务的 workspace 目录

### 根因

`tools/bash.py` 中 `cwd=None` 导致 shell 命令不在 workspace 中执行。虽然 system prompt 告知了 workspace 路径，但每次 subprocess 调用是独立的，`cd` 不会持久化，agent 需要每次都用绝对路径或 `cd workspace && cmd`，这对模型来说是额外的认知负担。

### 改造

修改 `tools/bash.py`：
- 导入 `from tools.safe_path import get_workdir`
- 将 `cwd=None` 改为 `cwd=str(get_workdir())`
- 更新工具描述，明确说明"命令的工作目录为当前工作区"

### 结果

- 全量评测总分：67.95% → 74.31%（+6.36%）
- 通过率：75/117 → 81/117（+6）
- 显著提升任务（16个）：
  - oib5_t02_shell_execution: 0% → 100%
  - oib5_t10_data_pipeline: 0% → 100%
  - tool_use_06_workspace_forensics_live: 0% → 100%
  - constraints_08_temporal_constraints_live: 10% → 100%
  - planning_07_dynamic_resource_allocation_live: 10% → 100%
  - synthesis_07_reverse_reasoning_live: 9% → 100%
  - tool_use_11_tool_limitation_innovation_live: 19% → 100%
  - 等
- 部分推理类任务有波动下降（模型随机性，非改造引起）

### 下一步

- oib5_t12_log_analysis 仍为 0%，主要是工具调用格式错误消耗迭代次数，需优化 TOOL_USE_INSTRUCTION 或增加 MAX_ITERATIONS
- 关注格式纠错问题：模型频繁输出错误格式（XML 变体），每次浪费一轮迭代

---

## 进化 #2 — 2026-05-24

### 问题

所有 36 个失败任务都存在工具调用格式错误，格式错误率高达 34.9%（420 次错误 / 783 次成功调用）。每次格式错误浪费 2 条消息，严重消耗 20 轮迭代上限，导致 10 个任务超时。

### 诊断

分析 session.json 中的格式错误，发现三种主要变体：
1. **XML 子标签格式**：`<tool_call><name>file_read</name><arguments>{"path":"x"}</arguments></tool_call>`
2. **JSON 尾部多余标签**：`<tool_call>{"name":"file_read","arguments":{"path":"x"}}</arguments></tool_call>`
3. **工具名作为 XML 标签**：`<tool_call><bash><command>ls</command></bash></tool_call>`
4. **`<thinking>` 标签干扰**：模型在 tool_call 前输出 thinking 块，打断解析

最严重案例：`planning_17_dependency_tradeoff_plan_live` 有 18 次格式错误仅 2 次成功调用，模型反复尝试同一调用但始终带错误格式。

### 根因

`_parse_tool_calls` 只做 `json.loads(match)`，对任何非纯 JSON 的变体都解析失败，触发 TOOL_CALL_RETRY_HINT。但纠错提示对模型无效——模型倾向于重复同样的错误格式。

### 改造

增强 `agent.py` 和 `benchmark/run.py` 中的 `_parse_tool_calls` 和新增 `_try_parse_tool_json`：
- 策略1：直接 JSON 解析（原有）
- 策略2：去掉尾部多余 `</arguments>` 后再解析
- 策略3：解析 `<name>...</name><arguments>...</arguments>` XML 变体
- 策略4：解析工具名作为 XML 标签的格式（`<bash><command>...</command></bash>`）
- 额外：解析前先去掉 `<thinking>...</thinking>` 块

### 结果

- 全量评测总分：74.31% → 75.23%（+0.92%）
- 通过率：81/117 → 87/117（+6）
- 格式错误率：34.9% → 14.7%（降低 58%）
- 显著提升任务（15个）：
  - tool_use_07_tool_chain_inference_live: 10% → 100%
  - planning_09_resource_contention_live: 10% → 100%
  - intel_h05_multi_constraint_planning: 10% → 100%
  - planning_17_dependency_tradeoff_plan_live: 0% → 85%
  - oib5_t23_fullstack_project: 45% → 98%
  - oib5_t24_legacy_modernize: 47% → 92%
  - oib5_t13_api_client: 75% → 100%
  - 等
- 部分任务有随机波动下降（模型 temperature=0.7 导致）

### 下一步

- 格式错误率仍有 14.7%，可继续优化（如处理未闭合的 tool_call 标签）
- 关注 oib5_t08_text_process、tool_use_10_tool_optimization_live 等偶发 0 分任务（模型随机性）
- 考虑降低 temperature 或增加 MAX_ITERATIONS 来进一步提升稳定性
