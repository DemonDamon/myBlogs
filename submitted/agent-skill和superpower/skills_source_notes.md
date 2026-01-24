# Source Notes - anthropics/skills

## 1. 它解决了什么问题 (Problem Solved)
Agent Skills 旨在解决通用大模型在处理专业、程序化任务时的局限性：
- **上下文压力**：通过“渐进式披露（Progressive Disclosure）”机制，避免将海量专业文档一次性塞入 Context Window，只有在触发时才加载详细指令。
- **程序化确定性**：对于模型容易出错或重复生成的逻辑（如复杂的 PDF 旋转、OOXML 操作），通过捆绑可执行脚本（Scripts）提供确定性保障。
- **模块化扩展**：将指令、脚本、参考资料和资产（Assets）打包成独立的文件夹，便于分发、管理和复用，使 Claude 能够从通用助理转变为领域专家。

## 2. 关键抽象 (Key Abstractions)
- **Skill (技能)**：最小的能力单元，由一个文件夹组成，核心是 `SKILL.md`。
- **SKILL.md**：技能的“说明书”。
    - **Metadata (Frontmatter)**：包含 `name` 和 `description`，是触发技能的唯一依据。
    - **Body (Markdown)**：技能触发后加载的详细指令。
- **Bundled Resources (捆绑资源)**：
    - `scripts/`：可执行代码（Python/Bash），提供确定性，可不加载到上下文直接执行。
    - `references/`：可选加载的背景文档（如 API 定义、业务规范）。
    - `assets/`：输出模板或资产（如字体、Logo、PPT 模板），不进入上下文。
- **Progressive Disclosure (渐进式披露)**：三级加载机制（Metadata -> Body -> Resources）。
- **Marketplace (市场)**：通过 `.claude-plugin/marketplace.json` 定义的技能注册表。

## 3. 关键调用链 (Key Call Chain)
1. **发现阶段 (Discovery)**：系统启动时扫描 `marketplace.json`，将所有 Skill 的 `name` 和 `description` 加载到初始上下文。
2. **触发阶段 (Trigger)**：LLM 根据用户 Query 匹配 `description`，决定激活特定 Skill。
3. **加载阶段 (Loading)**：系统动态读取该 Skill 文件夹下的 `SKILL.md` 正文，追加到 LLM 上下文。
4. **执行阶段 (Execution)**：LLM 根据 `SKILL.md` 指令进行推理，如需执行脚本，调用工具执行 `scripts/` 下的代码并获取结果。

## 4. 失败模式与错误处理 (Failure Modes)
- **描述漂移 (Metadata Drift)**：`description` 写得不准确导致 LLM 在该用时没触发，或误触发。
- **上下文膨胀 (Context Bloat)**：`SKILL.md` 正文超过 500 行或 5k Token，导致推理性能下降。
- **脚本执行异常**：`scripts/` 脚本运行时环境缺失、超时或权限不足（规范中未明确沙箱细节，但提示需在本地环境测试）。
- **引用断链**：`SKILL.md` 引用了不存在的 `references/` 文件。

## 5. 扩展点 (Extension Points)
- **新技能开发**：只需创建符合文件夹结构的目录，无需修改核心引擎。
- **多语言脚本**：支持 Python, Bash, Node.js 等（依赖宿主环境）。
- **Marketplace 联邦**：可以添加多个 GitHub 仓库作为 marketplace。

## 6. 交叉校验 (Cross-validation)
| 结论 | 证据 (源码/文档位置) | 状态 | 修正/备注 |
| :--- | :--- | :--- | :--- |
| 脚本可不进入上下文执行 | `skills/skill-creator/SKILL.md` L79 | 是 | 极大节省 Token 且保证逻辑确定性。 |
| SKILL.md Body 仅在触发后加载 | `skills/skill-creator/SKILL.md` L69, L116 | 是 | 依赖宿主引擎（如 Claude Code）实现。 |
| Marketplace 通过 JSON 联邦 | `.claude-plugin/marketplace.json` | 是 | 结构清晰，易于实现去中心化扩展。 |
| 资产（Assets）不进入上下文 | `skills/skill-creator/SKILL.md` L100 | 是 | 仅供输出使用，防止 Context 污染。 |

