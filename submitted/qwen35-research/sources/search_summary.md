# Qwen 3.5 研究搜索摘要

研究时间: 2026-02-16
主题: Qwen 3.5 (通义千问3.5)

## 一、核心发布信息

**发布时间**: 2026年2月16日（除夕夜）
**首发模型**: Qwen3.5-397B-A17B
**开源协议**: Apache 2.0

**关键规格**:
- 总参数量: 3970亿 (397B)
- 激活参数: 170亿 (A17B)
- 上下文窗口: 1M tokens (约2小时视频)
- 部署显存: 比Qwen3-Max降低60%
- 推理吞吐: 最高提升19倍
- API定价: 0.8元/百万Token

## 二、架构创新

### 2.1 Gated Delta Networks (GDN)
- 线性注意力机制
- 稀疏混合专家(MoE)架构
- 大模型质量，小模型成本

### 2.2 原生多模态
- 从预训练预段就联合学习文本+视觉tokens
- 非后期外挂视觉模块
- 视觉和语言在同一参数空间融合

### 2.3 原生多Token预测
- 训练时学习对后续多个位置联合预测
- 推理时一次输出多个token
- 推理速度接近翻倍

### 2.4 语言支持
- 语言/方言: 从119种扩展到201种
- 词表规模: 扩大到25万
词表编码效率提升10%-60%

## 三、性能评测

### 3.1 通用能力
- MMLU-Pro: 87.8 (超GPT-5.2的87.4)
- GPQA: 88.4 (超Claude Opus 4.5的87.0)
- IFBench: 76.5 (刷新全模型纪录，指令遵循能力)
- MMMLU: 88.5 (29种语言)

### 3.2 视觉能力（四项STEM视觉推理第一）
- MathVision: 88.6
- We-Math: 87.9
- MathVista: 90.3
- ZEROBench: 12分

### 3.3 文档OCR能力（三项第一）
- OmniDocBench: 90.8
- OCRBench: 93.1
- CC-OCR: 82.0

### 3.4 效率对比
- 32K上下文: 吞吐量是Qwen3-Max的8.6倍
- 256K上下文: 吞吐量是Qwen3-Max的19倍
- 相比Qwen3-235B-A22B: 提升3.5倍和7.2倍

## 四、高价值URL列表（待爬取）

### 官方/权威文章
1. https://news.qq.com/rain/a/20260216A05T0V00 - Qwen3.5除夕夜炸场详解
2. https://news.qq.com/rain/a/20260216A0602I00 - 千问3.5全网最详细解读
3. https://news.qq.com/rain/a/20260216A059DD00 - 阿里正式发布千问3.5
4. https://www.laohu8.com/news/2507150082 - 阿里巴巴Qwen2.5-Max发布
5. https://new.qq.com/rain/a/20250131A02LSD00 - Qwen2.5-Max性能超越DeepSeek V3

### 技术文档
6. https://doc.damodel.com/profile/best_practice/Qwen3/Qwen3.html - Qwen3部署与使用
7. http://developer.aliyun.com/article/1651031 - Qwen2.5-VL Cookbook视觉模型
8. https://help.aliyun.com/zh/model-studio/ - 阿里云百百API文档

### GitHub/开源
9. https://github.com/QwenLM/Qwen2.5-VL - Qwen2.5-VL官方仓库
10. https://gitcode.com/gh_mirrors/qw/Qwen - Qwen开源项目

### 性能评测
11. https://blog.csdn.net/qq_41472205/article/details/145395159 - Qwen2.5-max性能详细评测
12. https://blog.csdn.net/m0_70486148/article/details/145452520 - Qwen2.5-Max超越DeepSeek-V3

### 对比分析
13. https://zhuanlan.zhihu.com/p/720829906 - Qwen2.5来了，端侧LLM能力更强
14. https://zhuanlan.zhihu.com/p/720879955 - Qwen2.5登全球开源王座
15. https://www.toutiao.com/article/7437231436983222818 - Claude 3.5 Sonnet与GPT-4全面对比

### 工程实践
16. https://developer.aliyun.com/article/1646767 - Qwen模型应用：微调与部署实践
17. https://blog.csdn.net/u014739136/article/details/144029731 - 阿里大模型Qwen2.5本地部署步骤
18. https://community.modelscope.cn/67a33a2382931a478c507df2.html - Qwen2.5-VL Cookbook使用指南

### API调用
19. https://forestlong.blog.csdn.net/article/details/149974745 - Qwen官方API调用使用function call
20. https://blog.csdn.net/weixin_42118737/article/details/138918968 - Qwen调用外部API实现模型增强

## 五、Qwen系列演进

- 2023.04: Qwen1.0发布
- 2023.09: 通过国内大模型备案
- 2023.12: 开源720亿参数模型
- 2024.02: Qwen1.5-110B发布
- 2024.05: Qwen2.5发布，性能提升9%-19%
- 2024.09: Qwen2.5-72B击败Llama3 405B
- 2025.01: Qwen2.5-Max发布，性能超越DeepSeek V3
- 2025.03: QwQ-32B推理模型
- 2025.04: Qwen3发布
- 2026.02: Qwen3.5发布（首款397B-A17B）
