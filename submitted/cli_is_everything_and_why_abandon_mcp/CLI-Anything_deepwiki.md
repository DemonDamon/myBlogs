# CLI-Anything DeepWiki 问答记录

> 工具：DeepWiki MCP (`user-deepwiki`)
> 仓库：HKUDS/CLI-Anything
> 日期：2026-03-14
>
> **重要**：DeepWiki 的回答质量不稳定，部分回答混入了不相关项目（如 Devin CLI）的内容。所有关键结论均需与本地源码交叉校验。

---

## Q1: CLI-Anything 的整体架构、核心组件、执行流和 7-Phase Pipeline 是什么？

**A1（DeepWiki 原始回答摘要）**：
- 核心组件包括 `main.py`、`cli_anything_utils.py`、`harness_generation_utils.py`
- 执行流：用户运行 `/cli-anything` → 解析参数 → 7-Phase Pipeline → 输出 CLI harness
- 7-Phase：Analyze → Design → Implement → Plan Tests → Write Tests → Document → Publish

**源码校验备注**：
- ⚠️ **DeepWiki 回答不准确**。CLI-Anything 不存在 `main.py`/`cli_anything_utils.py`/`harness_generation_utils.py` 这些文件。
- ✅ **实际架构**：CLI-Anything 是一个**基于 Prompt 的方法论框架**，不是可执行的 Python 程序。
  - 核心是 `cli-anything-plugin/HARNESS.md`——一个 SOP 文档，由 Claude Code / Codex / OpenCode 等 Agent 在运行时读取并执行。
  - `cli-anything-plugin/commands/*.md` 定义了插件的 slash 命令（`/cli-anything`、`/refine`、`/test`、`/validate`）。
  - 这些 `.md` 文件就是 Agent 的"指令"，Agent 读取后按 SOP 自主执行 7 个阶段。
  - **没有硬编码的 pipeline 执行引擎**——执行者是 AI Agent 本身。

---

## Q2: 生成的 CLI Harness 的设计模式和架构？Click CLI、repl_skin.py、Session/State 管理？

**A2（DeepWiki 原始回答摘要）**：
- 混入了 `devin/cli/core.py` 相关内容（完全不相关）

**源码校验备注**：
- ⚠️ **完全不准确**。DeepWiki 混入了 Devin 项目的代码。
- ✅ **实际架构**（来源：`gimp/agent-harness/cli_anything/gimp/gimp_cli.py`、`HARNESS.md`）：
  1. **Click CLI**：使用 `@click.group(invoke_without_command=True)` 作为入口；命令组包括 `project`/`layer`/`canvas`/`filter`/`media`/`export`/`session`/`draw`
  2. **`repl_skin.py`**：统一 REPL 皮肤，提供 banner/prompt/success/error/warning/info/table/progress/help/goodbye。每个 harness 复制一份到 `utils/repl_skin.py`
  3. **Session 管理**：`core/session.py` 实现 `Session` 类，维护当前项目、undo/redo 栈（`snapshot()`/`undo()`/`redo()`）
  4. **State 持久化**：项目状态以 JSON 文件保存（`.gimp-cli.json` 等）
  5. **输出模式**：`--json` flag 控制 JSON 输出 vs 人类可读输出

---

## Q3: 扩展机制和插件点？Claude Code Marketplace？Codex Skill？OpenCode Commands？

**A3（DeepWiki 原始回答摘要）**：
- 提到 `Extension`/`ExtensionManager`/`registerExtension`

**源码校验备注**：
- ⚠️ **完全不准确**。CLI-Anything 不存在 `ExtensionManager` 或 `Extension` 类。
- ✅ **实际扩展机制**（来源：本地源码）：
  1. **Claude Code Plugin**：`.claude-plugin/marketplace.json` 声明插件；`cli-anything-plugin/.claude-plugin/` 定义 Claude Code 可识别的目录结构
  2. **Codex Skill**：`codex-skill/SKILL.md` 遵循 Anthropic SKILL.md 规范，提供名称/描述/工作流
  3. **OpenCode Commands**：`opencode-commands/*.md` 是 OpenCode 的 slash command 定义文件
  4. **Qodercli Plugin**：`qoder-plugin/setup-qodercli.sh` 注册到 `~/.qoder.json`
  5. **添加新软件目标**：按 `HARNESS.md` 的 `Directory Structure` 创建 `<software>/agent-harness/cli_anything/<software>/` 即可
  6. **PEP 420 命名空间包**：`cli_anything/` 无 `__init__.py`，允许多个独立包共存

---

## Q4: 测试策略详解？四层测试？`_resolve_cli`？输出验证？

**A4（DeepWiki 原始回答摘要）**：
- 提到四层测试、`_resolve_cli`、magic bytes 等

**源码校验备注**：
- ⚠️ **部分不准确**。DeepWiki 编造了 `src/cli_anything/cli_utils.py` 路径和错误的 `_resolve_cli` 实现。
- ✅ **实际测试策略**（来源：`HARNESS.md` 第 137-405 行）：
  1. **Unit tests** (`test_core.py`)：纯合成数据，无外部依赖
  2. **E2E tests — native** (`test_full_e2e.py`)：验证中间文件（ODF/XML/SVG 结构）
  3. **E2E tests — true backend** (`test_full_e2e.py`)：调用真实软件（LibreOffice/Blender/melt），验证输出（magic bytes/ZIP 结构/像素分析）
  4. **CLI subprocess tests** (`test_full_e2e.py`)：通过 `subprocess.run` 调用已安装的 `cli-anything-<software>` 命令
  5. **`_resolve_cli(name)`**：定义在每个 harness 的测试文件中（不是独立模块），先 `shutil.which(name)` 查找，失败时 fallback 到 `python -m cli_anything.<software>.<software>_cli`
  6. **`CLI_ANYTHING_FORCE_INSTALLED=1`**：环境变量，设置后 fallback 不生效，强制使用已安装命令
