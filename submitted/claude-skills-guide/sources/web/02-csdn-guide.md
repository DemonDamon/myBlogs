# 2026年最火的 AI 新功能——Claude Skills到底是什么？-CSDN博客

**来源**: [https://blog.csdn.net/ChailangCompany/article/details/157517138](https://blog.csdn.net/ChailangCompany/article/details/157517138)
**爬取时间**: 2026年 2月15日 星期日 15时35分39秒 CST

 















2026年最火的 AI 新功能——Claude Skills到底是什么？-CSDN博客





# 2026年最火的 AI 新功能——Claude Skills到底是什么？

最新推荐文章于 2026-02-12 17:56:40 发布

原创
最新推荐文章于 2026-02-12 17:56:40 发布
·
1k 阅读

·
![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Active.png)
![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Black.png)

36

·
![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollect2.png)
![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollectionActive2.png)

22
·

CC 4.0 BY-SA版权

版权声明：本文为博主原创文章，遵循 [CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/) 版权协议，转载请附上原文出处链接和本声明。

文章标签：

[#人工智能](https://so.csdn.net/so/search/s.do?q=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)

[![](https://i-blog.csdnimg.cn/columns/default/20201014180756918.png?x-oss-process=image/resize,m_fixed,h_224,w_224)


笔记
专栏收录该内容](https://blog.csdn.net/chailangcompany/category_9725506.html "笔记")

1055 篇文章

订阅专栏

#### 🌟 一句话总结：

**Claude Skills 就是给 AI（比如 Claude）发一本“岗位操作手册”，让它记住你希望它怎么干活，以后不用你每次都重复教。**

---

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/213162c250044c7aac584c0363afc486.jpeg#pic_center)

#### 🤔 以前的问题：AI 总是“健忘”

想象一下你让 AI 帮你写一篇小红书文案：

* 第一次你说：“语气要活泼一点，带点 emoji，结尾加个话题标签。”
* 第二次你又说：“记得用公司品牌色 #FF6B6B，开头要有钩子。”
* 第三次……你又要重复一遍！

因为 AI 每次聊天都是“临时记忆”，关掉窗口就全忘了。就像每次雇一个新员工，都要手把手再教一遍，特别累。

---

#### ✅ 现在有了 Claude Skills：AI 终于“长记性”了！

你只需要做一次：

1. **写一份“操作指南”**（其实就是一个普通文件，像 Word 文档一样）
2. **告诉 AI：以后写小红书文案，就按这个标准来**
3. 保存好这个文件（叫 Skill）

之后你只要说一句：

> “用我的‘小红书文案’技能帮我写一篇关于咖啡的笔记。”

AI 就会自动翻出那本“手册”，按你的风格、格式、语气、要求，**一次性写出符合你心意的内容**，再也不用你啰嗦！

---

#### 📁 Skill 长什么样？（超简单！）

一个 Skill 其实就是一个文件夹，里面至少有一个叫 `skill.md` 的文件，内容可能像这样：

```
# 小红书文案助手

## 描述
专门用于生成符合品牌调性的社交媒体文案。

## 使用规则
- 语气：轻松、亲切，像跟闺蜜聊天
- 开头要有“痛点”或“反差”
- 结尾加 2~3 个相关话题标签
- 必须包含 emoji（每段至少1个）
- 品牌色：#FF6B6B（仅用于视觉设计参考）
```

你甚至可以加上模板、例子、或者自动检查脚本（高级用法），但**基础版就是写清楚“怎么做”就行**。

---

#### 💡 它能干啥？举几个真实例子：

| 场景 | 以前 | 用了 Skills 后 |
| --- | --- | --- |
| 写周报 | 每次都要说格式、重点、字数 | 一键调用“周报技能”，自动生成 |
| 审查代码 | 每次粘贴公司编码规范 | AI 自动按规范检查，还能跑脚本验证 |
| 做数据分析 | 手动导出 Excel、写公式 | AI 直接连数据库，按模板出报告 |
| 写公众号 | 反复强调“别太正式，要口语化” | AI 自动用你的专属文风 |

---

#### ❓普通人能用吗？要编程吗？

**完全不需要！**

* 你会写 Word 或微信消息，就能写 Skill。
* 在 [claude.ai](https://claude.ai) 网页上，通过“项目（Projects）”功能上传文档就行。
* Anthropic（Claude 的公司）还提供了很多现成的 Skill 模板，直接下载改一改就能用。

---

#### 🔒 安全吗？

Skill 文件是你自己控制的，可以存在本地或私有项目里。  
 ⚠️ 但如果你用别人写的 Skill（尤其是带脚本的），要小心——**别随便运行来历不明的代码**，就像不随便点陌生链接一样。

---

#### ✅ 总结：Claude Skills 是什么？

| 类比 | 说明 |
| --- | --- |
| 👨‍💼 新员工 | AI 本来啥都会一点，但不专业 |
| 📚 岗位手册 | Skill 就是这本手册 |
| 🧠 肌肉记忆 | AI 学会后，自动按你的流程做事 |
| 🛠️ 数字员工 | 你定制的 AI 专家，7x24 小时待命 |

---

#### 🚀 行动建议：

1. 去 [claude.ai](https://claude.ai) 注册账号（免费可用）
2. 创建一个“项目”
3. 上传你的工作模板/规范（比如“会议纪要模板.txt”）
4. 下次直接说：“按我的会议纪要技能整理今天的讨论”

你会发现：**AI 终于真正“懂你”了。**

---

如果你是学生、运营、HR、自媒体、程序员……**现在就是把重复劳动交给 AI 的最好时机**。  
 Claude Skills 不是炫技，而是**让你少加班、少返工、效率翻倍的实用工具**。

试试看，你会回来感谢自己的 😊

---

Claude Skills 是 Anthropic 为 Claude AI 推出的一项强大功能，它的核心目标是：**将通用 AI 转化为你专属的、可复用的“领域专家”**。它不只是提示词（prompt）的升级版，而是一套完整的、模块化的“AI 工作流封装系统”。

以下是 **Claude Skills 的具体功能详解**，按类别清晰拆解：

---

#### 🧩 一、基础功能：指令与流程标准化

1. **自定义操作指南（Custom Instructions）**

   * 将你的工作规范、语气风格、输出格式等写入 `skill.md` 文件。
   * 示例：品牌文案需用特定口号、禁用某些词汇、必须包含数据来源等。
2. **重复任务自动化**

   * 把高频重复任务（如周报、会议纪要、代码审查）打包成 Skill。
   * 写一次，永久复用，无需每次重复说明。
3. **渐进式披露（Progressive Disclosure）**

   * **第一层**：只加载技能名称和简短描述（约 50–100 tokens）。
   * **第二层**：当任务匹配时，才加载详细指令（如 Markdown 正文）。
   * **第三层**：仅在需要时读取 `references/` 或 `scripts/` 中的资源。
   * ✅ **极大节省 token，避免上下文爆炸**。

---

#### ⚙️ 二、高级能力：代码执行与工具集成

4. **嵌入可执行脚本（Code Execution）**

   * 在 Skill 中包含 Python、TypeScript 等脚本。
   * AI 可直接运行脚本处理文件、调用 API、生成图表等。
   * 示例：
     + 自动解析 PDF 发票 → 提取金额、税号、分类汇总。
     + 读取 Excel → 生成可视化折线图并保存为 PNG。
5. **确定性任务交由代码处理**

   * 对于“规则明确”的任务（如格式校验、数据清洗），让脚本执行比让 AI “猜”更可靠。
   * 避免 AI 幻觉（hallucination）导致错误。
6. **工具权限控制**

   * 每个 Skill 可独立声明所需权限（如“允许读取当前目录文件”、“允许网络请求”）。
   * 安全隔离，避免一个 Skill 影响全局。

---

#### 📂 三、结构化组织：模块化与可维护性

7. **标准目录结构**

   ```
   my-skill/
   ├── SKILL.md          # 核心指令（必需）
   ├── scripts/          # 可执行脚本（如 analyze.py）
   ├── references/       # 分析方法论、行业指南等参考资料
   └── assets/           # 模板文件（如 report_template.docx）
   ```
8. **支持多文件协作**

   * 复杂 Skill 可拆分为多个文档，按需引用。
   * 例如：“当用户需求模糊时，加载 `guide_for_vague_requests.md`”。
9. **版本控制友好**

   * 整个 Skill 是普通文件夹，可直接放入 Git 仓库。
   * 团队协作、变更追踪、回滚历史全部支持。

---

#### 🌐 四、平台与集成能力

10. **跨平台使用**

    * **Claude Web（网页版）**：Pro/Team 用户可在 Projects 中上传使用。
    * **Claude API**：开发者可将 Skill 集成到自有应用中。
    * **Claude Code（本地 IDE）**：把 Skill 放入 `~/.claude/skills/` 即可自动识别。
11. **团队共享**

    * 项目级 Skill 存放在 `.claude/skills/`，所有成员可用。
    * 统一团队输出标准（如代码风格、文档模板）。
12. **与外部系统联动（配合 MCP 使用）**

    * 虽然 Skill 本身不直接访问数据库，但可与 **MCP（Model Context Protocol）** 配合：
      + MCP 负责“获取数据”（如查销售数据库），
      + Skill 负责“处理数据”（如按模板生成周报）。

---

#### 🎯 五、典型应用场景（真实案例）

| 场景 | Skill 功能体现 |
| --- | --- |
| **品牌一致性管理** | 自动应用公司字体、色值、语气、禁用词 |
| **财务自动化** | 日本乐天用 Skill 自动生成合规财报，效率提升 10 倍 |
| **发票识别助手** | 扫描 PDF 发票 → 提取信息 → 分类汇总 → 输出报销清单 |
| **数据分析大师** | 加载多格式数据 → 挖掘洞察 → 生成可视化报告 + 执行建议 |
| **新人培训包** | 把老员工经验写成 Skill，新人提问即得标准答案 |
| **代码审查机器人** | 自动检查 PR 是否符合团队规范，运行 lint 脚本 |

---

#### 🔒 六、安全与管理

13. **沙箱执行环境**

    * 脚本运行在受限环境中，无法随意访问系统敏感文件（除非显式授权）。
14. **用户可控**

    * 你完全掌控哪些 Skill 被启用。
    * **强烈建议：只使用自己创建或官方认证的 Skill**，避免恶意代码。

---

#### ✅ 总结：Claude Skills 的核心功能矩阵

| 功能维度 | 具体能力 |
| --- | --- |
| **智能增强** | 自定义指令、上下文感知、自动触发 |
| **效率提升** | 减少重复输入、降低 token 消耗、加速输出 |
| **可靠性** | 脚本执行确定性任务、减少 AI 幻觉 |
| **可维护性** | 模块化、Git 友好、团队共享 |
| **扩展性** | 支持脚本、多语言、API 集成 |
| **安全性** | 权限控制、沙箱执行、用户审核 |

---

> 💡 **一句话记住**：  
>  **Claude Skills = 你的 SOP（标准作业程序） × AI 执行力 × 自动化流水线**

![](https://csdnimg.cn/release/blogv2/dist/pc/img/vip-limited-close-newWhite.png)

确定要放弃本次机会？

福利倒计时

*:*

*:*

![](https://csdnimg.cn/release/blogv2/dist/pc/img/vip-limited-close-roup.png)
立减 ¥

普通VIP年卡可用

[立即使用](https://mall.csdn.net/vip)

[![](https://profile-avatar.csdnimg.cn/3d59418d823a4210acfc2ef8dd7db3de_chailangcompany.jpg!1)

向上的车轮](https://blog.csdn.net/ChailangCompany)

[关注](javascript:;)
关注

* ![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarThumbUpactive.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/like-active.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/like.png)

  36

  点赞
* ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/unlike-active.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/unlike.png)

  踩
* [![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/collect-active.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/collect.png)
  ![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCollectActive.png)

  22](javascript:;)

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

专栏目录

![]()

[【光子*AI* *2026* 企业级 Agent 架构指南】别再把 Skill 当 Tool：Agent *Skills* × MCP 企业级落地全指南（*最*新定义澄清 + 场景大全 + 选型决策树+安全工程清单）](https://dreamit.blog.csdn.net/article/details/156699459)

01-08
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
790

[摘要： *2026**年*企业级*AI*架构迎来两大核心标准——Agent *Skills*与MCP（Model Context Protocol），分别解决流程标准化与系统集成难题。Agent *Skills*通过“文件夹化能力包”（SOP+脚本+模板）固化专家流程，确保输出一致性；MCP则以类USB-C的协议统一外部系统接入，降低集成成本。两者差异显著：*Skills*专注程序性知识（如财报生成），MCP侧重动态连接（如跨平台数据调用）。实际场景中，复杂需求（如智能客服）需组合使用——MCP为骨架提供连接能力，*Skills*为大](https://dreamit.blog.csdn.net/article/details/156699459)

参与评论
您还未登录，请先
登录
后发表或查看评论

[OpenClaw 全球*最**火*的*AI*助手，到底是什么神仙？

最新发布](https://zhanghaiyang.blog.csdn.net/article/details/158010663)

[科技D人生](https://blog.csdn.net/u012562943)

02-12
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
32

[去*年*11月，老哥只是想写个小工具，把WhatsApp的消息转发给*AI*处理一下，结果越写越欢，一不小心写成了一个完整的*AI*自主智能体。整个流程就是：你通过“菜单”（飞书/微信）下单 → “前台”（Gateway）接单 → “大厨”（Agent）分析要做什么 → 拿起“工具”（*Skills*）动手干活 → 干完了通过“菜单”告诉你。你说“帮我给老板发个邮件”，它就发了。举个“翻车”案例：有人给OpenClaw一个含糊的指令“保护环境”，结果这个*AI*助手“努力过头”，直接修改了服务器的防*火*墙规则，](https://zhanghaiyang.blog.csdn.net/article/details/158010663)

[*Claude* Code *Skills* 入门：什么是 *Skills*，为什么你需要它](https://devpress.csdn.net/v1/article/detail/157095354)

[徐公，微信公众号同名](https://blog.csdn.net/gdutxiaoxu)

01-18
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
748

[*Claude* Code *Skills* 是一项革命性功能，它通过技能文件夹(SKILL.md)让*AI*记住并复用特定指令和规范。相比传统提示词，*Skills*具有三大优势：1)持久化存储，避免重复输入；2)渐进式加载机制，优化token使用；3)团队协作友好，便于知识沉淀。典型应用场景包括代码规范统一、PRD文档生成和团队知识管理，能显著提升工作效率50-70%。*Skills*采用三级加载机制(元数据→主体内容→参考资源)，实现按需调用，是*AI*协作领域的重大创新。](https://devpress.csdn.net/v1/article/detail/157095354)

[LLM - *Claude* Code *Skills* 实战指南：用模块化“技能包”重构*AI* 开发工作流](https://devpress.csdn.net/v1/article/detail/156808179)

[小工匠](https://blog.csdn.net/yangshangwei)

01-10
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
2491

[摘要：*AI*工程化新范式——*Claude* Code *Skills*机制解析 本文系统阐述了*Claude* Code推出的*Skills*机制，这是*AI*工程化领域的重要创新。随着大模型能力提升，团队差异已从"模型智能度"转向"*AI*工作流集成能力"。*Skills*机制通过将*AI*能力拆解为可组合、可复用的"技能包"，解决了传统Prompt方法存在的上下文冗余、行为不可预测等问题。文章详细分析了*Skills*的三层架构（元数据、指令层、资源层）和自动激活机制，并与Hoo](https://devpress.csdn.net/v1/article/detail/156808179)

[猫头虎*AI*分享10个全网超*火*的*Skills*开源仓库：*Claude* *Skills*开源库必装精选 & 安装配置实战指南](https://libin9ioak.blog.csdn.net/article/details/156400303)

[猫头虎技术团队：授渔优于赠鱼，兴趣引领智慧，探索之乐尤显珍贵。商务合作+：Libin9iOak ，万粉变现+：CSDNWF，猫头虎承诺每年免费为100名C站创作者做账号流量诊断服务！全网搜：猫头虎技术团队，点击文章底部名片或直接私信我一切皆可谈，快找虎哥！](https://blog.csdn.net/qq_44866828)

12-29
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1万+

[本文精选10个高星（500+）、高活跃的*Claude* *Skills*开源仓库，涵盖编码、科研、自动化等场景。核心推荐包括：obra/superpowers（5.7k星工程化技能库）、ComposioHQ的Awesome清单（12.5k星全领域技能）、K-Dense-*AI*科研工具集（2.4k星），以及Skill\_Seekers（5.7k星文档转技能工具）。作者猫头虎作为*AI*全栈工程师，详解各仓库适用场景与上手方法，助力开发者提升*AI*生产力。适合*Claude*中级以上用户构建自动化工作流或垂直领域](https://libin9ioak.blog.csdn.net/article/details/156400303)

[拒绝“*AI*废话”：深度解析*Claude* *Skills*实战逻辑与生产力进阶](https://goldenspider.blog.csdn.net/article/details/157126460)

[GoldenSpider.AI的博客](https://blog.csdn.net/NetGoldenSpider)

01-21
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
696

[*Claude* *Skills*功能深度评测：从*AI*废话到专业生产力工具 摘要：本文深入解析*Claude**最*新推出的*Skills*功能，揭示其与Projects的本质区别：Projects是静态知识库，而*Skills*是通用的专业能力模版。通过实战案例展示如何构建"反*AI*味"写作引擎，包括定义触发词、建立负面清单和格式规范。文章特别强调了一个关键配置技巧——在Custom Instructions中添加强制检查指令，以解决技能触发不可靠的问题。分析指出，*Skills*代表着*AI*交互从"提示词](https://goldenspider.blog.csdn.net/article/details/157126460)

[Vibe Coding氛围编程系列｜Anthropic *Claude*官方开源的16个*Skills*技能库：哪些*最*值得体验？如何安装配置使用*skills*库？](https://devpress.csdn.net/v1/article/detail/156400175)

[猫头虎技术团队：授渔优于赠鱼，兴趣引领智慧，探索之乐尤显珍贵。商务合作+：Libin9iOak ，万粉变现+：CSDNWF，猫头虎承诺每年免费为100名C站创作者做账号流量诊断服务！全网搜：猫头虎技术团队，点击文章底部名片或直接私信我一切皆可谈，快找虎哥！](https://blog.csdn.net/qq_44866828)

12-29
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
9725

[摘要： Anthropic *Claude*官方开源了16个*Skills*技能库，涵盖文档处理、创意开发等场景，安装仅需两条命令。重点推荐PDF处理（自动提取/合并文档）、skill-creator（自定义插件开发）和webapp-testing（网页测试）等核心功能。*Skills*无需手动调用，*Claude*会根据需求自动匹配，实现高效*AI*结对编程。通过Vibe Coding（氛围编程）理念，用户可专注规划，由*AI*执行模块化任务，避免代码失控。实测表明，这些*Skills*是目前开箱即用度*最*高的*AI* Agent技能库。](https://devpress.csdn.net/v1/article/detail/156400175)

[我的*2026**年*目标与计划——*AI*短剧/漫剧、自动化、文创](https://devpress.csdn.net/v1/article/detail/156573746)

[u014177256的博客](https://blog.csdn.net/u014177256)

01-04
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1252

[《*2026*：成为*AI*时代的系统化创作者》摘要：在*AI*普及化的未来，单纯掌握工具已不再是核心竞争力。本文提出创作者需构建三层价值体系：内容生产（短剧/漫剧创作）、系统建设（自动化工具开发）和品牌变现（文创产品验证）。核心在于培养四大能力：选题力（趋势洞察）、创作力（质量把控）、系统力（流程优化）和商业力（变现路径）。通过分阶段实施计划（1-2月工具掌握，3-4月系统搭建，5-6月商业验证），*最*终实现从执行者到"创作系统设计师"的转型，在内容民主化时代建立不可替代的竞争优势。](https://devpress.csdn.net/v1/article/detail/156573746)

[*2026**年**AI*圈爆*火*产品全解析：这些前沿应用为何引发行业热潮？](https://devpress.csdn.net/v1/article/detail/157944558)

[2501\_92406411的博客](https://blog.csdn.net/2501_92406411)

02-10
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
575

[Radar*AI*是一款聚焦“信息聚合+*AI*洞察+自动化推送”的平台，核心功能包括：聚合BestBlogs *AI*分类文章、GitHub Trending项目、*Claude*等技能库更新；通过通义千问API生成“应用端爆点”“机会方向”等结构化洞察；支持每8小时自动生成简报并推送至企微群、用户Webhook等渠道。优势多源数据整合能力强（覆盖博客、GitHub、技能库），信息覆盖面广；*AI*洞察功能基于Qwen API，能从海量内容中提取可落地的趋势与机会，辅助决策；](https://devpress.csdn.net/v1/article/detail/157944558)

[*2026* *AI* 新风口：告别 Prompt Engineering，Agent *Skills* 才是智能体的“杀手级”进化](https://devpress.csdn.net/v1/article/detail/156950017)

[gujiachun的专栏](https://blog.csdn.net/gujiachun)

01-14
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
726

[Agent *Skills*正在重塑*AI*与外部世界的交互方式，从静态的工具调用升级为动态的技能封装。](https://devpress.csdn.net/v1/article/detail/156950017)

[*2026**年*1月6日-用了这31招*Claude* Code直接起飞](https://devpress.csdn.net/v1/article/detail/156657279)

[个人技术](https://blog.csdn.net/wwwzhouhui)

01-06
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
940

[摘要 *Claude* Code是一款革命性的*AI*编程工具，通过命令行终端形式提供全栈开发支持。它具备超强代码理解能力、持久记忆和并行处理等核心特性，支持200K tokens的上下文窗口。本文分享了31个实用技巧，包括项目初始化方法、快捷键操作、会话管理技巧和生产力功能等。例如使用/init命令生成项目文档，通过!前缀快速执行bash命令，利用Ctrl+R反向搜索历史提示等。这些技巧能显著提升开发效率，使*Claude* Code成为开发者强有力的*AI*助手。](https://devpress.csdn.net/v1/article/detail/156657279)

[一文弄懂：MCP·提示词·Skill·智能体，到底有什么关系和区别？](https://blog.csdn.net/lovehu6686/article/details/157940261)

[lovehu6686的博客](https://blog.csdn.net/lovehu6686)

02-11
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
453

[摘要：掌握*AI*高效协作的四个关键要素——提示词、Skill、MCP和智能体，才能发挥*AI*的真正价值。提示词是精准指令，Skill是可复用的专业知识包，MCP让*AI*连接外部工具，智能体则像项目经理一样自主完成任务。这四者协同工作，形成*AI*应用的四级进化路径：从基础提示词到*最*终实现自主交付的智能体。*2026**年*智能体已进入规模化落地阶段，*AI*超级个体的能力取决于对这些要素的系统性运用。认知差距而非技术差距，决定了*AI*应用效果的差异。（149字）](https://blog.csdn.net/lovehu6686/article/details/157940261)

[OpenWork 开源版 *Claude* Cowork 深度解析：从原理到实战，手把手教你搭建本地*AI*协作系统](https://blog.csdn.net/lintser/article/details/157094892)

[lintser的博客](https://blog.csdn.net/lintser)

01-18
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1649

[OpenWork横空出世，成为开源、可扩展的*Claude* Cowork替代品。它基于OpenCode引擎，提供可视化执行计划、权限审批和技能扩展，支持本地运行与多模型，兼顾隐私与成本。本文深度解析其技术架构、安装部署、实战案例，并与*Claude* Cowork进行全面对比，助你打造专属*AI*数字同事。](https://blog.csdn.net/lintser/article/details/157094892)

[IoT、IIoT、*AI*oT的区别是什么？

热门推荐](https://blog.csdn.net/ChailangCompany/article/details/138021409)

[软件行业技术文化交流。](https://blog.csdn.net/ChailangCompany)

04-21
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1万+

[综上所述，IoT、IIoT和*AI*oT的发展趋势将表现为连接性和智能化的提升、多样化应用场景的拓展、边缘计算和*人工智能*的推动、安全和隐私保护的加强以及开放和标准化的平台发展。：随着物联网技术的不断发展，物联网设备之间的连接性将变得更加强大和稳定，设备将能够无缝地连接到互联网，实现实时的数据传输和交互。随着5G通信技术的发展，物联网的应用将更加广泛和深入。总的来说，IoT是物联网的泛称，IIoT是物联网在工业领域的应用，而*AI*oT则是物联网和*人工智能*技术的结合，强调通过*人工智能*技术实现数据的智能化处理和应用。](https://blog.csdn.net/ChailangCompany/article/details/138021409)

[网络安全等级保护2.0（等保2.0）全面解析](https://blog.csdn.net/ChailangCompany/article/details/140096609)

[软件行业技术文化交流。](https://blog.csdn.net/ChailangCompany)

07-01
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1万+

[网络安全等级保护2.0（简称“等保2.0”）是我国网络安全领域的基本制度、基本策略、基本方法。它是在《中华人民共和国网络安全法》指导下，对我国网络安全等级保护制度进行的重大升级。等保2.0的发布与实施，旨在全面强化我国网络安全保障能力，提升网络安全防护水平，确保关键信息基础设施和重要信息系统的稳定运行。](https://blog.csdn.net/ChailangCompany/article/details/140096609)

[如何有效管理项目团队，提高团队凝聚力和执行力？](https://blog.csdn.net/ChailangCompany/article/details/138283585)

[软件行业技术文化交流。](https://blog.csdn.net/ChailangCompany)

04-29
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1万+

[通过明确目标与分工、建立良好的沟通机制、培养团队信任与合作、激励与认可团队成员、定期回顾与调整策略、促进团队学习与成长、解决冲突与增进团结以及打造高效团队文化，项目经理可以带领团队走向成功。清晰的目标和分工可以为团队提供一个共同的方向和框架，让每个成员都明白自己的角色和重要性。项目经理应定期回顾项目的进展和团队的表现，及时调整策略，确保团队始终朝着目标前进。通过不断提升团队成员的能力和知识水平，提高团队整体的竞争力。：根据项目进度和需要，定期召开团队会议，让每个人报告自己的工作进展、遇到的问题和需求。](https://blog.csdn.net/ChailangCompany/article/details/138283585)

[目前主流的CPU有哪些？选择依据有哪些？](https://blog.csdn.net/ChailangCompany/article/details/148684241)

[软件行业技术文化交流。](https://blog.csdn.net/ChailangCompany)

06-16
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
1万+

[Intel与AMD作为两大CPU厂商，在2025*年*市场各具优势。Intel酷睿系列（i3/i5/i7/i9）以高频单核性能见长，适合游戏和*AI*应用；AMD锐龙系列（Ryzen 3/5/7/9）凭借Zen架构和多核性价比，在内容创作领域领先。](https://blog.csdn.net/ChailangCompany/article/details/148684241)

[什么是曼哈顿计划？什么是*AI*的曼哈顿计划？](https://blog.csdn.net/ChailangCompany/article/details/144924539)

[软件行业技术文化交流。](https://blog.csdn.net/ChailangCompany)

01-05
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
9922

[高峰时期参加者人数逾10万人，在整个“曼哈顿工程区”工作的15万人当中，只有12个人知道全盘的计划，全体人员中很少有人知道他们是在从事制造原子弹的工作。格罗夫斯同意成为洛斯阿拉莫斯名义上的管理单位和合同保证单位，基地的军队负责实验室建设、后勤供应和安全保障，以保证实验室内部的自由学术讨论。*AI*的曼哈顿计划是由美中经济与安全评估委员会（USCC）在2024*年*度报告中提出的一个类似于二战期间“曼哈顿计划”的*人工智能*研发项目，旨在加速实现通用*人工智能*（AGI）的能力。](https://blog.csdn.net/ChailangCompany/article/details/144924539)

[什么是计算机化系统验证CSV？](https://devpress.csdn.net/v1/article/detail/138046096)

[软件行业技术文化交流。](https://blog.csdn.net/ChailangCompany)

04-23
![](https://csdnimg.cn/release/blogv2/dist/pc/img/readCountWhite.png)
9859

[计算机化系统验证（CSV）是确保计算机化系统能够稳定并持续地执行既定功能的一系列保障措施和过程。通常应用于制药、医疗设备、生物技术等受监管行业，主要目的是保证系统的可靠性、一致性和完整性，以保护产品质量、数据完整性和患者安全。质量工程原则：CSV需要建立文件来证明系统的开发和实施符合质量工程的原则，满足用户需求，并能够长期稳定工作。系统生命周期管理：涉及从提出用户需求到终止使用的过程，包括设计、设定标准、编程、测试、安装、运行和维护等阶段。数据审计跟踪。](https://devpress.csdn.net/v1/article/detail/138046096)

[*Claude* 的 *Skills* 功能到底怎么用？网页版、桌面端和 Cursor 各自支持哪些操作？](https://wenku.csdn.net/answer/67ghf3de1mgz)

02-05

[*Claude* *Skills* 是 Anthropic 提供的模块化、可复用的 *AI* 助手能力封装机制，用于将特定任务（如代码审查、NL2SQL、API 文档生成）固化为具备元数据描述、执行逻辑与资源约束的标准化单元。其本质并非传统插件，而是基于 \*\*渐进式披露（Progressive Disclosure）\*\* 架构的上下文增强协议，依赖 SKILL.md 元数据文件、可执行脚本（Python/Shell）、资源文件（如 schema.json、prompt.txt）三要素构成[ref\_5]。
*Skills* 的安装与使用路径取决于目标客户端：
---
### ✅ 网页版 *Claude*（*claude*.*ai*）
仅支持官方预置 *Skills*（如 “Code Review”、“Expl*ai*n Code”），用户\*\*无法自行安装第三方或自定义 *Skills*\*\*。Anthropic 未开放网页端的 *Skills* 注册接口或上传入口，所有可用 *Skills* 均由 Anthropic 官方审核并内置分发[ref\_2]。
---
### ✅ *Claude* Code（独立桌面应用）
支持通过 `*skills*` 目录手动注册本地 *Skills*，需满足以下结构：
```text
~/.anthropic/*claude*-code/*skills*/my-review-skill/
├── SKILL.md # 必需：YAML frontmatter + Markdown 描述
├── run.py # 可选：Python 执行逻辑（需符合 Anthropic CLI 协议）
└── resources/ # 可选：schema.json, rules.json 等上下文资源
```
`SKILL.md` 示例：
```markdown
---
name: "Code Review Assistant"
description: "Performs static analysis and best practice feedback on Python code snippets."
trigger: ["review this code", "check for bugs", "is this secure*?*"]
input\_schema:
language: "python"
max\_lines: 200
output\_contract:
format: "markdown"
sections: ["issues", "suggestions", "severity\_rating"]
---
```
> 注意：*Claude* Code v1.3+ 要求 *Skills* 必须签名且通过 `*claude*-code-cli validate-skill` 校验；未经签名的 *Skills* 默认被拒绝加载[ref\_2]。
---
### ✅ Cursor IDE（基于 VS Code）
通过 Open*Skills* 工具链集成 *Skills*，流程如下：
1. 安装 Open*Skills* CLI：
```bash
npm install -g open*skills*-cli
```
2. 同步远程 *Skills* 仓库（如官方技能集）：
```bash
open*skills* sync https://github.com/anthropic/*claude*-*skills*-public
```
3. 在 Cursor 设置中启用 *Skills*：
```json
// cursor/settings.json
{
"*claude*.*skills*.enabled": true,
"*claude*.*skills*.paths": ["~/.open*skills*/*skills*"]
}
```
4. 在编辑器中通过 `/*skills*` 命令调用，或在自然语言请求中触发（如：“用 SQL 生成器帮我写查询”）[ref\_3]。
---
### ⚠️ 安全与合规约束
- 所有 *Skills* 在执行前必须通过沙箱环境校验：禁止 `os.system()`、`subprocess.Popen`（无限制）、网络请求（除非显式声明 `requires\_network: true` 并经用户授权）[ref\_4]。
- 自定义 *Skills* 的 `run.py` 必须实现 `execute(input: dict) -> dict` 接口，返回结构需严格匹配 `output\_contract` 中定义的 schema[ref\_5]。
- 企业部署需启用 `--enforce-skill-signing` 启动参数，拒绝未使用 Anthropic 私钥签名的 *Skills* 加载[ref\_2]。
---
| 维度 | 网页版 *claude*.*ai* | *Claude* Code | Cursor IDE |
|------|------------------|-------------|------------|
| 自定义 *Skills* 支持 | ❌ 不支持 | ✅ 本地文件系统注册 | ✅ 通过 Open*Skills* 同步 |
| 技能执行权限 | 仅限官方白名单 | 沙箱内 Python 执行 | 沙箱内 Shell/Python 执行 |
| 元数据标准 | 不可见 | `SKILL.md` YAML frontmatter | 兼容 `SKILL.md` + Open*Skills* 扩展字段 |
| 签名强制要求 | N/A | ✅ 强制签名验证 | ✅ 依赖 Open*Skills* 签名策略 |
*Skills* 的核心价值在于将重复性高、规则明确、输入输出契约清晰的开发任务（如 PR 描述生成、单元测试补全、合规性检查）转化为可版本化、可测试、可审计的软件资产，而非泛化 Prompt 工程[ref\_5]。](https://wenku.csdn.net/answer/67ghf3de1mgz)

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