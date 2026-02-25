# UI-Venus-1.5 调研信息汇总

## 调研信息
- **主题**：UI-Venus-1.5 - 蚂蚁集团/InclusionAI 端到端 GUI Agent
- **调研时间**：2026-02-25
- **数据来源**：技术报告 PDF、GitHub、HuggingFace、arXiv

## 官方资源
| # | 资源 | URL | 类型 |
|---|------|-----|------|
| 1 | GitHub 仓库 | https://github.com/inclusionAI/UI-Venus | 代码 |
| 2 | HuggingFace 模型集 | https://huggingface.co/collections/inclusionAI/ui-venus | 模型 |
| 3 | 技术报告 (arXiv:2602.09082) | https://arxiv.org/abs/2602.09082 | 论文 |
| 4 | VenusBench-GD 基准 | https://ui-venus.github.io/VenusBench-GD/ | 基准 |
| 5 | VenusBench-Mobile 分支 | https://github.com/inclusionAI/UI-Venus/tree/VenusBench-Mobile | 基准 |

## 模型变体
| 模型 | 参数量 | 类型 | HuggingFace |
|------|--------|------|-------------|
| UI-Venus-1.5-2B | 2B | Dense | inclusionAI/UI-Venus-1.5-2B |
| UI-Venus-1.5-8B | 8B | Dense | inclusionAI/UI-Venus-1.5-8B |
| UI-Venus-1.5-30B-A3B | 30B | MoE | inclusionAI/UI-Venus-1.5-30B-A3B |

## 关键发现摘要
- **机构**：Venus Team, Ant Group (蚂蚁集团) / InclusionAI
- **发布时间**：2026年2月
- **基座模型**：Qwen3-VL 系列
- **三大技术突破**：Mid-Training、Online RL、Model Merging
- **SOTA 基准**：ScreenSpot-Pro 69.6%、VenusBench-GD 75.0%、AndroidWorld 77.6%
- **中文应用**：支持 40+ 主流中文 App（微博、小红书、淘宝、美团、B站、支付宝等）
- **Venus Framework**：完整 Android 自动化框架，支持单任务、多设备并行、轨迹录制回放

## codecoze-research-agent 调用说明
- `deep_research`：因递归限制 (recursion_limit 25) 未完成
- `web_search`：需配置 COZE_WORKLOAD_IDENTITY_API_KEY 或 BOCHA_API_KEY
- `crawl_github`：对 inclusionAI/UI-Venus 返回空结果
- 本报告基于技术报告 PDF、网页抓取、GitHub/HuggingFace/arXiv 内容手动整理
