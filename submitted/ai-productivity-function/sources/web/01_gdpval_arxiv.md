# GDPval: Evaluating AI Model Performance on Real-World Economically Valuable Tasks

**来源**: https://arxiv.org/abs/2510.04374
**爬取时间**: 2026-02-23

---

## 论文信息

**标题**: GDPval: Evaluating AI Model Performance on Real-World Economically Valuable Tasks

**作者**: Tejal Patwardhan, Rachel Dias, Elizabeth Proehl, Grace Kim, Michele Wang, Olivia Watkins, Simón Posada Fishman, Marwan Aljubeh, Phoebe Thacker, Laurance Fauconnet, Natalie S. Kim, Patrick Chao, Samuel Miserendino, Gildas Chabot, David Li, Michael Sharman, Alexandra Barr, Amelia Glaese, Jerry Tworek

**学科**:
- Machine Learning (cs.LG)
- Artificial Intelligence (cs.AI)
- Computers and Society (cs.CY)

**发表时间**: 2025年10月5日

**arXiv ID**: 2510.04374

**DOI**: https://doi.org/10.48550/arXiv.2510.04374

---

## 摘要

我们介绍了GDPval，这是一个在真实世界中具有经济价值的任务上评估AI模型能力的基准。GDPval涵盖了美国劳工统计局所列44个职业中的大部分工作活动，这些职业来自对美国国内生产总值(GDP)贡献最大的前九大行业。任务是基于拥有平均14年经验的行业专业人士的实际工作内容构建而成。

### 主要发现

1. **性能提升趋势**: 我们发现前沿模型在GDPval上的表现随时间大致呈线性提升
2. **接近专家水平**: 当前最先进的模型在交付成果质量方面已接近行业专家水平
3. **人机协作潜力**: 我们分析了前沿模型在辅以人类监督的情况下，完成GDPval任务的成本和速度相较于无辅助的人类专家是否更具优势
4. **性能提升因素**: 我们证明增加推理投入、扩充任务上下文信息以及加强任务结构化支持均能提升模型在GDPval上的表现
5. **开源贡献**: 最后，我们开源了一个包含220项任务的高质量子集，并在evals.openai.com提供公开的自动化评分服务，以促进未来对模型现实世界能力的研究

---

## 核心贡献

### 任务构建方法

- **任务来源**: U.S. Bureau of Labor Statistics Work Activities
- **职业覆盖**: 44个职业
- **行业覆盖**: 对美国GDP贡献最大的前9大行业
- **任务构建依据**: 基于平均14年经验的行业专业人士的实际工作

### 评估维度

1. **任务完成质量**: 可交付成果质量
2. **效率指标**: 成本和速度对比
3. **人机协作**: 模型与人类监督的结合效果

### 影响因素分析

1. **推理投入**: 增加推理能力的影响
2. **上下文信息**: 任务上下文的丰富程度
3. **结构化支持**: 任务结构化的程度

---

## 下载资源

- [查看PDF](/pdf/2510.04374)
- [HTML版本](https://arxiv.org/html/2510.04374v1)
- [自动化评分服务](http://evals.openai.com/)

---

## 引用格式

arXiv:2510.04374 [cs.LG]
或
arXiv:2510.04374v1 (this version)
DOI: https://doi.org/10.48550/arXiv.2510.04374
