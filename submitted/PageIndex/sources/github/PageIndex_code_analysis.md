# PageIndex 本地代码分析

## 仓库信息
- **URL**: https://github.com/VectifyAI/PageIndex
- **Clone 路径**: sources/github/PageIndex/
- **分析时间**: 2026-02-12

## 目录结构

```
PageIndex/
├── pageindex/           # 核心代码
│   ├── __init__.py
│   ├── config.yaml      # 配置
│   ├── page_index.py    # PDF 处理主逻辑
│   ├── page_index_md.py # Markdown 处理
│   └── utils.py         # 工具函数
├── cookbook/            # 示例 Jupyter Notebook
│   ├── pageindex_RAG_simple.ipynb     # 无向量 RAG 示例
│   ├── vision_RAG_pageindex.ipynb    # 视觉 RAG
│   ├── agentic_retrieval.ipynb       # Agent 检索
│   └── pageIndex_chat_quickstart.ipynb
├── run_pageindex.py     # CLI 入口
├── requirements.txt
└── tests/
    ├── results/         # 示例树结构 JSON
    └── pdfs/            # 测试 PDF
```

## 依赖分析

- **语言**: Python
- **核心依赖**: OpenAI API (CHATGPT_API_KEY)
- **PDF 处理**: PyMuPDF (fitz)
- **异步**: asyncio, concurrent.futures

## 核心模块清单

| 文件 | 模块 | 功能说明 |
|------|------|---------|
| run_pageindex.py | CLI | 命令行入口，解析 PDF/Markdown |
| pageindex/page_index.py | 核心引擎 | PDF 树解析、TOC 提取、摘要生成 |
| pageindex/page_index_md.py | Markdown | 基于 # 标题的 Markdown 树构建 |
| pageindex/utils.py | 工具 | LLM 调用、配置加载、JSON 解析 |

## 关键代码片段

### 1. 主入口: page_index_main

**文件**: `pageindex/page_index.py` L1058-L1100

```python
def page_index_main(doc, opt=None):
    # 1. 提取 PDF 页面 tokens
    page_list = get_page_tokens(doc)
    
    # 2. 异步构建树结构
    async def page_index_builder():
        structure = await tree_parser(page_list, opt, doc=doc, logger=logger)
        if opt.if_add_node_id == 'yes':
            write_node_id(structure)
        if opt.if_add_node_summary == 'yes':
            await generate_summaries_for_structure(structure, model=opt.model)
        # ...
    
    return asyncio.run(page_index_builder())
```

### 2. 树解析核心: tree_parser

**文件**: `pageindex/page_index.py` L1021-L1056

```python
async def tree_parser(page_list, opt, doc=None, logger=None):
    # 1. 检测目录
    check_toc_result = check_toc(page_list, opt)
    
    # 2. 根据 TOC 存在与否选择处理模式
    if check_toc_result.get("toc_content") and check_toc_result["page_index_given_in_toc"] == "yes":
        toc_with_page_number = await meta_processor(
            page_list, mode='process_toc_with_page_numbers', ...)
    else:
        toc_with_page_number = await meta_processor(
            page_list, mode='process_no_toc', ...)
    
    # 3. 后处理：添加前言、校验标题、构建树、递归细分大节点
    toc_with_page_number = add_preface_if_needed(toc_with_page_number)
    toc_tree = post_processing(valid_toc_items, len(page_list))
    tasks = [process_large_node_recursively(node, ...) for node in toc_tree]
    await asyncio.gather(*tasks)
    return toc_tree
```

### 3. TOC 检测: toc_detector_single_page

**文件**: `pageindex/page_index.py` L106-L125

使用 LLM 判断给定页面是否包含目录，返回 JSON `{"toc_detected": "yes/no"}`。

### 4. 配置与默认模型

**文件**: `run_pageindex.py` L13

```python
--model: default='gpt-4o-2024-11-20'
--toc-check-pages: default=20
--max-pages-per-node: default=10
--max-tokens-per-node: default=20000
```

## 数据流概览

```
PDF/Markdown 输入
    ↓
get_page_tokens() / md_to_tree()
    ↓
check_toc() → meta_processor() [TOC 提取/无 TOC 推断]
    ↓
post_processing() → 扁平淡平列表转树
    ↓
process_large_node_recursively() → 大节点递归细分
    ↓
generate_summaries_for_structure() → LLM 生成节点摘要
    ↓
JSON 树结构输出
```

## 初步发现

- 强依赖 OpenAI API，无本地模型支持
- PDF 处理分三种模式：有页码 TOC、无页码 TOC、无 TOC（全文档推断）
- 大节点（超过 max_pages/max_tokens）会递归调用 `process_no_toc` 细分
- 支持并行异步生成摘要（`asyncio.gather`）
