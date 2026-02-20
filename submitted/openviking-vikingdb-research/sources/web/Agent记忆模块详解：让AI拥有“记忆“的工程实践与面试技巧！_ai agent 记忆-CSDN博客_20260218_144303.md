# Agent记忆模块详解：让AI拥有“记忆“的工程实践与面试技巧！_ai agent 记忆-CSDN博客

原文链接: https://blog.csdn.net/m0_63171455/article/details/154843125

# Agent记忆模块详解：让AI拥有“记忆“的工程实践与面试技巧！

最新推荐文章于 2025-11-26 00:00:00 发布

原创
最新推荐文章于 2025-11-26 00:00:00 发布
·
1.4k 阅读

·
![](images/0b22a680d8caf61b3fc4d6ce595a5a36.png)
![](images/5e06ae5b64a61915c89019db36be22b5.png)

44

·
![](images/169ac251df55845562af7f2f9151a130.png)
![](images/4a1192b08a5588d2ac0f778efad9e13f.png)

52
·

CC 4.0 BY-SA版权

版权声明：本文为博主原创文章，遵循 [CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/) 版权协议，转载请附上原文出处链接和本声明。

文章标签：

[#人工智能](https://so.csdn.net/so/search/s.do?q=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#大数据](https://so.csdn.net/so/search/s.do?q=%E5%A4%A7%E6%95%B0%E6%8D%AE&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#产品经理](https://so.csdn.net/so/search/s.do?q=%E4%BA%A7%E5%93%81%E7%BB%8F%E7%90%86&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#机器学习](https://so.csdn.net/so/search/s.do?q=%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#算法](https://so.csdn.net/so/search/s.do?q=%E7%AE%97%E6%B3%95&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#深度学习](https://so.csdn.net/so/search/s.do?q=%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#大模型学习](https://so.csdn.net/so/search/s.do?q=%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AD%A6%E4%B9%A0&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)

【ollama】embeddinggemma-300m一键部署

使用ollama部署embeddinggemma-300m的embedding服务

回到今天的主题，面试官经常问这样一个问题：

> “你能讲讲 Agent 的记忆模块（Memory）是怎么做的吗？”

这个问题其实比听起来难。

很多人回答“就是存上下文呀”，但这只是冰山一角。

要真正答好，得从三个角度说清楚：**为什么需要记忆、有哪些类型、在工程上怎么落地。**

今天这篇，就把 Agent 里的“记忆系统”讲透。

### 一、为什么 Agent 需要“记忆”

很多人第一次接触 Agent 时，都会想： LLM 本身不是能看上下文吗？那为什么还需要单独搞个 Memory 模块？

原因其实很现实，那就是**上下文是易失的，记忆是持久的。**

LLM 的上下文窗口（context window）再大，也只能容纳有限的 token； 一旦超出窗口，早期对话内容就会被截断丢失。

而真实世界的任务，往往是**持续多轮、跨天、跨主题**的。

比如：

* 一个 AI 助手在帮用户规划学习计划；
* 一个内部知识问答 Agent 在多轮推理；
* 或一个自动化 Agent 在执行长期任务（如研究报告生成）。

这些任务都要求 Agent 能“记住”之前发生的事。

换句话说，**没有 Memory，Agent 就只是一个短期对话机器人； 有了 Memory，它才开始像一个“持续智能体”。**

### 二、记忆模块的主流类型

从工程角度看，Agent 的记忆主要分为两类：

* **短期记忆（Short-term / Context Memory）**
* **长期记忆（Long-term / Persistent Memory）**

两者的区别，本质是**存多久、怎么取、何时更新**。

#### 2.1 短期记忆：上下文缓存

短期记忆就是对“当前任务上下文”的维护。

比如，当前任务的最近 3~5 轮对话、执行状态、调用结果。

\*\*实现方式：\*\*通常就是将最近的 Prompt、Response 压缩成结构化的上下文缓存， 下一轮输入时，再把这些内容拼接进模型上下文，让 LLM “记得”当前对话。

**常见做法：**

1. Sliding Window（滑动窗口）：固定容量，最新的进、最早的出。
2. Summarization（摘要式记忆）：当窗口超长时，用 LLM 总结旧内容。
3. State Tracking（状态缓存）：将任务状态（变量、参数）结构化保存。

短期记忆的关键，是**实时性与上下文一致性**。 但它有天然限制：存不多、查不快、易丢失。

#### 2.2 长期记忆：持久存储 + 向量检索

长期记忆是 Agent 的“知识库大脑”， 用于存放历史事件、长期目标、人物信息、任务日志等。

典型结构包括：

1. **向量数据库（Vector Store）**

* 把对话或文档内容转成 embedding 向量；
* 存入 Milvus、Faiss、Weaviate、Chroma 等；
* 当需要回忆时，通过语义相似度检索相关内容。

2. **检索回顾（Retrieval + Reflection）机制**

* 模型每次决策前，先从记忆库里查找相关内容；
* 将检索结果拼回 prompt ；
* 再由 LLM 决定如何利用这些信息。

3. **重要性筛选（Memory Filtering）**

* 不是什么都存，而是存“有意义”的片段；
* 例如通过打分机制筛选出“影响后续决策”的记忆。

一个常见策略是：

> 短期用 Context 记当前，长期用 Vector Store 记历史。

这样一来，Agent 就能在任意时刻“回忆起”过去的交互、计划或决策依据。

### 三、Memory 模块在框架中的位置

从架构上看，Memory 模块通常嵌在 **Agent 主循环（loop）** 中， 介于输入解析和决策生成之间。

典型流程如下：

```

Input → Retrieve Memory → Combine Context → LLM Reasoning → Output → Update Memory

```

也就是说：

1. 在每轮决策前，从记忆库里检索可能有用的历史信息；
2. 把它们拼到当前 prompt；
3. 生成输出后，再把新的决策和结果写回 Memory。

在 ReAct、AutoGPT、LangChain 等框架中，这个过程几乎是标配。

LangChain 里甚至直接提供了 Memory 接口：

```

ConversationBufferMemoryConversationSummaryMemoryVectorStoreRetrieverMemory

```

每一种都代表不同粒度和生命周期的记忆形式。

### 四、记忆在真实项目里的落地方式

结合训练营中的几个典型项目，我们来看 Memory 模块是如何被用起来的。

#### Case 1：企业内部知识助手

* \*\*背景：\*\*某企业想让员工用自然语言查询内部制度、流程文档。
* **实现：**

* 长期记忆：所有制度文档嵌入向量数据库；
* 短期记忆：用户最近提问与系统回答缓存；
* 检索机制：每次提问先从向量库取 5 条相关文档，再结合上下文拼 Prompt。

* \*\*效果：\*\*模型能“记得”用户上次问过的主题，避免重复解释； 还能跨文档整合答案。

#### Case 2：智能会议纪要 Agent

* \*\*背景：\*\*企业会议中自动生成纪要和任务清单。
* **实现：**

* 短期记忆：会议实时转录文本；
* 长期记忆：每次会议总结的议题、负责人、进展；
* 检索：新会议前先检索相关项目进度。

* \*\*效果：\*\*Agent 能“记得”上次会议谁负责什么任务，自动续写本次议题。

#### Case 3：AI 学习助手

* \*\*背景：\*\*面向学员的问答机器人，能持续跟踪学习进度。
* **实现：**

* 长期记忆：每个学员的知识点记录、提问历史；
* 短期记忆：当前提问上下文；
* 机制：每次回答时，检索该学员之前错误题目和近期表现。

* \*\*效果：\*\*回答不再“零散”，而是持续追踪用户的知识路径。

#### 小结：

真实项目中的记忆模块，几乎都采用：

> **“短期上下文 + 长期检索” 的混合策略。**

这种设计能兼顾实时性与容量，既让模型保持语境连续，又能避免超窗口问题。

### 五、工程化取舍与实现细节

从工程角度看，设计 Memory 模块时主要要解决三件事：

#### 5.1 存哪儿？——存储方式

1. **本地文件（轻量级）**

* 适合单用户、小项目；
* 一般用 JSON/SQLite 存储对话与 embedding。

2. **云端数据库（中型项目）**

* 如 Supabase、Pinecone、Milvus；
* 支持 embedding 存储、向量检索。

3. **混合存储（企业级）**

* 结构化内容存 SQL；
* 非结构化内容存向量库；
* 用索引映射做快速检索。

#### 5.2 存什么？——记忆内容选择

典型策略包括：

* **摘要压缩：** 旧记忆生成摘要存档；
* **重要性过滤：** 只保留被模型评估为“有价值”的内容；
* **分层存储：** 高频使用的放快存区，低频的归档；
* **多模态扩展：** 可加入图片、语音等 embedding 信息。

#### 5.3 什么时候更新？——记忆维护机制

Agent 的记忆不能无限增长，必须有更新机制。

常见策略：

1. **时间衰减（Time Decay）**

* 旧记忆权重逐渐降低；
* 检索时优先取近期内容。

2. **重要性更新（Relevance Update）**

* 当一条记忆被反复检索，就提升它的重要性；
* 不再被用到的，逐步淘汰。

3. **总结归档（Summarize & Merge）**

* LLM 定期对历史对话生成摘要，替代旧记忆。

这就是“让 Agent 既记得住，又不忘记太多”的工程平衡。

### 六、面试官在听什么？

很多人在面试里说“我们用了 Memory”， 但如果说不清楚它**存哪、取哪、怎么用**，就显得空。

可以这样答：

1、当前主流 Agent 的记忆系统通常由短期与长期两部分组成：

2、短期记忆维持上下文连续，常用滑动窗口或摘要；

3、长期记忆用向量数据库存历史信息，通过相似度检索进行回顾；

4、在每轮推理前，系统会从记忆库中检索相关内容拼接进 prompt，

5、推理结束后再将结果写回数据库，形成一个“Retrieve → Reason → Update”的闭环。

若被追问“为什么不直接让模型自己记”， 可以补一句：

> 因为 LLM 不具备持久状态存储能力，必须依赖外部存储系统， Memory 模块的本质，就是“为语言模型补上状态管理能力”。

### 七、总结

1. **记忆模块的核心价值**： 让模型具备“长期状态感”，从短期问答进化为真正的 Agent。
2. **两类核心机制**： 短期记忆保上下文一致性，长期记忆保知识持续性。
3. **实现关键**： 存储（Vector Store）+ 检索（Retrieval）+ 更新（Summarize）。
4. **工程取舍**： 灵活与效率、容量与可控之间永远是平衡问题。
5. **面试启发**： 会讲原理没用，能解释“为什么这样设计”才显得懂工程。

### 八、如何系统的学习大模型 AI ？

由于新岗位的生产效率，要优于被取代岗位的生产效率，所以实际上整个社会的生产效率是提升的。

但是具体到个人，只能说是：

**“最先掌握AI的人，将会比较晚掌握AI的人有竞争优势”。**

这句话，放在计算机、互联网、移动互联网的开局时期，都是一样的道理。

我在一线互联网企业工作十余年里，指导过不少同行后辈。帮助很多人得到了学习和成长。

我意识到有很多经验和知识值得分享给大家，也可以通过我们的能力和经验解答大家在人工智能学习中的很多困惑，所以在工作繁忙的情况下还是坚持各种整理和分享。但苦于知识传播途径有限，很多互联网行业朋友无法获得正确的资料得到学习提升，故此将并将重要的AI大模型资料包括AI大模型入门学习思维导图、精品AI大模型学习书籍手册、视频教程、实战学习等录播视频免费分享出来。

**一直在更新，更多的大模型学习和面试资料已经上传带到CSDN的官方了，有需要的朋友可以扫描下方二维码免费领取【保证100%免费】👇👇**

![在这里插入图片描述](images/999a0d6db49643fc2967a6a158bdb6d3.jpeg)

### 01.大模型风口已至：月薪30K+的AI岗正在批量诞生

![在这里插入图片描述](images/e5e633843184938c7bceb51f0fd461cd.png)

2025年大模型应用呈现爆发式增长，根据工信部最新数据：

国内大模型相关岗位缺口达47万

初级工程师平均薪资28K（数据来源：BOSS直聘报告）

70%企业存在"能用模型不会调优"的痛点

真实案例：某二本机械专业学员，通过4个月系统学习，成功拿到某AI医疗公司大模型优化岗offer，薪资直接翻3倍！

### 02.大模型 AI 学习和面试资料

1️⃣ 提示词工程：把ChatGPT从玩具变成生产工具
 2️⃣ RAG系统：让大模型精准输出行业知识
 3️⃣ 智能体开发：用AutoGPT打造24小时数字员工

📦熬了三个大夜整理的《AI进化工具包》送你：
 ✔️ 大厂内部LLM落地手册（含58个真实案例）
 ✔️ 提示词设计模板库（覆盖12大应用场景）
 ✔️ 私藏学习路径图（0基础到项目实战仅需90天）

![在这里插入图片描述](images/b2566af563b0266bea1781f453a3d409.jpeg)
 ![在这里插入图片描述](images/07e9ac08750c5f362e1c5cd77deaceaf.jpeg)
 ![在这里插入图片描述](images/5480a85d683c37ad69374b00a0a95d02.jpeg)

![在这里插入图片描述](images/2741a0e3cfe0a284abba5b5c86ad20a8.jpeg)
 ![在这里插入图片描述](images/03ae42fc9372e3a2c91375e6332a465a.jpeg)
 ![在这里插入图片描述](images/a6dd175713f7b6c4116aa54a1f02f22a.jpeg)

#### 第一阶段（10天）：初阶应用

该阶段让大家对大模型 AI有一个最前沿的认识，对大模型 AI 的理解超过 95% 的人，可以在相关讨论时发表高级、不跟风、又接地气的见解，别人只会和 AI 聊天，而你能调教 AI，并能用代码将大模型和业务衔接。

* 大模型 AI 能干什么？
* 大模型是怎样获得「智能」的？
* 用好 AI 的核心心法
* 大模型应用业务架构
* 大模型应用技术架构
* 代码示例：向 GPT-3.5 灌入新知识
* 提示工程的意义和核心思想
* Prompt 典型构成
* 指令调优方法论
* 思维链和思维树
* Prompt 攻击和防范
* …

#### 第二阶段（30天）：高阶应用

该阶段我们正式进入大模型 AI 进阶实战学习，学会构造私有知识库，扩展 AI 的能力。快速开发一个完整的基于 agent 对话机器人。掌握功能最强的大模型开发框架，抓住最新的技术进展，适合 Python 和 JavaScript 程序员。

* 为什么要做 RAG
* 搭建一个简单的 ChatPDF
* 检索的基础概念
* 什么是向量表示（Embeddings）
* 向量数据库与向量检索
* 基于向量检索的 RAG
* 搭建 RAG 系统的扩展知识
* 混合检索与 RAG-Fusion 简介
* 向量模型本地部署
* …

#### 第三阶段（30天）：模型训练

恭喜你，如果学到这里，你基本可以找到一份大模型 AI相关的工作，自己也能训练 GPT 了！通过微调，训练自己的垂直大模型，能独立训练开源多模态大模型，掌握更多技术方案。

到此为止，大概2个月的时间。你已经成为了一名“AI小子”。那么你还想往下探索吗？

* 为什么要做 RAG
* 什么是模型
* 什么是模型训练
* 求解器 & 损失函数简介
* 小实验2：手写一个简单的神经网络并训练它
* 什么是训练/预训练/微调/轻量化微调
* Transformer结构简介
* 轻量化微调
* 实验数据集的构建
* …

#### 第四阶段（20天）：商业闭环

对全球大模型从性能、吞吐量、成本等方面有一定的认知，可以在云端和本地等多种环境下部署大模型，找到适合自己的项目/创业方向，做一名被 AI 武装的产品经理。

* 硬件选型
* 带你了解全球大模型
* 使用国产大模型服务
* 搭建 OpenAI 代理
* 热身：基于阿里云 PAI 部署 Stable Diffusion
* 在本地计算机运行大模型
* 大模型的私有化部署
* 基于 vLLM 部署大模型
* 案例：如何优雅地在阿里云私有部署开源大模型
* 部署一套开源 LLM 项目
* 内容安全
* 互联网信息服务算法备案
* …

学习是一个过程，只要学习就会有挑战。天道酬勤，你越努力，就会成为越优秀的自己。

如果你能在15天内完成所有的任务，那你堪称天才。然而，如果你能完成 60-70% 的内容，你就已经开始具备成为一名大模型 AI 的正确特征了。

###### 这份完整版的大模型 AI 学习资料已经上传CSDN，朋友们如果需要可以微信扫描下方CSDN官方认证二维码免费领取【`保证100%免费`】

![在这里插入图片描述](images/999a0d6db49643fc2967a6a158bdb6d3.jpeg)

您可能感兴趣的与本文相关的镜像

![【ollama】embeddinggemma-300m](images/2725516f178d750220ca40ac4691992e.jpg)

【ollama】embeddinggemma-300m

语义检索

相似度

Embedding

使用ollama部署embeddinggemma-300m的embedding服务

一键部署运行

![](images/3499c7f767d8069c132c42c5e958af67.png)

确定要放弃本次机会？

福利倒计时

*:*

*:*

![](images/241bad06794cb671d2a282c127a3c99e.png)
立减 ¥

普通VIP年卡可用

[立即使用](https://mall.csdn.net/vip)

[![](images/9219e38287a2060015ab6491a4025275.jpg)

AI大模型-大飞](https://blog.csdn.net/m0_63171455)

[关注](javascript:;)
关注

* ![](images/7ae65a949cf422c16a3786a91cf99bf5.png)
  ![](images/864d5cb763134ab76db2e859d86c6ac9.png)
  ![](images/0242911ea5c167952ccce45d91294727.png)

  44

  点赞
* ![](images/0b4303d154e4a79a407e76e4701501e5.png)
  ![](images/eeee8107f3b2f57f85820f2decdaec0b.png)

  踩
* [![](images/79bdf29087a3087d00590dc03d3fb1b5.png)
  ![](images/7fd742a4babd71a5a9496b1b4bd992d0.png)
  ![](images/4674569fc86e4bbaace341fb5a9fec58.png)

  52](javascript:;)

  收藏

  觉得还不错?
  一键收藏
  ![](images/b6f228a33563ff279d1935a8d841e241.png)
* ![](images/b2e686a877c19770edb75ee87b4459a0.png)
  知道了

  [![](images/96a8575800e94aded08b5299cc1f98de.png)

  0](#commentBox)

  评论
* [![](images/d2fcbdc90dda726c2bfd8148bb28973b.png)
  分享](javascript:;)

  复制链接

  分享到 QQ

  分享到新浪微博

  ![](images/4c875eeaf69ccf68dbb37cf3137e1884.png)扫一扫
* ![](images/3f6c9dae656a10d2abaa9b2f08bffd89.png)

  ![](images/6e27cb0a51e039d131e7e6af5c4b931c.png)
  举报

  ![](images/6e27cb0a51e039d131e7e6af5c4b931c.png)
  举报

![]()

[科学智能体（*AI* *Agent*）系统工程师：构建未来科研自动化的核心力量

最新发布](https://blog.csdn.net/zwqhlzd/article/details/158035426)

[郑伟强dev的专栏](https://blog.csdn.net/zwqhlzd)

02-13
![](images/c435921c498fd8cf48f9f07527be548a.png)
155

[摘要：安徽省人力资源有限公司招聘科学智能体系统工程师，负责设计实现面向科学仿真*与*优化的*AI**Agent*系统架构。岗位要求具备扎实的软件系统设计能力，熟悉大语言模型技术，有构建*Agent*系统的经验，熟练使用Python，并能*与*科研团队协作。工作内容包括智能体系统架构设计、*大模型**与*科学工具集成、*记忆*机制开发、科学推理模块构建等。该职位处于*AI**与*科学计算交叉领域前沿，旨在通过智能体系统提升科研自动化水平，加速科学发现进程。](https://blog.csdn.net/zwqhlzd/article/details/158035426)

参与评论
您还未登录，请先
登录
后发表或查看评论

[*AI**产品经理**面试*宝典第79天：GPT演进*与*多模态*AI*应用*面试*指南](https://blog.csdn.net/lifetragedy/article/details/151063005)

[打造全国最全的AI Agent开发知识领域的博客](https://blog.csdn.net/lifetragedy)

09-01
![](images/c435921c498fd8cf48f9f07527be548a.png)
216

[本文深入解析GPT系列模型从基础语言预测到多模态智能的演进历程，涵盖Transformer架构、RLHF技术、多模态融合等核心概念，并提供企业级*AI*应用场景*与**面试*应答策略，助力*AI**产品经理*精准掌握技术要点*与**面试**技巧*。](https://blog.csdn.net/lifetragedy/article/details/151063005)

[*AI* *Agent*的*记忆*体系*与*架构设计](https://blog.csdn.net/qq_33137873/article/details/148606642)

[深度学习机器](https://blog.csdn.net/qq_33137873)

06-12
![](images/c435921c498fd8cf48f9f07527be548a.png)
1233

[在实际应用中，需要考虑效率和准确率、以及性价比来选择最合适的方案。对于简单的聊天机器人场景，可以直接使用滑动窗口维护上下文，利用LLM的长上下文能力保持*记忆*；如果需要*Agent*能在多个会话历史中保持*记忆*，则需要借助数据库进行持久化；对于超长期的*记忆*，可以利用LLM进行关键信息的抽取并进行结构化存储。](https://blog.csdn.net/qq_33137873/article/details/148606642)

[主流*Agent* Memory工具or框架对比（Mem0、LangMem、Letta）](https://blog.csdn.net/wuyongfan6589/article/details/148233043)

[wuyongfan6589的博客](https://blog.csdn.net/wuyongfan6589)

05-26
![](images/c435921c498fd8cf48f9f07527be548a.png)
3402

[主流memory框架对比](https://blog.csdn.net/wuyongfan6589/article/details/148233043)

[| *AI* *Agent* 核心架构 | 智能体生命周期（感知→规划→执行→反馈）、工具调用（Function Calling）、*记忆*机制（短期/长期*记忆*）](https://programb.blog.csdn.net/article/details/155140216)

[[Blog][Domain] programb.blog.csdn.net](https://blog.csdn.net/blog_programb)

11-26
![](images/c435921c498fd8cf48f9f07527be548a.png)
1287

[*AI* *Agent* 技术的核心是“让 LLM 具备自主决策能力”，而 ReAct/CoT 等思维框架是实现这一目标的关键工具。实践中需注意：
- 先解决“场景聚焦”：不要追求“万能 *Agent*”，优先落地垂直场景（如“电商数据分析 *Agent*”“办公 *Agent*”），再逐步扩展；
- 平衡“自动化*与*人工干预”：关键任务（如财务审批）需预留人工审核入口，避免 *Agent* 自主决策风险；
- 持续优化思维链：基于用户反馈迭代 Prompt 设计，丰富示例库，让 *Agent* 越用越智能。](https://programb.blog.csdn.net/article/details/155140216)

[*Agent*中的memory](https://blog.csdn.net/sinat_28694519/article/details/150450926)

[sinat\_28694519的博客](https://blog.csdn.net/sinat_28694519)

08-16
![](images/c435921c498fd8cf48f9f07527be548a.png)
1145

[众所周知，*大模型*是无状态的。但是基于*大模型*的*agent*一般是有状态的，也就是它有*记忆*功能。在*AI* *Agent*框架中，Memory机制是核心组件之一，它赋予*Agent*持续*学习*和上下文感知的能力，使其能够像人类一样基于历史交互进行决策。类似人脑一样，memory机制是*agent*智能化的基石。当前，memory机制也有一些挑战，比如*记忆*泄露（未清理的旧数据可能导致存储膨胀（需设置TTL））、隐私合规（GDPR要求用户数据可删除）等。参考文档。](https://blog.csdn.net/sinat_28694519/article/details/150450926)

[进阶篇05*Agent**记忆*memory](https://blog.csdn.net/omonday1234/article/details/147688230)

[omonday1234的专栏](https://blog.csdn.net/omonday1234)

05-03
![](images/c435921c498fd8cf48f9f07527be548a.png)
2002

[*记忆*（Memory）模块负责存储信息，包括过去的交互、*学习*到的知识，甚至是临时的任务信息。对于一个智能体来说，有效的*记忆*机制能够保障它在面对新的或复杂的情况时，调用以往的经验和知识。例如，一个具备*记忆*功能的聊天机器人可以记住用户的偏好或先前的对话内容，从而提供更个性化和连贯的交流体验。它分为短期*记忆*和长期*记忆*：a. 短期*记忆*，所有的上下文*学习*都是利用短期*记忆*来*学习*；b. 长期*记忆*，这为智能体提供了长时间保留和回忆。](https://blog.csdn.net/omonday1234/article/details/147688230)

[*AI* *Agent* *记忆*技术浅析](https://devpress.csdn.net/v1/article/detail/145400248)

[m0\_59163425的博客](https://blog.csdn.net/m0_59163425)

02-03
![](images/c435921c498fd8cf48f9f07527be548a.png)
2486

[*Agent**记忆*（*Agent* Memory）是指*AI* *Agent*在执行任务过程中存储和管理信息的能力和机制。它类似于人类的*记忆*系统，使*Agent*能够记住过去的交互、经验和知识，并在后续任务中利用这些信息做出更好的决策。这种*记忆*机制对于实现持续*学习*和处理长期任务至关重要。](https://devpress.csdn.net/v1/article/detail/145400248)

[智能制造Java *AI*开发*面试*：Spring *AI**与*RAG系统深度解析](https://blog.csdn.net/2303_76177839/article/details/152115318)

[2303\_76177839的博客](https://blog.csdn.net/2303_76177839)

09-26
![](images/c435921c498fd8cf48f9f07527be548a.png)
864

[本文通过一场真实的Java *AI*开发*面试*，深入解析Spring *AI*框架和RAG系统在智能制造场景中的应用，包含完整的技术实现代码和架构设计思路，帮助开发者掌握*AI*技术*与*传统Java开发的结合。](https://blog.csdn.net/2303_76177839/article/details/152115318)

[字节跳动*AI**大模型**学习*手册：涵盖LLM基础、RAG、*Agent*、微调*与*私有化部署的全栈*学习*路径](https://wenku.csdn.net/doc/3axeox6sp7)

[*AI**大模型**学习*手册作为字节跳动系统性梳理并开源的一套面向*工程实践**与*学术进阶并重的*学习*资源，其知识体系并非零散知识点的堆砌，而是以“认知跃迁—能力构建—工程落地—领域深化—生态协同”为逻辑主线，构建起覆盖...](https://wenku.csdn.net/doc/3axeox6sp7)

[*AI**面试*核心知识点汇总：从智能代理、神经网络到Python主流框架*详解*](https://wenku.csdn.net/doc/28je6z6wa0)

[本笔记标题《*AI*-Interview-Notes：*AI*我的*AI**面试*注意事项，代码和来源在这里》明确指向一个面向求职者、尤其是应届生*与*转行工程师的实战型知识体系，其核心价值不仅在于概念梳理，更在于将抽象理论*与**工程实践*、*面试*...](https://wenku.csdn.net/doc/28je6z6wa0)

[*大模型*从入门到应用——LangCh*ai*n：快速入门-[链（Ch*ai*ns）、代理（*Agent**:*）和*记忆*（Memory）]

热门推荐](https://machinelearning.blog.csdn.net/article/details/131622827)

[冯·诺依曼](https://blog.csdn.net/hy592070616)

07-09
![](images/c435921c498fd8cf48f9f07527be548a.png)
1万+

[在本系列文章中我们会用最简练的语言*与*范例带领大家快速调试并上手LangCh*ai*n，读者读完本系列的文章后，就会对LangCh*ai*n有一个大致的了解并可以将LangCh*ai*n运用到自己开发的程序中。但如果读者想对LangCh*ai*n的各个模块进行更深入的了解，可以继续*学习*《》系列文章。本文主要是阐述了LangCh*ai*n的。](https://machinelearning.blog.csdn.net/article/details/131622827)

[LLM下半场之*Agent*基础能力概述：Profile、Memory、Plan、Action、Eval*学习*笔记](https://devpress.csdn.net/v1/article/detail/133577947)

[Garvin的专栏](https://blog.csdn.net/gshengod)

10-05
![](images/c435921c498fd8cf48f9f07527be548a.png)
3912

[另一种是Muti-Path，这个方案更符合人类的思维方式，因为要解决问题，很难完全设定好端到端的流程，需要给出几种候选的模式，另外需要考虑环境反馈，可以每走一步再次推理和选择最优模式，这里可以参考最近非常火的ReAct的模式，另外LLM也可以代替人类去做多种方案的选择，我们可以把需要考虑的边界给到LLM，由LLM去思考每一步如何选择。在这一步需要建设的能力是*与*外部的服务关联，比如我们的*Agent*是解决帮用户买飞机票的问题，那么在执行阶段就需要*与*飞机票务系统的订票接口关联，也需要*与*用户的信用卡付款接口关联。](https://devpress.csdn.net/v1/article/detail/133577947)

[*ai* *agent*系列之一：从*Agent*到Br*ai*n到Memory 概念摘要](https://devpress.csdn.net/v1/article/detail/139290457)

[Iamduyabo的博客](https://blog.csdn.net/Iamduyabo)

05-29
![](images/c435921c498fd8cf48f9f07527be548a.png)
2276

[A*:* 根据chatgpt的self.client.chat.completions.create源码跟踪，其支持calls参数，并返回下一步是否要执行function call，可以理解是chatgpt实现了planning和reflection。长期*记忆*（LTM）：长期*记忆*可以存储相当长的时间信息，从几天到几十年不等，存储容量基本上是无限的。感知*记忆*：这是*记忆*的最早阶段，提供在原始刺激结束后保留感觉信息（视觉、听觉等）印象的能力。br*ai*n需要具备下图的能力[2]，这些能力都是LLM具备的。](https://devpress.csdn.net/v1/article/detail/139290457)

[一文读懂*大模型* *Agent* 架构，*详解*Profile，Memory，Planning，Action模块作用](https://blog.csdn.net/m0_59596990/article/details/135717263)

[机器学习社区](https://blog.csdn.net/m0_59596990)

01-20
![](images/c435921c498fd8cf48f9f07527be548a.png)
9808

[在*人工智能*领域，人们对*Agent*的期待日益增长。每当基于*Agent*的新开源工具或产品出现时，都能引发热烈的讨论，比如之前的AutoGPT。对于对*Agent*感兴趣的朋友们，我推荐一篇论文，它全面地介绍了*Agent*的架构，对于理解*Agent*的全局有着重要的价值。这篇论文详细解读了*Agent*的概念、发展历史以及近期的研究热点。除了这些基础知识，我认为最有价值的部分在于，它总结了基于大型语言模型（LLM）的*Agent*的架构，使我们能够按照一定的标准范式去设计自己的*Agent*。](https://blog.csdn.net/m0_59596990/article/details/135717263)

[Memory模块是*agent*的一个关键组件](https://blog.csdn.net/weixin_44245188/article/details/148109635)

[weixin\_44245188的博客](https://blog.csdn.net/weixin_44245188)

05-21
![](images/c435921c498fd8cf48f9f07527be548a.png)
1644

[在*Agent*系统中，Memory模块是一个关键的组件，其主要功能是存储和检索信息，以支持*agent*的*学习*和决策过程。该模块模拟人类*记忆*的某些特征，能够动态地保存和更新信息，使*agent*能够利用过去的经验进行推理和决策。为什么要有Memory模块？试想一下，当你和*agent*交互时，如果*agent*没有*记忆*，那就没法进行多轮对话了。你每次提问都相当于重新开始一个对话，对话就不具备连续性。信息储存：能够高效存储多种形式的数据，包括事实、事件、规则和上下文信息，以便在需要时快速访问。信息检索。](https://blog.csdn.net/weixin_44245188/article/details/148109635)

[*Agent*——*记忆模块*](https://blog.csdn.net/xzq_qzx_/article/details/136561767)

[xzq\_qzx\_的博客](https://blog.csdn.net/xzq_qzx_)

03-08
![](images/c435921c498fd8cf48f9f07527be548a.png)
1726

[在一系列的教育辅导对话中，学生可能会提出不同的数学问题或理解难题（如“我不太理解二次方程的求解方法”）。ConversationSummaryMemory 可以帮助 *AI* 总结之前的辅导内容和学生的疑问点，以便在随后的辅导中提供更针对性的解释和练习。](https://blog.csdn.net/xzq_qzx_/article/details/136561767)

[万字解析 *Agent* Memory 实现，入门到精通，看这一篇就够了](https://devpress.csdn.net/v1/article/detail/151077509)

[HJS123456780的博客](https://blog.csdn.net/HJS123456780)

09-01
![](images/c435921c498fd8cf48f9f07527be548a.png)
2245

[大语言模型本质是对人脑神经网络的模拟，智能体*记忆*也可以通过模拟人脑*记忆*来实现更强的性能。](https://devpress.csdn.net/v1/article/detail/151077509)

[【爆肝干货】*Agent**记忆*系统全拆解：从原理到实战，一篇搞定*记忆模块*的N种实现方式“](https://devpress.csdn.net/v1/article/detail/154777084)

[m0\_59164520的博客](https://blog.csdn.net/m0_59164520)

11-13
![](images/c435921c498fd8cf48f9f07527be548a.png)
1235

[*Agent**记忆模块*分为短期*记忆*（维护上下文连续性）和长期*记忆*（提供知识持久性）。短期*记忆*通过上下文缓存实现，长期*记忆*依赖向量数据库和检索机制。工程实现需考虑存储方式、*记忆*内容选择和更新策略，采用*"*短期上下文+长期检索*"*混合策略。*记忆模块*让*AI*从短期对话机器人进化为持续智能体，成为*Agent*的核心能力之一。](https://devpress.csdn.net/v1/article/detail/154777084)

[*AI* *Agent*核心概念解析：架构组成、*记忆*机制*与*多智能体框架MetaGPT实战](https://wenku.csdn.net/doc/3ygwq8ovw8)

[*AI* *Agent*（*人工智能*智能体）是当前*人工智能*领域最具革命性*与*实践潜力的核心范式之一，其本质已远超传统*机器学习*模型或静态大语言模型（LLM）的范畴，而是一种具备目标导向性、自主决策能力、动态环境交互能力*与*持续...](https://wenku.csdn.net/doc/3ygwq8ovw8)