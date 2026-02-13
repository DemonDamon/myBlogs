# GitHub - VectifyAI/PageIndex: 📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG

原文链接: https://github.com/VectifyAI/PageIndex

[VectifyAI](/VectifyAI)
/
**[PageIndex](/VectifyAI/PageIndex)**
Public

* [Notifications](/login?return_to=%2FVectifyAI%2FPageIndex) You must be signed in to change notification settings
* [Fork
  1.1k](/login?return_to=%2FVectifyAI%2FPageIndex)
* [Star
   14.8k](/login?return_to=%2FVectifyAI%2FPageIndex)

📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG

[pageindex.ai](https://pageindex.ai "https://pageindex.ai")

### License

[MIT license](/VectifyAI/PageIndex/blob/main/LICENSE)

[14.8k
stars](/VectifyAI/PageIndex/stargazers) [1.1k
forks](/VectifyAI/PageIndex/forks) [Branches](/VectifyAI/PageIndex/branches) [Tags](/VectifyAI/PageIndex/tags) [Activity](/VectifyAI/PageIndex/activity)

[Star](/login?return_to=%2FVectifyAI%2FPageIndex)

[Notifications](/login?return_to=%2FVectifyAI%2FPageIndex) You must be signed in to change notification settings

# VectifyAI/PageIndex

main

[Branches](/VectifyAI/PageIndex/branches)[Tags](/VectifyAI/PageIndex/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | | Name | Last commit message | Last commit date |
| --- | --- | --- | --- | --- |
| Latest commit   History[234 Commits](/VectifyAI/PageIndex/commits/main/)   234 Commits | | |
| [cookbook](/VectifyAI/PageIndex/tree/main/cookbook "cookbook") | | [cookbook](/VectifyAI/PageIndex/tree/main/cookbook "cookbook") |  |  |
| [pageindex](/VectifyAI/PageIndex/tree/main/pageindex "pageindex") | | [pageindex](/VectifyAI/PageIndex/tree/main/pageindex "pageindex") |  |  |
| [tests](/VectifyAI/PageIndex/tree/main/tests "tests") | | [tests](/VectifyAI/PageIndex/tree/main/tests "tests") |  |  |
| [tutorials](/VectifyAI/PageIndex/tree/main/tutorials "tutorials") | | [tutorials](/VectifyAI/PageIndex/tree/main/tutorials "tutorials") |  |  |
| [.gitattributes](/VectifyAI/PageIndex/blob/main/.gitattributes ".gitattributes") | | [.gitattributes](/VectifyAI/PageIndex/blob/main/.gitattributes ".gitattributes") |  |  |
| [.gitignore](/VectifyAI/PageIndex/blob/main/.gitignore ".gitignore") | | [.gitignore](/VectifyAI/PageIndex/blob/main/.gitignore ".gitignore") |  |  |
| [CHANGELOG.md](/VectifyAI/PageIndex/blob/main/CHANGELOG.md "CHANGELOG.md") | | [CHANGELOG.md](/VectifyAI/PageIndex/blob/main/CHANGELOG.md "CHANGELOG.md") |  |  |
| [LICENSE](/VectifyAI/PageIndex/blob/main/LICENSE "LICENSE") | | [LICENSE](/VectifyAI/PageIndex/blob/main/LICENSE "LICENSE") |  |  |
| [README.md](/VectifyAI/PageIndex/blob/main/README.md "README.md") | | [README.md](/VectifyAI/PageIndex/blob/main/README.md "README.md") |  |  |
| [requirements.txt](/VectifyAI/PageIndex/blob/main/requirements.txt "requirements.txt") | | [requirements.txt](/VectifyAI/PageIndex/blob/main/requirements.txt "requirements.txt") |  |  |
| [run\_pageindex.py](/VectifyAI/PageIndex/blob/main/run_pageindex.py "run_pageindex.py") | | [run\_pageindex.py](/VectifyAI/PageIndex/blob/main/run_pageindex.py "run_pageindex.py") |  |  |
| View all files | | |

## Repository files navigation

[![PageIndex Banner](../../images/18282b0dae230c64b38e0e3a0d5ec912.png)](../../images/7fc9f1b46196e1febde231ee6590bf29.jpg)



[![VectifyAI%2FPageIndex | Trendshift](../../images/6fc8cbc01205952404e24c0b09ae48a4.jpg)](../../images/ada9384e9a6a42d724997ee4290c67f4.jpg)

# PageIndex: Vectorless, Reasoning-based RAG

**Reasoning-based RAG  ◦  No Vector DB  ◦  No Chunking  ◦  Human-like Retrieval**

#### [🏠 Homepage](https://vectify.ai)  •   [🖥️ Chat Platform](https://chat.pageindex.ai)  •   [🔌 MCP](https://pageindex.ai/mcp)  •   [📚 Docs](https://docs.pageindex.ai)  •   [💬 Discord](https://discord.com/invite/VuXuf29EUj)  •   [✉️ Contact](https://ii2abc2jejf.typeform.com/to/tK3AXl8T)

### 📢 Latest Updates

**🔥 Releases:**

* [**PageIndex Chat**](https://chat.pageindex.ai): The first human-like document-analysis agent [platform](https://chat.pageindex.ai) built for professional long documents. Can also be integrated via [MCP](https://pageindex.ai/mcp) or [API](https://docs.pageindex.ai/quickstart) (beta).

**📝 Articles:**

* [**PageIndex Framework**](https://pageindex.ai/blog/pageindex-intro): Introduces the PageIndex framework — an *agentic, in-context* *tree index* that enables LLMs to perform *reasoning-based*, *human-like retrieval* over long documents, without vector DB or chunking.

**🧪 Cookbooks:**

* [Vectorless RAG](https://docs.pageindex.ai/cookbook/vectorless-rag-pageindex): A minimal, hands-on example of reasoning-based RAG using PageIndex. No vectors, no chunking, and human-like retrieval.
* [Vision-based Vectorless RAG](https://docs.pageindex.ai/cookbook/vision-rag-pageindex): OCR-free, vision-only RAG with PageIndex's reasoning-native retrieval workflow that works directly over PDF page images.


---

# 📑 Introduction to PageIndex

Are you frustrated with vector database retrieval accuracy for long professional documents? Traditional vector-based RAG relies on semantic *similarity* rather than true *relevance*. But **similarity ≠ relevance** — what we truly need in retrieval is **relevance**, and that requires **reasoning**. When working with professional documents that demand domain expertise and multi-step reasoning, similarity search often falls short.

Inspired by AlphaGo, we propose **[PageIndex](https://vectify.ai/pageindex)** — a **vectorless**, **reasoning-based RAG** system that builds a **hierarchical tree index** from long documents and uses LLMs to **reason** *over that index* for **agentic, context-aware retrieval**.
It simulates how *human experts* navigate and extract knowledge from complex documents through *tree search*, enabling LLMs to *think* and *reason* their way to the most relevant document sections. PageIndex performs retrieval in two steps:

1. Generate a “Table-of-Contents” **tree structure index** of documents
2. Perform reasoning-based retrieval through **tree search**

[![](../../images/5c48fa52a8e17af473162932146e7934.jpg)](https://pageindex.ai/blog/pageindex-intro "The PageIndex Framework")

### 🎯 Core Features

Compared to traditional vector-based RAG, **PageIndex** features:

* **No Vector DB**: Uses document structure and LLM reasoning for retrieval, instead of vector similarity search.
* **No Chunking**: Documents are organized into natural sections, not artificial chunks.
* **Human-like Retrieval**: Simulates how human experts navigate and extract knowledge from complex documents.
* **Better Explainability and Traceability**: Retrieval is based on reasoning — traceable and interpretable, with page and section references. No more opaque, approximate vector search (“vibe retrieval”).

PageIndex powers a reasoning-based RAG system that achieved **state-of-the-art** [98.7% accuracy](https://github.com/VectifyAI/Mafin2.5-FinanceBench) on FinanceBench, demonstrating superior performance over vector-based RAG solutions in professional document analysis (see our [blog post](https://vectify.ai/blog/Mafin2.5) for details).

### 📍 Explore PageIndex

To learn more, please see a detailed introduction of the [PageIndex framework](https://pageindex.ai/blog/pageindex-intro). Check out this GitHub repo for open-source code, and the [cookbooks](https://docs.pageindex.ai/cookbook), [tutorials](https://docs.pageindex.ai/tutorials), and [blog](https://pageindex.ai/blog) for additional usage guides and examples.

The PageIndex service is available as a ChatGPT-style [chat platform](https://chat.pageindex.ai), or can be integrated via [MCP](https://pageindex.ai/mcp) or [API](https://docs.pageindex.ai/quickstart).

### 🛠️ Deployment Options

* Self-host — run locally with this open-source repo.
* Cloud Service — try instantly with our [Chat Platform](https://chat.pageindex.ai/), or integrate with [MCP](https://pageindex.ai/mcp) or [API](https://docs.pageindex.ai/quickstart).
* *Enterprise* — private or on-prem deployment. [Contact us](https://ii2abc2jejf.typeform.com/to/tK3AXl8T) or [book a demo](https://calendly.com/pageindex/meet) for more details.

### 🧪 Quick Hands-on

* Try the [**Vectorless RAG**](https://github.com/VectifyAI/PageIndex/blob/main/cookbook/pageindex_RAG_simple.ipynb) notebook — a *minimal*, hands-on example of reasoning-based RAG using PageIndex.
* Experiment with [*Vision-based Vectorless RAG*](https://github.com/VectifyAI/PageIndex/blob/main/cookbook/vision_RAG_pageindex.ipynb) — no OCR; a minimal, reasoning-native RAG pipeline that works directly over page images.

[![Open in Colab: Vectorless RAG](../../images/ab1c80f33a3a9379a2edb08633caebf2.jpg)](../../images/7f98b1ae562a4baf3cf0d650f82e1a35.jpg)

[![Open in Colab: Vision RAG](../../images/27b50962e06b13b59389f4098e529165.jpg)](../../images/9c82ca0d1671e92ea37d36d35393f34a.jpg)

---

# 🌲 PageIndex Tree Structure

PageIndex can transform lengthy PDF documents into a semantic **tree structure**, similar to a *"table of contents"* but optimized for use with Large Language Models (LLMs). It's ideal for: financial reports, regulatory filings, academic textbooks, legal or technical manuals, and any document that exceeds LLM context limits.

Below is an example PageIndex tree structure. Also see more example [documents](https://github.com/VectifyAI/PageIndex/tree/main/tests/pdfs) and generated [tree structures](https://github.com/VectifyAI/PageIndex/tree/main/tests/results).

```

...
{
  "title": "Financial Stability",
  "node_id": "0006",
  "start_index": 21,
  "end_index": 22,
  "summary": "The Federal Reserve ...",
  "nodes": [
    {
      "title": "Monitoring Financial Vulnerabilities",
      "node_id": "0007",
      "start_index": 22,
      "end_index": 28,
      "summary": "The Federal Reserve's monitoring ..."
    },
    {
      "title": "Domestic and International Cooperation and Coordination",
      "node_id": "0008",
      "start_index": 28,
      "end_index": 31,
      "summary": "In 2023, the Federal Reserve collaborated ..."
    }
  ]
}
...

```

You can generate the PageIndex tree structure with this open-source repo, or use our [API](https://docs.pageindex.ai/quickstart)

---

# ⚙️ Package Usage

You can follow these steps to generate a PageIndex tree from a PDF document.

### 1. Install dependencies

```

pip3 install --upgrade -r requirements.txt

```

### 2. Set your OpenAI API key

Create a `.env` file in the root directory and add your API key:

```

CHATGPT_API_KEY=your_openai_key_here

```

### 3. Run PageIndex on your PDF

```

python3 run_pageindex.py --pdf_path /path/to/your/document.pdf

```

**Optional parameters**

You can customize the processing with additional optional arguments:

```

--model                 OpenAI model to use (default: gpt-4o-2024-11-20)
--toc-check-pages       Pages to check for table of contents (default: 20)
--max-pages-per-node    Max pages per node (default: 10)
--max-tokens-per-node   Max tokens per node (default: 20000)
--if-add-node-id        Add node ID (yes/no, default: yes)
--if-add-node-summary   Add node summary (yes/no, default: yes)
--if-add-doc-description Add doc description (yes/no, default: yes)

```


**Markdown support**

We also provide markdown support for PageIndex. You can use the `-md\_path` flag to generate a tree structure for a markdown file.

```

python3 run_pageindex.py --md_path /path/to/your/document.md

```

> Note: in this function, we use "#" to determine node heading and their levels. For example, "##" is level 2, "###" is level 3, etc. Make sure your markdown file is formatted correctly. If your Markdown file was converted from a PDF or HTML, we don't recommend using this function, since most existing conversion tools cannot preserve the original hierarchy. Instead, use our [PageIndex OCR](https://pageindex.ai/blog/ocr), which is designed to preserve the original hierarchy, to convert the PDF to a markdown file and then use this function.


---

# 📈 Case Study: PageIndex Leads Finance QA Benchmark

[Mafin 2.5](https://vectify.ai/mafin) is a reasoning-based RAG system for financial document analysis, powered by **PageIndex**. It achieved a state-of-the-art [**98.7% accuracy**](https://vectify.ai/blog/Mafin2.5) on the [FinanceBench](https://arxiv.org/abs/2311.11944) benchmark, significantly outperforming traditional vector-based RAG systems.

PageIndex's hierarchical indexing and reasoning-driven retrieval enable precise navigation and extraction of relevant context from complex financial reports, such as SEC filings and earnings disclosures.

Explore the full [benchmark results](https://github.com/VectifyAI/Mafin2.5-FinanceBench) and our [blog post](https://vectify.ai/blog/Mafin2.5) for detailed comparisons and performance metrics.

[![](../../images/21ebe3d375a5703e0452fb22a869720e.png)](../../images/e19fb3f9cfb0c757637fe1dd93124dbc.jpg)

---

# 🧭 Resources

* 🧪 [Cookbooks](https://docs.pageindex.ai/cookbook/vectorless-rag-pageindex): hands-on, runnable examples and advanced use cases.
* 📖 [Tutorials](https://docs.pageindex.ai/doc-search): practical guides and strategies, including *Document Search* and *Tree Search*.
* 📝 [Blog](https://pageindex.ai/blog): technical articles, research insights, and product updates.
* 🔌 [MCP setup](https://pageindex.ai/mcp#quick-setup) & [API docs](https://docs.pageindex.ai/quickstart): integration details and configuration options.

---

# ⭐ Support Us

Please cite this work as:

```

Mingtian Zhang, Yu Tang and PageIndex Team,
"PageIndex: Next-Generation Vectorless, Reasoning-based RAG",
PageIndex Blog, Sep 2025.

```

Or use the BibTeX citation:

```

@article{zhang2025pageindex,
  author = {Mingtian Zhang and Yu Tang and PageIndex Team},
  title = {PageIndex: Next-Generation Vectorless, Reasoning-based RAG},
  journal = {PageIndex Blog},
  year = {2025},
  month = {September},
  note = {https://pageindex.ai/blog/pageindex-intro},
}

```

Leave us a star 🌟 if you like our project. Thank you!

[![](https://private-user-images.githubusercontent.com/13518252/481667856-eae4ff38-48ae-4a7c-b19f-eab81201d794.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzA4NjY5MDQsIm5iZiI6MTc3MDg2NjYwNCwicGF0aCI6Ii8xMzUxODI1Mi80ODE2Njc4NTYtZWFlNGZmMzgtNDhhZS00YTdjLWIxOWYtZWFiODEyMDFkNzk0LmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjEyVDAzMjMyNFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWNmYzkyY2E5Zjk3NWIyZDQyOGFkNDE5OTU5ZGRiMDFmYTZhZTQzMTUwOGJiNTM3MmMzYmZhZTg4NWRlY2NhMGYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.uf3SZhYHh3TYnfckUGwb95_l8zurNVRCSfmKeXnG38M)](https://private-user-images.githubusercontent.com/13518252/481667856-eae4ff38-48ae-4a7c-b19f-eab81201d794.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzA4NjY5MDQsIm5iZiI6MTc3MDg2NjYwNCwicGF0aCI6Ii8xMzUxODI1Mi80ODE2Njc4NTYtZWFlNGZmMzgtNDhhZS00YTdjLWIxOWYtZWFiODEyMDFkNzk0LmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjEyVDAzMjMyNFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWNmYzkyY2E5Zjk3NWIyZDQyOGFkNDE5OTU5ZGRiMDFmYTZhZTQzMTUwOGJiNTM3MmMzYmZhZTg4NWRlY2NhMGYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.uf3SZhYHh3TYnfckUGwb95_l8zurNVRCSfmKeXnG38M)

### Connect with Us

[![Twitter](../../images/49a213717bed6388d0fe96bcfd5a9898.jpg)](../../images/9cccdb302bb0a99879b31cef18cc9a67.jpg)
[![LinkedIn](../../images/54ac7a19e8a54312b3530a93e43f758b.jpg)](https://www.linkedin.com/company/vectify-ai/)
[![Discord](../../images/b31a4d46324522c031e275c116f71573.jpg)](../../images/a2eea2948e503e2eb20adec296769544.jpg)
[![Contact Us](../../images/144de845b5d3aaab51d190f0d606d984.jpg)](../../images/934242a8ef707d84e063e9778105622f.jpg)

---

© 2025 [Vectify AI](https://vectify.ai)

## About

📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG

[pageindex.ai](https://pageindex.ai "https://pageindex.ai")

### Topics

[agent](/topics/agent "Topic: agent")
[ai](/topics/ai "Topic: ai")
[retrieval](/topics/retrieval "Topic: retrieval")
[reasoning](/topics/reasoning "Topic: reasoning")
[rag](/topics/rag "Topic: rag")
[llm](/topics/llm "Topic: llm")
[agentic-ai](/topics/agentic-ai "Topic: agentic-ai")
[context-engineering](/topics/context-engineering "Topic: context-engineering")

### Resources

[Readme](#readme-ov-file)

### License

[MIT license](#MIT-1-ov-file)

### Uh oh!

There was an error while loading. Please reload this page.

[Activity](/VectifyAI/PageIndex/activity)

[Custom properties](/VectifyAI/PageIndex/custom-properties)

### Stars

[**14.8k**
stars](/VectifyAI/PageIndex/stargazers)

### Watchers

[**74**
watching](/VectifyAI/PageIndex/watchers)

### Forks

[**1.1k**
forks](/VectifyAI/PageIndex/forks)

[Report repository](/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FVectifyAI%2FPageIndex&report=VectifyAI+%28user%29)

## [Releases](/VectifyAI/PageIndex/releases)

No releases published

## [Packages 0](/orgs/VectifyAI/packages?repo_name=PageIndex)

No packages published

### Uh oh!

There was an error while loading. Please reload this page.

## [Contributors 3](/VectifyAI/PageIndex/graphs/contributors)

### Uh oh!

There was an error while loading. Please reload this page.

## Languages

* [Python
  100.0%](/VectifyAI/PageIndex/search?l=python)