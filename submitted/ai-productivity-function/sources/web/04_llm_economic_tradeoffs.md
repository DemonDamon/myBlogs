# The economic trade-offs of large language models: A case study

**来源**: https://arxiv.org/abs/2306.07402
**爬取时间**: 2026-02-23

---

## 论文信息

**标题**: The economic trade-offs of large language models: A case study

**中文标题**: 大语言模型的经济权衡：一个案例研究

**作者**: Kristen Howell, Gwen Christian, Pavel Fomitchov, Gitit Kehat, Juliann Marzulla, Leanne Rolston, Jadin Tredup, Ilana Zimmerman, Ethan Selfridge, Joseph Bradley

**学科**:
- Computation and Language (cs.CL)
- Artificial Intelligence (cs.AI)

**发表时间**: 2023年6月8日

**备注**: 论文将在 Association for Computational Linguistics 的 Industry Track 2023 发表

**arXiv ID**: 2306.07402

---

## 摘要

### 应用场景

**通过聊天联系客服**是一种常见做法。

### 核心问题

由于雇佣客服代理的成本很高，许多公司转向**能够辅助人类代理的NLP**，这些系统可以：
- 自动生成回复
- 回复可以直接使用或经过修改

### 模型选择

**大语言模型(LLM)** 很适合这个用例；然而，其功效必须与**训练和提供它们的成本相平衡**。

---

## 研究方法

### 评估框架

本论文评估了LLM对企业实际成本和影响，作为其**生成回复的有用性的函数**。

### 案例研究

在一个现有代理辅助产品的背景下，对**单个品牌**进行案例研究应用。

### 模型特化策略比较

比较三种特化LLM的策略，使用品牌客服代理的反馈：

1. **提示工程** (Prompt Engineering)
2. **微调** (Fine-tuning)
3. **知识蒸馏** (Knowledge Distillation)

---

## 主要发现

### 核心结论

**模型响应的有用性可以弥补我们案例研究品牌的大推理成本差异。**

### 外推应用

我们将发现**外推到更广泛的企业空间**。

---

## 研究意义

### 学术价值

1. **成本-性能权衡**: 系统分析LLM的经济权衡
2. **特化策略比较**: 对比三种主流LLM优化方法
3. **实证研究**: 提供真实企业的案例数据

### 实践价值

1. **企业决策支持**: 帮助企业在LLM部署中平衡成本与效果
2. **策略选择**: 为提示工程、微调、蒸馏提供选择依据
3. **ROI优化**: 通过提升响应有用性来补偿推理成本

---

## 下载资源

- [查看PDF](/pdf/2306.07402)

---

## 引用格式

arXiv:2306.07402 [cs.CL]

---

## 核心要点总结

1. **应用场景**: 客服自动回复生成
2. **核心问题**: LLM功效与训练/服务成本的平衡
3. **三种策略**: 提示工程、微调、知识蒸馏
4. **关键发现**: 响应有用性可补偿推理成本
5. **实践意义**: 企业LLM部署的成本优化指导
