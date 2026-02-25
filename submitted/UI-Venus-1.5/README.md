# UI-Venus-1.5 深度调研

蚂蚁集团 Venus Team（InclusionAI）端到端 GUI Agent 的深度调研资料。

## 目录结构

```
UI-Venus-1.5/
├── README.md                    # 本说明
├── blog.md                      # 图文并茂的深度技术博客
├── blog.md.backup               # 旧版博客备份
├── images/                      # 论文原图（15 张）
│   ├── paper_figure_1~8.png    # Figure 1-8（系统概览、流程图、架构图等）
│   └── paper_table_1~8.png     # Table 1-8（基准对比表格）
├── sources/
│   ├── search_summary.md       # 调研信息汇总
│   └── web/                     # 爬取的网页资料（90+ 篇）
├── generated/
│   └── visual_prompts/          # 视觉描述提示词（备用）
└── UI-Venus-1.5 Technical Report 2026.02.09.pdf-*/
    └── full.md                  # 技术报告 PDF 转 Markdown 全文
```

## 博客配图清单

| 图片 | 内容 | 对应章节 |
|------|------|----------|
| paper_figure_1.png | SOTA 雷达图 + 柱状图 | 七、基准测试 |
| paper_figure_2.png | 系统概览 + 轨迹实例 | 二、系统概览 |
| paper_figure_3.png | 四阶段训练流水线 | 三、训练流程 |
| paper_figure_4.png | Mid-Training 数据分布 + 精炼流程 | 四、Mid-Training |
| paper_figure_5.png | DaaS 数据生成循环 | 四、Mid-Training |
| paper_figure_6.png | Step vs. Trace 准确率分析 | 五、强化学习 |
| paper_figure_7.png | DaaS 平台工程架构 | 五、强化学习 |
| paper_figure_8.png | 潜在空间可视化对比 | 四、Mid-Training |
| paper_table_1.png | Grounding 基准对比 | 七、基准测试 |
| paper_table_2.png | AndroidWorld 基准 | 七、基准测试 |
| paper_table_3.png | AndroidLab 基准 | 七、基准测试 |
| paper_table_4.png | VenusBench-Mobile 基准 | 七、基准测试 |
| paper_table_5.png | WebVoyager 基准 | 七、基准测试 |
| paper_table_7.png | 四阶段消融实验 | 六、Model Merging |
| paper_table_8.png | 动作空间定义 | 二、系统概览 |

## 核心结论

- **三大突破**：Mid-Training（10B tokens）、Online RL（GRPO + DaaS）、Model Merging（TIES-Merge）
- **SOTA 基准**：ScreenSpot-Pro 69.6%、VenusBench-GD 75.0%、AndroidWorld 77.6%
- **中文生态**：40+ App，含微博、小红书、淘宝、美团、B站、支付宝等
- **规模效率**：8B 模型已超越上代 72B

## 官方链接

- [GitHub](https://github.com/inclusionAI/UI-Venus)
- [HuggingFace](https://huggingface.co/collections/inclusionAI/ui-venus)
- [arXiv:2602.09082](https://arxiv.org/abs/2602.09082)
- [项目官网](https://ui-venus.github.io/UI-Venus-1.5/)
