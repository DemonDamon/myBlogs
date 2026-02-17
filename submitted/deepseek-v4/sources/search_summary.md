# DeepSeek V4 搜索摘要

## 搜索时间
2026-02-17

## 核心发现

### 1. 发布状态
- **当前状态**：正灰度测试中，App 已更新至 1.7.4 版本
- **预计发布时间**：2026 年 2 月中旬（春节前后）
- **版本定位**：可能是 V3 系列最终进化形态，或 V4 正式亮相前的终极灰度版

### 2. 性能突破
- **上下文长度**：从 128K 扩展至 1M（提升约 10 倍）
- **知识库更新**：截至 2025 年 5 月
- **复杂任务处理**：已对齐 Gemini 3 Pro 及 Kimi K2.5 等主流闭源模型
- **编程任务**：内部测试显示超越 Anthropic Claude 及 OpenAI GPT 系列同代模型

### 3. 核心技术创新
- **mHC（流形约束超连接）**：
  - 解决 Transformer 模型在层数极深时信息流动的瓶颈和训练不稳定问题
  - 让神经网络层之间的"对话"更丰富、更灵活
  - 通过数学"护栏"防止信息被放大或破坏

- **Engram 架构**：
  - 受生物神经系统启发的"AI 记忆模块"
  - 将"记忆"与"计算"解耦
  - 静态知识存放在稀疏内存表中（可放在廉价 DRAM）
  - 释放昂贵的 GPU 内存（HBM）用于动态计算

### 4. 泄露基准测试数据（待确认）
- **SWE-bench Verified**: 83.7%（超越 Claude Opus 4.5 的 80.9% 和 GPT-5.2 的 80%）
- **AIME 2026**: 99.4%
- **IMO Answer Bench**: 88.4%
- **FrontierMath Tier 4**: 23.5%（达到 GPT-5.2 的 11 倍）

### 5. 成本与价值
- **训练与推理成本**：进一步压缩
- **核心价值**：通过底层架构创新推动 AI 应用商业化落地，而非颠覆现有 AI 价值链
- **算力芯片与内存瓶颈**：从算法和工程层面突破

## 待爬取高价值页面列表

### 官方/权威来源
1. DeepSeek 官网（待获取具体 URL）
2. DeepSeek API 文档（多个来源）

### 技术分析文章
1. [中关村在线] DeepSeek V4 即将发布,代码更新暗示新架构与性能飞跃
   - URL: https://ai.zol.com.cn/1121/11216926.html
   - 关键：FlashMLA 代码更新、MODEL1 标识符、键值缓存结构变化

2. [腾讯新闻] 从 DSA 到 Engram，一年来 DeepSeek 层层勾勒 V4 架构创新
   - URL: https://news.qq.com/rain/a/20260114A06NQI00
   - 关键：UE8M0 FP8、DSA、上下文光学压缩、mHC 与 Engram 技术演变

3. [网易] 春节见？DeepSeek 下一代模型："高性价比"创新架构
   - URL: https://m.163.com/dy/article/KLFTG9VJ05198NMR.html
   - 关键：野村证券报告分析、mHC 与 Engram 详细介绍

4. [中关村在线] DeepSeek 静默升级至百万级上下文,V4 未官宣但性能跃居系列最强
   - URL: https://ai.zol.com.cn/1133/11332914.html
   - 关键：百万上下文实测、编程任务复杂物理建模测试

### 对比评测文章
1. [新智元] 刚刚,DeepSeek V4 基准测试泄露!疑似明天发布,全场惊呼新王归来
   - URL: https://m.163.com/dy/article/KLTQ4AFU055616YL.html
   - 关键：泄露的基准测试数据详细分析

2. [CSDN] gpt 和 deepseek 对比
   - URL: https://m.blog.csdn.net/m0_63345182/article/details/145758047
   - 关键：性能、多模态、成本对比

### 架构原理文章
1. [PHP中文网] DeepSeek 支持哪些模型?MoE 架构详解
   - URL: https://www.php.cn/faq/2098151.html
   - 关键：MoE 架构、V4 Preview 特性

2. [腾讯新闻] DeepSeek 新模型上线实测:1M 上下文背后,是进化还是取舍?
   - URL: https://news.qq.com/rain/a/20260214A07FFT00
   - 关键：实际测试案例、性能表现

### 实战/应用文章
1. [CSDN] DeepSeek API 文档介绍
   - URL: https://blog.csdn.net/qq_38027465/article/details/145519538
   - 关键：API 使用方法

## 搜索总结

从搜索结果看，DeepSeek V4 是一次重要的架构创新迭代：

1. **技术路线**：延续 DeepSeek 在"稀疏化"方向的探索（MoE、MLA、FP8），新增 mHC 和 Engram 两项突破性技术
2. **性能目标**：通过百万级上下文 + Engram 记忆机制实现全仓库级推理能力
3. **成本优化**：在国产算力受限背景下，通过架构创新突破算力芯片和内存瓶颈
4. **市场定位**：推动 AI 应用商业化落地，而非单纯追求参数规模

下一步需要详细爬取这些页面以获取更详细的技术细节和实测数据。
