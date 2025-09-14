# 7_Test_AI_Perceptron
EvoPrompt — 自动化提示词库优化框架

简介
----
EvoPrompt 是一个用于自动化提示词（prompt）优化的轻量级框架。采用“学生-教师”模式：学生模型（student，DeepSeek）生成文本，教师模型（teacher，GPT-4 或 DeepSeek）对学生输出进行评价并提出改进建议，系统根据教师的反馈迭代更新提示词库。

主要特性
----
- 支持 OpenAI-compatible 的模型调用（已实现对 DeepSeek 的兼容调用路径）
- 提示词本地化存储（`prompts/`，JSON 格式，含版本历史）
- 教师评分与反馈规范化为 JSON（score、criteria、feedback、suggested_prompt）
- 简单优化器（基于教师建议或保守规则生成候选提示词）
- 缓存机制避免重复调用（`.cache/`）
- 日志与结果存储（`logs/`、`results/`）
- 演示脚本：`run_demo.py`（交互）与 `run_full_demo.py`（非交互批量运行）

安装
----
推荐使用 Python 3.10+。

```bash
py -3 -m pip install -r requirements.txt
```

快速开始
----
1. 配置 API Key（示例使用 DeepSeek）：
   - 在交互运行时输入，或在运行 `run_full_demo.py` 前通过环境变量设置：
     - `DEEPSEEK_API_KEY`
     - `DEEPSEEK_BASE_URL`（例如 `https://api.deepseek.com`）
     - 可选：`DEEPSEEK_MODEL`（默认 `deepseek-chat`）

2. 运行交互式演示：
   ```bash
   py -3 run_demo.py
   ```

3. 运行非交互全流程（示例）：
   - 将 API key 导出为环境变量后运行：
   ```powershell
   $env:DEEPSEEK_API_KEY='sk-...'
   $env:DEEPSEEK_BASE_URL='https://api.deepseek.com'
   py -3 run_full_demo.py
   ```

文件与目录说明
----
- `evo_prompt/`：主代码包（clients、prompt_store、evaluator、optimizer、workflow、cache、logger、cli 等）
- `prompts/`：提示词 JSON 文件（含版本历史）
- `logs/`：运行期间写入的原始响应与评估记录（JSONL）
- `results/`：每次迭代的结构化结果（JSON）
- `run_demo.py`：交互式演示脚本（按轮次询问是否应用优化）
- `run_full_demo.py`：非交互自动运行脚本（读取环境变量）
- `smoke_test.py`：脱离 API 的本地测试脚本（使用 MockClient）

安全与注意事项
----
- 请勿将 API key 直接写入代码或提交到版本控制。建议通过环境变量或安全秘钥管理器提供密钥。
- 日志中目前会记录模型原文响应，如需脱敏请在运行前调整 `logger` 或使用脚本清理日志。

下一步建议
----
- 添加更严格的单元测试与 CI 配置
- 增强 `Evaluator` 的解析鲁棒性与教师评分模板
- 扩展 Optimizer 为多候选生成与 A/B 比较

