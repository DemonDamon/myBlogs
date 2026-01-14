# Introducing Agent Skills

> 来源：https://claude.com/blog/skills
> 
> Claude现在可以使用Skills来改进它执行特定任务的方式。

- **分类**: Product announcements
- **产品**: Claude Developer Platform
- **日期**: October 16, 2025
- **阅读时间**: 5分钟

---

**更新：** 我们已经添加了[组织范围的Skills管理](https://claude.com/blog/skills-for-organizations-partners-the-ecosystem)、一个[目录](https://claude.com/resources/skills)展示合作伙伴构建的Skills，并发布了[Agent Skills](https://github.com/anthropics/agent-skills)作为跨平台可移植性的开放标准。（2025年12月18日）

Claude现在可以使用**Skills**来改进它执行特定任务的方式。Skills是包含指令、脚本和资源的文件夹，Claude可以在需要时加载它们。

Claude只会在任务相关时访问skill。使用时，Skills使Claude在专业任务上表现更好，比如使用Excel或遵循你组织的品牌指南。

你已经在Claude应用中看到了Skills的作用，Claude使用它们来创建电子表格和演示文稿等文件。现在，你可以构建自己的Skills，并在Claude应用、Claude Code和我们的API中使用它们。

## Skills如何工作

在处理任务时，Claude扫描可用的Skills以找到相关匹配。当匹配时，它只加载所需的最少信息和文件——在访问专业知识的同时保持Claude的快速。

Skills是：

* **可组合的**：Skills可以堆叠在一起。Claude自动识别需要哪些Skills并协调它们的使用。
* **可移植的**：Skills在所有地方使用相同的格式。构建一次，在Claude应用、Claude Code和API中使用。
* **高效的**：只在需要时加载所需的内容。
* **强大的**：Skills可以包含可执行代码，用于传统编程比token生成更可靠的任务。

将Skills视为自定义入职材料，让你可以打包专业知识，使Claude成为对你最重要的领域的专家。有关Agent Skills设计模式、架构和开发最佳实践的技术深度分析，请阅读我们的[工程博客](https://www.anthropic.com/research/agent-skills)。

## Skills适用于每个Claude产品

### Claude应用

Skills适用于Pro、Max、Team和Enterprise用户。我们为常见任务提供Skills，你可以自定义的示例，以及创建自己的自定义Skills的能力。

Claude.ai中的Skills功能界面，示例Skills已启用。

Claude根据你的任务自动调用相关Skills——无需手动选择。你甚至会在Claude工作时在其思维链中看到Skills。

创建Skills很简单。"skill-creator" skill提供交互式指导：Claude询问你的工作流程，生成文件夹结构，格式化SKILL.md文件，并打包你需要的资源。无需手动编辑文件。

在设置中启用Skills。对于Team和Enterprise用户，管理员必须首先在组织范围内启用Skills。

### Claude Developer Platform (API)

Agent Skills（我们通常简称为Skills）现在可以添加到Messages API请求中，新的`/v1/skills`端点为开发者提供了对自定义skill版本和管理的程序化控制。Skills需要Code Execution Tool beta，它提供了运行所需的安全环境。

使用Anthropic创建的Skills可以让Claude读取和生成带有公式的专业Excel电子表格、PowerPoint演示文稿、Word文档和可填写的PDF。开发者可以创建自定义Skills来扩展Claude的功能，以满足他们的特定用例。

开发者还可以通过Claude Console轻松创建、查看和升级skill版本。

探索[文档](https://docs.anthropic.com/en/docs/build-with-skills)、我们的[skills cookbook](https://github.com/anthropics/agent-skills)，或[Anthropic Academy](https://academy.anthropic.com/)了解更多。

---

### 合作伙伴案例

**Box**

Skills教Claude如何与Box内容协作。用户可以将存储的文件转换为遵循其组织标准的PowerPoint演示文稿、Excel电子表格和Word文档——节省数小时的工作。

— Yashodha Bhavnani, Head of AI

**Canva**

Canva计划利用Skills来自定义代理并扩展它们的功能。这解锁了将Canva更深入地融入代理工作流程的新方法——帮助团队捕获其独特的上下文并轻松创建令人惊叹的高质量设计。

— Anwar Haneef, GM & Head of Ecosystem

**Notion**

使用Skills，Claude与Notion无缝协作——让用户从问题更快地转向行动。在复杂任务上减少提示处理，获得更可预测的结果。

— MJ Felix, Product Manager

**其他企业案例**

Skills简化了我们的管理会计和财务工作流程。Claude处理多个电子表格，捕获关键异常，并使用我们的程序生成报告。以前需要一天的工作，我们现在可以在一个小时内完成。

— Yusuke Kaji, General Manager AI

### Claude Code

Skills通过你团队的专业知识和工作流程扩展Claude Code。通过anthropics/skills市场中的插件安装Skills。Claude在相关时自动加载它们。通过版本控制与团队共享Skills。你也可以通过将它们添加到`~/.claude/skills`来手动安装Skills。Claude Agent SDK为构建自定义代理提供相同的Agent Skills支持。

## 开始使用

* **Claude应用**：[用户指南和帮助中心](https://support.anthropic.com/en/articles/9452000-skills-overview)
* **API开发者**：[文档](https://docs.anthropic.com/en/docs/build-with-skills)
* **Claude Code**：[文档](https://docs.anthropic.com/en/docs/claude-code-skills)
* **可自定义的示例Skills**：[GitHub仓库](https://github.com/anthropics/agent-skills)

## 下一步

我们正在努力简化skill创建工作流程和企业范围的部署功能，使组织更容易在团队之间分发Skills。

请记住，此功能使Claude能够执行代码。虽然强大，但这意味着要注意你使用哪些Skills——坚持使用可信来源以保护你的数据安全。[了解更多](https://docs.anthropic.com/en/docs/build-with-skills#security)。

---

## 相关文章

- [Cowork: Claude Code for the rest of your work](https://claude.com/blog/cowork-claude-code-for-the-rest-of-your-work) (Jan 12, 2026)
- [Claude can now use tools](https://claude.com/blog/claude-can-now-use-tools) (May 30, 2024)
- [Managing context on the Claude Developer Platform](https://claude.com/blog/managing-context-on-the-claude-developer-platform) (Sep 29, 2025)
- [Skills for organizations, partners, the ecosystem](https://claude.com/blog/skills-for-organizations-partners-the-ecosystem) (Dec 18, 2025)
