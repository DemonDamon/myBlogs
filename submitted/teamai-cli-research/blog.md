# teamai-cli 实测：把 Coding Agent 的「团队经验」装进 Git 仓库，这事成色如何

前几天刷到一篇推文，介绍腾讯开源的 teamai-cli——一个把 Skills、Rules、Hooks、MCP 配置放进共享 Git 仓库、再同步给 Claude Code / Codex / CodeBuddy / Cursor 等各种 Coding Agent 的 CLI 工具。推文的卖点很清楚：模型、Agent、设备都可以换，唯独你给 Agent 调教出来的那套工作习惯带不走。

这个痛点我熟。同一个项目，Claude Code 里攒的一套 Skill，换到 Codex 要重配一遍；同事踩坑总结的 Rule 留在他本地，其他人一概不知。问题是真的，问题是这个工具解决得怎么样。

光看 README 没有发言权，我把仓库 clone 下来读了一遍源码，跑了构建、测试套件，并挑了四个核心机制在本地做了实验。下面是实测结果，好话坏话都讲。

## 一、它到底是个什么东西

一句话：**一个骑在 Git 上的 Agent 配置分发器 + 团队知识库**。

核心循环不复杂：

- 管理员建一个共享仓库（GitHub / TGit / CNB 都行），成员 `teamai init` 绑定
- 你在某个 Agent 里调好了 Skill / Rule / Hook，`teamai push` 推到新分支并自动开 MR
- 评审合并后，其他成员的 SessionStart Hook 自动执行 `teamai pull`，把资源写进各自 Agent 的目录（`~/.claude/skills/`、`~/.codex/skills/`……）
- 另有 `teamai source add` 订阅别的团队公开的 Skill 仓库，形成跨团队的「经验联邦」

![系统架构](./images/architecture.svg)

架构上没什么发明：版本管理靠 Git，评审靠 MR，触发靠 Hook，检索靠 BM25，全是工程界成熟了几十年的组件。它的全部价值在于「编织」——把这些散装组件缝成一张网，兜住 AI 团队协作里四处漂散的配置和经验。

工程底子先给个数据：src 下 334 个 TypeScript 文件、约 8.6 万行，配了 147 个测试文件、1978 个用例，我在本地全量跑了一遍，**7.5 秒全部通过**。对一个刚开源几个月的项目，这个测试密度在同类工具里算少见的认真。

## 二、实测一：摩擦信号，这层最有想象力

推文里最吸引我的是「摩擦信号」机制：Session 结束时，Stop Hook 给这次会话打分——你有没有打断 AI、拒绝过它的工具调用、AI 有没有反复重试失败命令。又长又顺的会话不触发；真正「跟 AI 搏斗过」的会话才值得沉淀成文档。

读完源码，评分规则是明牌：

| 信号 | 得分 |
|------|------|
| 用户打断 AI | 每次 +20 |
| 用户拒绝工具调用 | 每次 +20 |
| 用户发修正性提示 | 每次 +20 |
| AI 重试失败工具 | ≥3 次 +10，≥5 次 +18，≥8 次 +25 |
| 用了 Skill / 工具多样性 | 最多 +10 |

触发门槛是**摩擦分 ≥ 20 且工具调用 ≥ 15 次**——后者是硬门槛，防止「一个命令被拒了三次」这种空会话也来烦你。

我在沙箱环境里构造了四种 session 事件流，直接喂给它的 Stop Hook 处理器：

**Case A（高摩擦）**：打断 2 次、拒绝工具 1 次、失败重试 8 次、工具调用 20 次。触发了，输出和推文里那条提示一字不差：

```
[teamai] This session may contain a problem worth documenting:
you interrupted the AI twice, you rejected 1 tool call,
the AI retried failing tools 8 times.

Task: Fix duplicate project-level Hook injection

Consider running /teamai-share-learnings to summarize what
you learned and share it with your team.
```

**Case B（顺滑）**：30 次工具调用、零摩擦。不触发。「又长又顺的 session 不沉淀」的承诺兑现了。

**Case C（摩擦够但没干活）**：打断 3 次、拒绝 2 次，但工具调用只有 5 次。不触发。硬门槛起作用了。

**Case D（边界值）**：打断 1 次 + 重试 3 次（20+10=30 分）、工具调用 20 次。触发。

![摩擦信号数据流](./images/friction-flow.svg)

四个 case 全部符合设计预期。更让我意外的是实现质量：这段代码有分层缓存（5 分钟 TTL 的 fast-path 短路）、每 session 只提示一次的去重、防抖动设计，注释里连「为什么 PID 回退的 sessionId 会产生嵌套目录导致 GC 清不掉」这种边角都写了。这不是 demo 代码的写法。

## 三、实测二：知识检索，中文能用，但别指望跨语言

recall 是 BM25 加图谱增强的检索，默认关闭，`teamai recall enable` 显式开启。我构造了一个四篇文档的中文知识库（端口冲突排查、部署配置规范、React 踩坑、数据库迁移锁），测了几组查询：

- `recall "端口 冲突"` → 精准命中《MR review 抓到的端口冲突 bug 排查记录》，得分 14.3
- `recall "数据库 迁移 锁"` → 命中迁移锁文档，16.8 分
- `recall "useEffect 订阅 清理"` → 命中 React 文档，但输出了一行 `Matched: useEffect, 清理 | Missing: 订阅`——「订阅」明明在正文里，为什么算 Missing？

看了源码才明白：matched/missing 只按**标题和标签**计算，正文命中不算。这是刻意设计——标题命中的才算「覆盖了你的主题」，只蹭到正文的算「主题相邻」。README 也如实写了：区分词全在 Missing 里时，这条结果只是相关而非答案。这种把判断权交还调用方的诚实，我喜欢。

分词器值得单独一提：`Intl.Segmenter('zh-CN')` 加 CJK bigram 兜底，camelCase 还会拆子词，注释里甚至写清楚了「为什么索引版本不 bump 就能安全地删 token」。中文团队可以放心用。

![知识检索管线](./images/recall-pipeline.svg)

**但有个硬伤**：`recall "port conflict"` 在纯中文文档上一无所获。BM25 是纯词法匹配，没有任何跨语言能力——文档写成中文，英文查询就查不到，反之亦然。混语言团队（文档中文、代码注释英文）要有心理准备，这是词法检索的天花板，不是 bug。

## 四、实测三：代码知识图谱，方向对，口径要打折

`teamai import --dir` 可以把一个代码仓库解析成 `teamwiki/` 下的结构化图谱：组件、接口、配置、跨文件依赖边，检索命中时附带源码路径，让 Agent「拿着地图改代码」而不是盲人摸象。

我写了个四文件的小项目（`OrderService` 依赖 `OrderRepository` 和 `HttpOrderApiClient`，都依赖 `types.ts`）喂进去：

```
Files: 4
Facts: 11 (relation:5, interface:3, component:3)
Graph: 10 nodes, 8 edges
```

依赖链完全正确：`service.ts → repository.ts → types.ts`、`service.ts → api.ts → types.ts`，接口和组件分类也对。用 `recall "OrderService syncOrder"` 能命中模块页，摘要里直接给出每个组件的源码位置。

但我要泼一盆冷水：所谓「多语言 AST 提取」，实际上是**逐行正则**。TypeScript 的 import 解析就是一条 `/^import\s+.*?from\s+["']([^"']+)["']/`，Go 的组件识别靠 `^type\s+([A-Z]\w+)\s+struct`，整个依赖树里没有一个真正的解析器（没有 typescript、ts-morph、tree-sitter）。所以依赖边在图谱里的来源标的是 `code-heuristic`，不是 `code-ast`。

正则启发式不是不能用——零依赖、快、对约定俗成的代码结构命中率不低，这是个务实的取舍。但它的天花板也很清楚：动态 import、re-export、路径别名、装饰器这些稍复杂的语法就靠不住了，跨仓库依赖是靠节点标签字符串匹配「猜」出来的。**「代码知识图谱」当索引用是合格的，当依赖分析的真相源是不够的。**宣传口径和实现之间，建议按六折理解。

## 五、实测四：Hook 注入与平台绑定

`teamai pull` 会往各 Agent 的配置里写 Hook。我在沙箱里验证了写入 `.claude/settings.json` 的内容：SessionStart、Stop、PostToolUse（含 Skill / TodoWrite 匹配器）各就各位，全部指向统一的 `teamai hook-dispatch` 分发器。

两个细节值得肯定。一是所有 Hook 命令都带 `2>/dev/null || true`——teamai 挂了也绝不搞挂你的 Agent 会话，这是对的优先级。二是它对 Hook 时序预算抠得很细：前台处理统一 4.5 秒预算，硬退出 7 秒，注释里写明了「CodeBuddy 会在 10 秒杀掉 Hook」——这种约束只能来自真实生产环境的挨打。

然后是该说的局限：

**平台绑定偏腾讯系**。托管平台只认 GitHub、TGit（腾讯内网 git.woa.com）、CNB（cnb.cool）三家，自建 GitLab 不支持。代码里留着 tnpm 内部镜像、iWiki 导入、WorkBuddy / CodeBuddy 优先适配的痕迹。MIT 协议是真开源，但这个项目显然首先是为腾讯内部团队的规模服务的，开源更像是顺手为之。用之前想清楚：你的团队工作流是否恰好落在这三家托管平台上。

**维护面是个隐患**。28 个 Agent 适配器、8.6 万行单包 CLI，每家 Agent 的配置格式都在漂移（注释里 CodeBuddy 杀进程超时就是一例），这个适配矩阵的长期维护成本不会低。好在它给了 `toolPaths` 自定义配置路径的逃生门，也做了多 scope（user/project）隔离和继承，架构上是给认真用户的。

## 六、值不值得用

我的判断分三档：

**团队规模 5 人以上、多人共用多个 Coding Agent、托管平台恰好是 GitHub**——值得认真试。它把「Agent 配置」从个人手工艺品变成了有版本、有评审、可回滚的团队资产，光这一点就解决了真实问题。摩擦信号那套「自动识别值得沉淀的 session」是目前开源里少见的思路，且实现质量高于我的预期。

**个人用户**——价值有限但不是零。`teamai init` 会在仓库不存在时自动建仓，一个人用它当「跨 Agent 配置同步器」也行，只是知识库那半套基本吃灰。

**指望图谱做深度代码分析、或者团队文档中英混杂**——现阶段会失望。提取层是正则，检索是词法，这两个天花板短期内不会变。

最后说句总评：teamai-cli 没有发明任何东西，它做的事情是承认一个现实——**Agent 时代的团队工程实践，缺的不是模型能力，是配置和经验的版本控制**。这个判断我认为是对的，执行也够扎实。至于「经验联邦」能不能像它设想的那样在团队间流动起来，那不是技术问题，是组织问题，代码解决不了。
