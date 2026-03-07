# Claude Skills_skills目录-CSDN博客

**来源**: [https://blog.csdn.net/qq_41081984/article/details/156990291](https://blog.csdn.net/qq_41081984/article/details/156990291)
**爬取时间**: 2026年 2月15日 星期日 15时35分39秒 CST

 















Claude Skills\_skills目录-CSDN博客





# Claude Skills

最新推荐文章于 2026-01-30 20:52:38 发布

原创
最新推荐文章于 2026-01-30 20:52:38 发布
·
740 阅读

·
![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Active.png)
![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Black.png)

15

·
![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollect2.png)
![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollectionActive2.png)

17
·

CC 4.0 BY-SA版权

版权声明：本文为博主原创文章，遵循 [CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/) 版权协议，转载请附上原文出处链接和本声明。

文章标签：

[#agi](https://so.csdn.net/so/search/s.do?q=agi&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#程序人生](https://so.csdn.net/so/search/s.do?q=%E7%A8%8B%E5%BA%8F%E4%BA%BA%E7%94%9F&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#机器人](https://so.csdn.net/so/search/s.do?q=%E6%9C%BA%E5%99%A8%E4%BA%BA&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#人工智能](https://so.csdn.net/so/search/s.do?q=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)

![Python3.9](https://csdn-665-inscode.s3.cn-north-1.jdcloud-oss.com/image/cover/gpu_img_miniconda_py_3_9.png/middle)

Python3.9

Conda

Python

Python 是一种高级、解释型、通用的编程语言，以其简洁易读的语法而闻名，适用于广泛的应用，包括Web开发、数据分析、人工智能和自动化脚本

一键部署运行

## Claude Skills

最近 Claude 在 `github` 上有一个比较火的项目：`https://github.com/anthropics/skills`，项目是围绕新概念 `Skills`，我觉得实际上是：通过工程化结构来实现智能体，用一种工程范式来完成子功能，就像C++代码中提出一种更好的设计模式来解决通用问题。

#### 1. 什么是 `Skills`

`Skills` 是一组由说明文档、脚本与资源组成的 “技能包”，Claude 会在需要时动态加载，用于提升在特定任务上的一致性与表现，借助 `Skills`，Claude 能以可复用的方式完成某类任务，例如：按公司品牌规范创作文档、按组织特定流程分析数据，或自动化个人工作流。

#### `Skills` 如何工作

`Skills` 通过 “逐步迭代” 的方式工作：当你发起任务时，Claude 会审视可用 `Skills`，自动挑选相关的技能并只加载完成任务所需的指令与资源，这样既能提升速度与效果，也能避免将无关内容塞满上下文窗口，从而保持对话与计算的高效与稳定。

**核心机制：**

1. 你提出任务请求
2. Claude 在可用 `Skills` 中进行匹配与选择
3. 自动加载相关技能的指令/脚本/资源
4. 按技能流程执行任务，提高一致性与完成质量

**优势：**

* 提升专项任务表现：为文档创作、数据分析与领域任务提供专门能力，补强通用模型的知识与流程执行力
* 组织知识沉淀：将组织流程、最佳实践与制度化知识打包，使团队成员与 Claude 保持一致的执行标准
* 易于定制：使用 Markdown 编写说明即可创建基础 `Skills`，如需更高级功能，可为自定义技能附加可执行脚本
* 易于组合：对于复杂的任务，可以通过多个 `Skills` 组合迭代处理

**SKILL.md 模版文件：**

```
yaml
 体验AI代码助手
 代码解读
复制代码
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

#### 2. 与 Claude 其他功能对比

**Skills vs. Projects：**

* Projects：为特定项目对话提供 “持续加载” 的静态背景知识
* Skills：提供 “按需激活” 的专门流程与操作指南，并可在任意对话中动态生效

**Skills vs. MCP（Model Context Protocol）：**

* MCP：将 Claude 连接到外部服务与数据源
* `Skills`：提供 “如何完成任务” 的流程性知识与操作步骤
* 二者可协同：MCP 负责接入工具与数据，`Skills` 负责教会 Claude 如何有效使用这些工具

**Skills vs. Prompt**

* Prompt：对所有对话生效，强调通用偏好与风格
* `Skills`：面向特定任务，仅在相关时加载，更适合专业工作流与场景化流程

#### 3. `Skills` 目录结构

**`Skills` 目录结构如下：**

```
arduino
 体验AI代码助手
 代码解读
复制代码
my-skill/
├── SKILL.md (required)
├── reference.md (optional documentation)
├── examples.md (optional examples)
├── scripts/
│   └── helper.py (optional utility)
└── templates/
    └── template.txt (optional template)
```

##### 3.1 基础结构

* `Skills` 目录与 `SKILL.md` 文件
* 每个 `Skills` 至少包含一个目录和其中的 `SKILL.md` 文件
* `SKILL.md` 顶部必须以 `YAML frontmatter` 开始，至少包含 `name` 与 `description` 两个必填元数据字段
* 其余内容采用 “迭代执行” 原则：先读元数据，必要时再加载正文、参考文件与脚本，避免上下文过载

##### 3.2 元数据

* name【必填】：人类可读的 Skill 名称（≤ 64 字符），示例：Brand Guidelines
* description【必填】：Skill 的用途与触发条件（≤ 200 字符；Claude 依此判断何时调用），示例：Apply Acme Corp brand guidelines to presentations and documents, including official colors, fonts, and logo usage.
* version【可选】：版本号（便于演进与回滚），示例：1.0.0
* dependencies【可选】：所需软件包，示例：python>=3.8, pandas>=1.5.0

##### 3.3 `SKILL.md` 的正文

* 当仅凭元数据不足以执行任务时，Claude 会加载正文
* 正文可包含：执行步骤、规范细则、示例、何时/何不适用、引用的资源文件等

**`SKILL.md`样例：**

```
yaml
 体验AI代码助手
 代码解读
复制代码
---
name: Brand Guidelines
description: Apply Acme Corp brand guidelines to all presentations and documents, including official colors, fonts, and logo usage.
version: 1.0.0
dependencies: []
---

# Overview
This Skill provides Acme Corp's official brand guidelines for creating consistent, professional materials. When creating presentations, documents, or marketing materials, apply these standards to ensure all outputs match Acme's visual identity. Claude should reference these guidelines whenever creating external-facing materials or documents that represent Acme Corp.

## Brand Colors
- Primary: #FF6B35 (Coral)
- Secondary: #004E89 (Navy Blue)
- Accent: #F7B801 (Gold)
- Neutral: #2E2E2E (Charcoal)

## Typography
- Headers: Montserrat Bold
- Body text: Open Sans Regular
- Size guidelines:
  - H1: 32pt
  - H2: 24pt
  - Body: 11pt

## Logo Usage
- Use the full-color logo on light backgrounds; use the white logo on dark backgrounds.
- Maintain minimum spacing of 0.5 inches around the logo.

## When to Apply
Apply these guidelines when creating:
- PowerPoint presentations
- Word documents for external sharing
- Marketing materials
- Client-facing reports

## Examples
- Input: “Create a 10-slide pitch deck for Acme Corp’s new product.”
- Output: A PPT with the above colors, fonts, logo rules, and spacing applied consistently.

## Resources
See the resources folder for logo files and font downloads.
```

##### 3.4 `Skill` 涉及的资源

**`SKILL.md` 需要引入的资源文件**

* 当信息较多、且部分内容仅在特定情境需要时，可将补充材料拆分为独立文件（如 REFERENCE.md、CHECKLIST.md、TEMPLATES/）
* 在 `SKILL.md` 中引用这些文件，Claude 将按需加载，减少无关内容占用

**可执行脚本**

* 进阶 `Skill` 可附带可执行代码文件，供 Claude 调用以完成复杂任务（例如文档批量处理、数据清洗、可视化等）
* 常用语言与生态：
* + Python（pandas、numpy、matplotlib 等）
  + JavaScript / Node.js等
* 包管理约束：
* + Claude 与 Claude Code 在加载 `Skill` 时可从标准仓库安装依赖（Python PyPI、JavaScript npm）
  + 使用 API Skills 时，运行时无法临时安装新包，所有依赖必须预装在容器中

#### 4. 在 Claude 上如何使用

**上传前：**

1. 通读 `SKILL.md`，确保指令清晰、步骤完备
2. 确认 description 能准确描述 “何时使用”
3. 校验被引用文件路径与命名无误
4. 以若干示例提示词本地自测，观察 Claude 是否会触发该 Skill

**上传到 Claude 后：**

1. 在 Settings > Capabilities 中启用该 Skill
2. 使用多种应触发它的提示词进行验证
3. 确认 Claude 在响应中已加载 Skill（例如输出中体现技能名称或遵循技能流程）
4. 若未按预期触发，迭代完善 description 与正文的触发条件与范围

#### 5. 最佳实践：什么样的 `Skills` 才是好 “Skill”

* 指令清晰、可被 Claude 稳定执行
* 面向一个明确、可重复的任务
* 聚焦单一工作流：面向不同流程分别创建技能，小而专注的 Skills 更易组合复用
* 描述要具体：明确“适用对象、时机、边界与例外”，便于 Claude 正确判定调用
* 从简入手：先用 Markdown 指令跑通骨架，再逐步引入脚本与复杂逻辑
* 加示例：在 Skill.md 放入典型输入/输出，帮助对齐 “何为成功”
* 版本化：持续维护 version 字段，便于回溯与排错
* 渐进测试：每次重要变更后快速验证，避免一次性 “大改大上”
* 组合性：尽管 Skills 不能显式互相引用，但 Claude 可自动同时使用多个技能，发挥 “组装效应”

#### 6. `Claude Skills` 官方示例

Claude 官方提供 `https://github.com/anthropics/skills` 20+个样例，本文就拆解其中一个比较常用的，自动执行 `Web 应用程序测试` ，目录结构如下：

```
objectivec
 体验AI代码助手
 代码解读
复制代码
webapp-testing/
├── SKILL.md
├── scripts/
│   └── with_server.py
└── examples/
    └── console_logging.py
    └── element_discovery.py
    └── static_html_automation.py
```

##### 6.1 功能描述

根据 description 介绍当前功能，用于使用 Playwright 交互和测试本地 Web 应用程序的工具包，支持验证前端功能、调试 UI 行为、捕获浏览器截图以及查看浏览器日志。

```
yaml
 体验AI代码助手
 代码解读
复制代码
---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---
```

##### 6.2 正文-工作流程

这部分是正文重点的部分，介绍当前决策树的工作流，不过我觉得用时序图，EARS等也可以，只要能介绍清楚每个步骤需要做什么。

```
sql
 体验AI代码助手
 代码解读
复制代码
## Decision Tree: Choosing Your Approach

User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and waitfor networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

##### 6.3 正文-使用脚本示例

这部分主要是介绍脚本怎么使用，脚本执行前需要做什么，脚本执行后需要做什么等，如下：

```
perl
 体验AI代码助手
 代码解读
复制代码
## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:
...
```

##### 6.4 正文-其他

其他部分就是包括一些流程需要的细节，注意事项，涉及的一些文件是做什么的等介绍，如下：

```
shell
 体验AI代码助手
 代码解读
复制代码
## Reconnaissance-Then-Action Pattern
...

## Common Pitfall
...

## Best Practices
...

## Reference Files
...
```

#### 7. 总结

Claude `Skills` 是提供了一种工程范式，以前大家通过各种 `MCP`，`Agent` 等将功能组合起来，中间层通过 `Prompt` 粘合，一方面不容易维护和继承，另一方面没有规范会导致不稳定，但是 `Skills` 通过工程范式约束很大程度上解决 `AI` 项目的工程化问题；  
同时每一个 `Skills` 文件夹就是小的 `Agent`，这些 `Skills` 又可以组合为一个复杂的 `Agent`，就像我们写代码一样，先有基础库，然后通过基础库再组合复杂工程逻辑，这个大概是就是从混沌到规范化的历程。

您可能感兴趣的与本文相关的镜像

![Python3.9](https://csdn-665-inscode.s3.cn-north-1.jdcloud-oss.com/image/cover/gpu_img_miniconda_py_3_9.png/middle)

Python3.9

Conda

Python

Python 是一种高级、解释型、通用的编程语言，以其简洁易读的语法而闻名，适用于广泛的应用，包括Web开发、数据分析、人工智能和自动化脚本

一键部署运行

![](https://csdnimg.cn/release/blogv2/dist/pc/img/vip-limited-close-newWhite.png)

确定要放弃本次机会？

福利倒计时

*:*

*:*

![](https://csdnimg.cn/release/blogv2/dist/pc/img/vip-limited-close-roup.png)
立减 ¥

普通VIP年卡可用

[立即使用](https://mall.csdn.net/vip)

[![](https://profile-avatar.csdnimg.cn/default.jpg!1)

取个鸣字真的难](https://blog.csdn.net/qq_41081984)

[关注](javascript:;)
关注

* ![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarThumbUpactive.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/like-active.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/like.png)

  15

  点赞
* ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/unlike-active.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/unlike.png)

  踩
* [![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/collect-active.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/collect.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCollectActive.png)

  17](javascript:;)

  收藏

  觉得还不错?
  一键收藏
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/collectionCloseWhite.png)
* ![](https://csdnimg.cn/release/blogv2/dist/pc/img/guideRedReward01.png)
  知道了

  [![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/comment.png)

  0](#commentBox)

  评论
* [![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/share.png)
  分享](javascript:;)

  复制链接

  分享到 QQ

  分享到新浪微博

  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/share/icon-wechat.png)扫一扫
* ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/more.png)

  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/report.png)
  举报

  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/report.png)
  举报

![]()

[*Claude*的*Skills*详解](https://criss.blog.csdn.net/article/details/156311989)

[Criss@陈磊](https://blog.csdn.net/chenlei_525)

12-26
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
2035

[skill*目录*下最小集合是必须有一个SKILL.md文件，其他类似scripts/，references/，assets/等都是可选择项。在SKILL.md文件中，YAML格式的定义内容是必须存在的。---------metadata:---FieldRequiredYes最大64个字符。仅限小写字母、数字和连字符。不得以连字符开头或结尾。Yes最大1024个字符。非空字段。描述技能功能及使用场景。No许可证名称或捆绑许可证文件的引用。No最大500个字符。](https://criss.blog.csdn.net/article/details/156311989)

参与评论
您还未登录，请先
登录
后发表或查看评论

[详解*Claude* *Skills*——大模型的高级工具架构和规范](https://blog.csdn.net/liujunjiang/article/details/156641327)

[LiuJunjiang的专栏](https://blog.csdn.net/liujunjiang)

01-06
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
562

[*Claude* *Skills*是一种模块化AI工具架构，将专业知识打包为可执行的指令、脚本和资源包。其核心创新在于"渐进式披露"机制，通过三级加载(元数据→核心指令→按需资源)显著优化上下文窗口利用率，降低80-95%的Token消耗。该架构赋予AI在沙箱中执行Python/Bash脚本的能力，将LLM的推理能力与确定性计算相结合，提升金融建模、编程自动化等复杂任务的精确性。通过标准化知识封装和权限管控，*Claude* *Skills*实现了从静态对话到动态工作流代理的转型，使AI能像专业员工一样](https://blog.csdn.net/liujunjiang/article/details/156641327)

[2026 最新 *Claude* *Skills* 保姆级教程及实践！

最新发布](https://devpress.csdn.net/v1/article/detail/157554359)

[AI心易行者](https://blog.csdn.net/zhengiqa8)

01-30
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
852

[本文介绍了2026年最新*Claude* *Skills*技术，将其定义为"可复用的指令包"技能工具包，能解决AI专业知识缺乏问题。文章对比了*Skills*与MCP的区别，前者是操作逻辑导航系统，后者是连接外部工具的接口控制器。教程部分详细演示了安装使用步骤，推荐了5个必备*Skills*，并以"PDF转PPT"为例展示自制技能流程。作者认为*Skills*让AI从被动响应转向主动决策，将成为数字第二大脑，建议开发者掌握工具链后从开源库筛选技能包开始实践。文末还提供了AI编程手册和代码](https://devpress.csdn.net/v1/article/detail/157554359)

[有了 MCP，为啥 *Claude* 还要推出 *Skills*？一文带你搞懂它到底强在哪? MCP 有啥区别、该怎么用！](https://devpress.csdn.net/v1/article/detail/154398698)

[hogwarts\_beibei的博客](https://blog.csdn.net/hogwarts_beibei)

11-06
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
2781

[*Claude*推出的*Skills*功能将AI能力模块化，通过预装插件实现特定任务的快速执行。*Skills*包含说明书、脚本模板和资源文件，能按需加载完成Excel处理、PPT制作等标准化工作。与MCP（连接外部系统的协议）不同，*Skills*专注于任务执行，两者结合可形成"模块执行+系统联动"的解决方案。官方测试显示*Skills*使任务效率提升40%，错误率降低35%，12个开源示例已覆盖常见办公场景。该功能预演了AI工程化的未来趋势：从Prompt竞争转向模块化能力复用。](https://devpress.csdn.net/v1/article/detail/154398698)

[终于有人把 *Claude* *Skills* 的概念给我讲明白了！](https://devpress.csdn.net/v1/article/detail/156141949)

[悟鸣的技术博客](https://blog.csdn.net/w605283073)

12-22
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1713

[本文用相对通俗易懂的语言讲解一下 *Claude* 的 *Skills* 是什么，和 MCP 有什么区别，最核心的优势有哪些等等。](https://devpress.csdn.net/v1/article/detail/156141949)

[别再手动写代码了！*Claude* *Skills* 实战，让 AI 帮你干 80% 的活！

热门推荐](https://devpress.csdn.net/v1/article/detail/156983068)

[羑悻的博客.](https://blog.csdn.net/2401_82648291)

01-15
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1万+

[*Claude* *Skills* 是模块化的能力包，包含指令、元数据和可选资源（脚本、模板），让 *Claude* 在需要时自动加载和使用。](https://devpress.csdn.net/v1/article/detail/156983068)

[MCP 不香了，*Claude* Code 又推出了 *Skills*！！（保姆级安装和使用教程分享）](https://javastack.blog.csdn.net/article/details/154370363)

[Java技术栈，分享最主流的Java技术](https://blog.csdn.net/youanyyou)

11-03
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
7412

[在很多场景下，问题不是调用 API，而是按公司标准／流程来做事，MCP 可以访问数据或工具，但不会自动知道这个流程的外在规则是什么。*Skills* 是由模型驱动的，*Claude* 会根据你的任务和 Skill 的描述自动匹配并使用这些 *Skills*，完全不需要你介入。本文系公众号 "AI技术宅" 原创，转载、引用本文内容请注明出处，抄袭、洗稿一律投诉侵权，后果自负，并保留追究其法律责任的权利。而且，在它工作的过程中，你甚至能看到 *Skills* 在 *Claude* 的思考链里是怎么运作的。](https://javastack.blog.csdn.net/article/details/154370363)

[*Claude* *Skills*：不是更聪明，而是更“像专家”的 Agent 养成方法](https://aigctesthub.blog.csdn.net/article/details/156062823)

[测试者家园](https://blog.csdn.net/tony2yy)

12-19
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1039

[*Claude* *Skills* 不是在告诉 Agent“你能做什么”， 而是在约束它“你应该如何思考、如何判断、如何给结论”。](https://aigctesthub.blog.csdn.net/article/details/156062823)

[*Claude* *Skills* 深度讲解](https://blog.csdn.net/u013134676/article/details/156411813)

[u013134676的博客](https://blog.csdn.net/u013134676)

12-30
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1105

[阶段 1：Function Call（2023）├─ 大模型可以调用外部工具├─ 问题：缺乏对任务的深度理解└─ 局限：工具调用简单线性阶段 2：MCP 上下文工程（2024）├─ 大模型有了更丰富的上下文和工具├─ 问题：仍然需要手动编写复杂的 Prompt└─ 局限：每次对话都需要重新加载上下文阶段 3：*Claude* *Skills*（2025）├─ 大模型有了「能力模块」的概念├─ 可以动态加载、组合、执行专门的工作流├─ 真正实现了「知识的模块化和复用」](https://blog.csdn.net/u013134676/article/details/156411813)

[使用 *Claude* *Skills* 构建专业级 AI Agent：技术实践指南](https://blog.csdn.net/weixin_44058951/article/details/154070344)

[weixin\_44058951的博客](https://blog.csdn.net/weixin_44058951)

11-03
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1833

[*Claude* *Skills*（也称）是一组基于文件系统的可重用资源包，为 *Claude* 提供特定领域的专业知识、标准化工作流程和最佳实践。与传统一次性 Prompt 不同，*Skills* 是持久化、自动触发、支持代码执行的智能模块。让 AI 真正理解并执行你的工作方式。*Claude* *Skills* 正在重新定义 AI 助手的边界——从“回答问题”升级为“执行专业工作的能力”。其可组合、可移植、高效、强大的特性，使其成为自动化重复任务、标准化工作流、提升团队效率的理想工具。未来已来。](https://blog.csdn.net/weixin_44058951/article/details/154070344)

[拒绝单纯对话：用 *Claude* *Skills* 打造你的第一位“AI 数字员工”](https://goldenspider.blog.csdn.net/article/details/156447350)

[GoldenSpider.AI的博客](https://blog.csdn.net/NetGoldenSpider)

01-01
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1209

[*Claude*推出的*Skills*功能标志着AI交互方式的革新，将LLM从临时对话工具转变为可复用的"数字员工"。该功能通过封装专业知识和标准流程，解决了AI输出不稳定的痛点。用户可通过Markdown文件定义"技能包"，构建如文案审核专家等专业角色，实现工作流程的标准化和自动化。*Skills*与Projects的关键区别在于前者是持久性能力，后者是临时性任务。该功能预示了"SOP代码化"的平民化趋势，使业务人员能够将隐性知识转化为可执行的AI*程序*。未来](https://goldenspider.blog.csdn.net/article/details/156447350)

[MCP之后，*Claude*为何还要推出*Skills*？揭秘背后逻辑！](https://devpress.csdn.net/v1/article/detail/153879582)

[2401\_84204207的博客](https://blog.csdn.net/2401_84204207)

10-25
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1855

[看起来很强大，但跟 MCP 有啥区别？出这个是做啥的？
*Skills* 是什么？
要想知道区别，先知道是什么。
根据官方介绍，*Claude* 的 *Skills* 是一种模块化的能力包，它以文件夹的形式组织，
每个 Skill 包含：](https://devpress.csdn.net/v1/article/detail/153879582)

[*Claude* Agent *Skills* 深度解析：原理、工作流与最佳实践](https://devpress.csdn.net/v1/article/detail/156947700)

[lvaolan168的博客](https://blog.csdn.net/lvaolan168)

01-14
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
779

[*Claude* 现已引入 *Skills* 功能，显著提升了其执行特定任务的能力。*Skills* 本质上是一个包含指令、脚本和资源的结构化文件夹，*Claude* 能够根据任务需求动态加载这些资源。
这一机制的核心优势在于按需加载：*Claude* 仅在检测到当前任务与特定技能相关时才会调用该技能。这种设计不仅确保了 *Claude* 的运行效率，还能使其快速获取特定领域的专业知识，从而更高效地完成任务。](https://devpress.csdn.net/v1/article/detail/156947700)

[小白向：*Claude* *Skills* 是什么？教你写*Skills*，与小胡说技书的元提示词：一份自指循环的分析](https://h-y-c.blog.csdn.net/article/details/156789717)

[初始阶段。长文本博客做模型上下文。新书《千界明彻录》（故事形式构建元思维）——胡说小说。更多思辨内容在公众号。](https://blog.csdn.net/hyc010110)

01-10
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1175

[拆解*Claude*系统提示词，发现*Skills*机制的本质：任务型元提示词——告诉模型"面对X任务时如何行动"的封装。本文对比*Skills*与我的"锚点优先"元提示词框架，发现两者同构：都包含触发条件、核心流程、约束规则、质量标准。更有趣的是，我用自己的框架分析*Skills*，又用*Skills*原则优化自己的框架——形成自指循环。附录包含优化后的元提示词（*Skills*风格重构版）。](https://h-y-c.blog.csdn.net/article/details/156789717)

[别把*Claude*当玩具用了！*Claude* *Skills*深度指南：手把手教你打造“专家级”AI智能体！](https://devpress.csdn.net/v1/article/detail/156772819)

[m0\_59164520的博客](https://blog.csdn.net/m0_59164520)

01-09
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1125

[*Claude* Agent *Skills*(技能)是一种可复用的文件系统资源,为*Claude*提供特定领域的专业知识、工作流程和最佳实践。与传统的提示词不同,*Skills*可以按需加载,无需在每次对话中重复提供相同的指导。](https://devpress.csdn.net/v1/article/detail/156772819)

[*Claude* Code教程（五）| *Claude* Code *Skills* 完全指南](https://blog.csdn.net/qq_20236937/article/details/156824407)

[qq\_20236937的博客](https://blog.csdn.net/qq_20236937)

01-11
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
2086

[*Claude* Code教程（五）| *Claude* Code *Skills* 完全指南](https://blog.csdn.net/qq_20236937/article/details/156824407)

[*Claude* *Skills*技能包详解：大模型Agentic能力的最佳实践与产品启示！](https://devpress.csdn.net/v1/article/detail/154398571)

[2401\_84494441的博客](https://blog.csdn.net/2401_84494441)

11-04
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1221

[文章解析了*Claude* *Skills*功能如何代表大模型开发范式的转变，从AI工具化到AI主导化。*Skills*通过元数据、正式说明文档及资源包(references、scripts、assets)为AI提供工具支持，成为Agentic能力的最小可行性实现。作者详细介绍了11组技能模板及其应用场景，强调产品经理和开发者掌握这些技能是理解AI产品开发的关键，值得深入学习研究。](https://devpress.csdn.net/v1/article/detail/154398571)

[gemini 整合*Claude* *Skills*](https://wenku.csdn.net/answer/824wog4hfe)

01-16

[目前并没有公开的通用标准方法来直接将Gemini与*Claude* *Skills*进行整合，不过可以从技术层面提供一些通用思路。 从技术架构角度来看，首先可以考虑使用API接口进行整合。Gemini和*Claude*通常都提供了API供开发者调用...](https://wenku.csdn.net/answer/824wog4hfe)

评论
![](https://csdnimg.cn/release/blogv2/dist/pc/img/closeBt.png)

![](https://csdnimg.cn/release/blogv2/dist/pc/img/commentArrowLeftWhite.png)被折叠的  条评论
[为什么被折叠?](https://blogdev.blog.csdn.net/article/details/122245662)
[![](https://csdnimg.cn/release/blogv2/dist/pc/img/iconPark.png)到【灌水乐园】发言](https://bbs.csdn.net/forums/FreeZone)

查看更多评论![](https://csdnimg.cn/release/blogv2/dist/pc/img/commentArrowDownWhite.png)

添加红包

祝福语

请填写红包祝福语或标题

红包数量

个

红包个数最小为10个

红包总金额

元

红包金额最低5元

余额支付

当前余额3.43元
[前往充值 >](https://i.csdn.net/#/wallet/balance/recharge)

需支付：10.00元

取消
确定

![](https://csdnimg.cn/release/blogv2/dist/pc/img/guideRedReward02.png)
下一步

![](https://csdnimg.cn/release/blogv2/dist/pc/img/guideRedReward03.png)
知道了

实付元

[使用余额支付](javascript:;)

![](https://csdnimg.cn/release/blogv2/dist/pc/img/pay-time-out.png)
点击重新获取

![](https://csdnimg.cn/release/blogv2/dist/pc/img/weixin.png)![](https://csdnimg.cn/release/blogv2/dist/pc/img/zhifubao.png)![](https://csdnimg.cn/release/blogv2/dist/pc/img/jingdong.png)扫码支付

钱包余额
0

![](https://csdnimg.cn/release/blogv2/dist/pc/img/pay-help.png)

抵扣说明：

1.余额是钱包充值的虚拟货币，按照1:1的比例进行支付金额的抵扣。  
 2.余额无法直接购买下载，可以购买VIP、付费专栏及课程。

[![](https://csdnimg.cn/release/blogv2/dist/pc/img/recharge.png)余额充值](https://i.csdn.net/#/wallet/balance/recharge)

![]()