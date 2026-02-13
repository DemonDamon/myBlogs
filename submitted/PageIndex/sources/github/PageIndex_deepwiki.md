# PageIndex DeepWiki 研究记录

## 仓库信息
- **URL**: https://github.com/VectifyAI/PageIndex
- **研究时间**: 2026-02-12

## 文档结构

- 1 PageIndex Overview (Installation, Getting Started, Core Concepts, Version History)
- 2 System Architecture (Core Components, Document Processing Pipeline, Data Model, Configuration, Cloud vs Self-Hosted)
- 3 Technical Implementation (PDF/MD Processing, TOC Extraction, Tree Generation, LLM Integration)
- 4 Usage & Examples (CLI, Cloud API, Cookbooks, MCP Integration)
- 5 Retrieval Methods (Tree-Based Search, Metadata, Semantics)

## 问答记录

### Q1: What is PageIndex? What is its core architecture and main components?

**A1**: PageIndex 是无向量、基于推理的 RAG 系统，将长文档转换为层级树结构，用 LLM 在树上进行推理式检索，模拟人类专家阅读文档的方式。

**核心架构**：
- **树结构**：每个节点含 title, node_id, start_index, end_index, summary, prefix_summary, text, nodes(子节点)
- **节点类型**：叶节点（無子节点，有 summary）与父节点（有 nodes 和 prefix_summary）
- **处理路径**：PDF（TOC 检测→页码映射→校验→递归细分）与 Markdown（正则提取标题→栈构建树）
- **丰富字段**：node_id、摘要、文档描述、节点全文

### Q2: How does the PDF processing pipeline work?

**A2**: 由 `tree_parser()` 编排：

1. **TOC 检测**：`check_toc()` → `find_toc_pages()` → `toc_detector_single_page()` 逐页判断
2. **meta_processor 三种模式**：
   - `process_toc_with_page_numbers`：TOC 有页码 → toc_transformer → toc_index_extractor → verify_toc
   - `process_no_toc`：无 TOC → generate_toc_init → generate_toc_continue
   - `process_toc_no_page_numbers`：TOC 无页码 → toc_transformer → add_page_number_to_toc
3. **后处理**：add_preface_if_needed → post_processing（扁平淡平转树）→ process_large_node_recursively（大节点细分）
4. **可选丰富**：write_node_id、generate_summaries_for_structure、doc_description

### Q3: What LLM models are supported? How does tree-based search work?

**A3**: 
- **模型**：默认 gpt-4o-2024-11-20，可通过 `--model` 指定；视觉 RAG 使用 GPT-4.1 等多模态模型
- **树搜索**：LLM 根据问题与树结构（标题、摘要）推理相关 node_id → 提取节点内容 → 作为上下文生成答案

### Q4: What are the limitations and when would it not work well?

**A4**: 
- **文档结构依赖**：需有清晰层级（财报、法规、教材、手册）；无结构或结构混乱效果差
- **Markdown 转化**：从 PDF/HTML 转来的 MD 若未保留层级，需用 PageIndex OCR
- **大文档处理时延**：云端异步处理，超大文档需轮询完成状态
- **LLM 依赖**：检索与答案质量依赖所用 LLM
- **不适用场景**：无结构文档、需实时处理原始数据、强数据隐私且不能上云、信息主要在复杂图表中
