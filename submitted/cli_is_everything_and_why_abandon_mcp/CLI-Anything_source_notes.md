# CLI-Anything 源码阅读笔记

## 1. 它解决了什么问题（边界/非目标）

### 核心问题
AI Agent 能推理但不能操作真实专业软件（GIMP/Blender/LibreOffice 等）。现有方案（GUI 自动化/有限 API/简化重实现）都有严重缺陷。

### CLI-Anything 的解法
**一条命令把任意 GUI 软件变成 Agent 可控的 CLI 工具。** 本质是一个**基于 Prompt 的方法论框架**（不是可执行的 pipeline 引擎），由 AI Agent（Claude Code / Codex / OpenCode）读取 HARNESS.md SOP 后自主执行 7 个阶段。

### 边界
- ✅ 为已有源码的开源 GUI 软件生成 CLI harness
- ✅ 生成的 CLI 调用真实软件后端（非重实现）
- ✅ 支持 REPL + 一次性命令双模式
- ✅ 输出 JSON（机器消费）+ 人类可读格式
- ✅ 跨 Agent 平台（Claude Code/Codex/OpenCode/Qodercli）

### 非目标
- ❌ 不是通用 pipeline 引擎——执行者是 AI Agent，不是 Python 程序
- ❌ 不处理闭源二进制软件（需源码分析）
- ❌ 不替代软件本身——生成的 CLI 是"接口"，不是"重实现"
- ❌ 不处理 GUI 自动化——纯 CLI/API 路线

## 2. 关键抽象（7 个名词）

| 抽象 | 源码位置 | 说明 |
|------|---------|------|
| **HARNESS.md** | `cli-anything-plugin/HARNESS.md` | 方法论 SOP，唯一的 source of truth |
| **Command (slash command)** | `cli-anything-plugin/commands/*.md` | Agent 的指令定义（`/cli-anything`、`/refine`、`/test`、`/validate`） |
| **Agent Harness** | `<software>/agent-harness/` | 为特定软件生成的完整 CLI 包 |
| **Core Module** | `cli_anything/<software>/core/` | 业务逻辑模块（project/session/export/layers 等） |
| **Backend Wrapper** | `cli_anything/<software>/utils/<software>_backend.py` | 真实软件的调用封装 |
| **ReplSkin** | `cli-anything-plugin/repl_skin.py` | 统一 REPL 界面皮肤 |
| **Namespace Package** | `cli_anything/`（无 `__init__.py`） | PEP 420 命名空间，多 CLI 共存 |

## 3. 关键调用链

### 3.1 生成阶段（Agent 执行）

```
用户: /cli-anything <software-path>
  → Agent 读取 HARNESS.md
  → Phase 1: 分析源码（识别后端引擎/GUI-API 映射/数据模型/现有 CLI）
  → Phase 2: 设计 CLI 架构（命令组/状态模型/输出格式）
  → Phase 3: 实现（数据层→探查命令→变更命令→后端集成→导出→会话管理→REPL）
  → Phase 4: 测试规划（TEST.md）
  → Phase 5: 测试实现（test_core.py + test_full_e2e.py）
  → Phase 6: 测试文档（追加结果到 TEST.md）
  → Phase 7: 打包发布（setup.py + pip install -e .）
```

### 3.2 运行阶段（生成的 CLI）

```
用户/Agent: cli-anything-gimp --json project new -o poster.json
  → gimp_cli.py:cli() — Click group 入口
  → 检查 --json flag，设置 _json_output
  → 检查 --project flag，加载已有项目
  → 路由到 project.new 子命令
  → proj_mod.create_project() — core/project.py
  → Session.set_project() — core/session.py
  → output() — JSON 或人类可读
```

### 3.3 REPL 模式

```
用户: cli-anything-gimp（无参数）
  → cli() 检测 ctx.invoked_subcommand is None
  → ctx.invoke(repl)
  → ReplSkin("gimp").print_banner()
  → 循环: skin.get_input() → cli.main(args, standalone_mode=False)
  → quit/exit 退出
```

## 4. 失败模式与错误处理

| 场景 | 处理策略 |
|------|---------|
| 软件未安装 | `utils/<software>_backend.py` 中 `shutil.which()` 检查，失败时 `raise RuntimeError` 并附带安装说明 |
| 无效参数 | `handle_error` 装饰器捕获 `ValueError/IndexError/RuntimeError`，JSON 模式输出错误 JSON，非 REPL 模式 `sys.exit(1)` |
| REPL 中的错误 | 捕获异常后继续（不退出 REPL），打印 `skin.error()` |
| 导出失败 | HARNESS.md 规定"不信任退出码为 0"，必须验证输出文件（magic bytes/ZIP 结构/像素分析） |
| 渲染差距 | HARNESS.md 的 "Rendering Gap" 教训：CLI 操作项目文件，但渲染必须用原生引擎（melt/ffmpeg/libreoffice --headless） |

## 5. 扩展点

| 扩展点 | 机制 | 稳定性 |
|--------|------|--------|
| 新增软件目标 | 按 HARNESS.md Directory Structure 创建目录 | ⭐⭐⭐ 稳定 |
| 新增 Agent 平台 | 参考 `opencode-commands/` 目录创建命令文件 | ⭐⭐ 中等 |
| CLI 命令扩展 | Click `@group.command()` 添加子命令 | ⭐⭐⭐ 稳定 |
| REPL 皮肤定制 | 继承或修改 `ReplSkin` | ⭐⭐ 中等 |
| 命名空间共存 | PEP 420 namespace package | ⭐⭐⭐ 稳定 |
| 后端替换 | 替换 `utils/<software>_backend.py` | ⭐⭐⭐ 稳定 |

## 6. 交叉校验表

| 结论 | 证据 | 属实 |
|------|------|------|
| CLI-Anything 是 Prompt 驱动的方法论框架 | `cli-anything-plugin/commands/cli-anything.md` 开头明确要求"Read HARNESS.md First" | ✅ 是 |
| 没有可执行的 pipeline 引擎 | 仓库中无 `main.py`/`cli_anything_utils.py` | ✅ 是 |
| 生成的 CLI 使用 Click 框架 | `gimp_cli.py` 第 116-136 行 | ✅ 是 |
| REPL 为默认模式 | `gimp_cli.py` 第 135-136 行 `invoke_without_command=True` | ✅ 是 |
| PEP 420 命名空间 | `HARNESS.md` 第 485-490 行明确说明 | ✅ 是 |
| 1508 个测试全部通过 | README 声明，需本地验证 | ⚠️ 未证实（需本地运行） |
| DeepWiki 回答中的 `ExtensionManager` | 仓库中不存在此类 | ❌ 不属实 |
| DeepWiki 回答中的 `src/cli_anything/cli_utils.py` | 不存在此路径 | ❌ 不属实 |
