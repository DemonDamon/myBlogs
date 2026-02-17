# DeepSeek V4 技术细节与公式推导

本目录包含 DeepSeek V4 相关核心技术的数学公式推导与实现细节，供深入研究者参考。

## 文档索引

| 文档 | 内容 | 关联论文 |
|------|------|----------|
| [01_mHC_流形约束超连接_公式推导.md](./01_mHC_流形约束超连接_公式推导.md) | 残差连接、HC、双随机矩阵、Sinkhorn-Knopp 投影 | arXiv:2512.24880 |
| [02_MLA_多头潜在注意力_公式推导.md](./02_MLA_多头潜在注意力_公式推导.md) | KV 低秩压缩、解耦 RoPE、与 MHA/GQA 对比 | DeepSeek-V2/V3 Report |
| [03_Engram_条件记忆_公式推导.md](./03_Engram_条件记忆_公式推导.md) | N-gram 哈希查表、稀疏分配、U 形扩展律 | Engram Paper (GitHub) |
| [04_MoE_DSA_补充公式.md](./04_MoE_DSA_补充公式.md) | MoE 门控、DSA 稀疏注意力、四维协同 | DeepSeek-V3 Report |

## 论文与资源

- **mHC**: https://arxiv.org/abs/2512.24880
- **Engram**: https://github.com/deepseek-ai/Engram
- **MTLA** (MLA 时序扩展): https://arxiv.org/abs/2505.13544
- **FlashMLA**: https://github.com/deepseek-ai/FlashMLA
