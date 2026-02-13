# PageIndex Leads Financial QA Benchmark | PageIndex

原文链接: https://vectify.ai/blog/Mafin2.5

PageIndex Leads Financial QA Benchmark

Published on
:   Feb 19, 2025

[Mingtian Zhang](https://mingtian.ai)[Yu Tang](https://linkedin.com/in/yu-tang-7b982321)

![image](../../images/42ebe8242cad78d377afeea5e3bca38a.png)

## Introduction

We’re excited to share a real-world application of **PageIndex** in the domain of financial question answering.

**PageIndex** is a reasoning-based retrieval framework that mimics how human experts read, navigate, and extract insights from complex documents. Rather than relying on vector-based semantic similarity search, it transforms documents into hierarchical tree structures and conducts structured tree searches to identify and retrieve the most relevant information.

This approach has proven especially effective in domains like finance, where small semantic differences can lead to incorrect answers.

## PageIndex in Financial Question Answering

Based on **PageIndex**, we built Mafin 2.5 — a state-of-the-art reasoning-based RAG model designed specifically for financial document analysis. It achieved a market-leading [**98.7% accuracy**](https://vectify.ai/blog/Mafin2.5) on the [FinanceBench](https://arxiv.org/abs/2311.11944) benchmark — significantly outperforming traditional vector-based RAG systems.

PageIndex's hierarchical indexing enabled precise navigation and extraction of relevant content from complex financial reports, such as SEC filings and earnings disclosures.

Detailed benchmark results are available in our [**GitHub repo**](https://github.com/VectifyAI/Mafin2.5-FinanceBench).

### **Performance Benchmark**

[**FinanceBench**](https://arxiv.org/pdf/2311.11944) is an industry-standard benchmark designed to evaluate the performance of large language models (LLMs) on financial question answering (QA). It consists of questions about publicly traded companies that require finding answers directly from SEC filings (e.g., 10-K, 10-Q, 8-K). The following table shows some sampled questions from FinanceBench:

| **Ticker** | **Question** |
| --- | --- |
| AMD | Does AMD have a reasonably healthy liquidity profile based on its quick ratio for FY22? If the quick ratio is not relevant to measure liquidity, please state that and explain why. |
| JPM | Which of JPM's business segments had the lowest net revenue in 2021 Q1? |

### **State-of-the-Art Accuracy**

Mafin 2.5 achieves **98.7% accuracy** when tested on the **full benchmark dataset (100%)**, ensuring a more comprehensive and fair evaluation compared to models that only cover 66.7% of the dataset. We have open-sourced our benchmark results in the [**GitHub repo**](https://github.com/VectifyAI/Mafin2.5-FinanceBench).

![summary](../../images/b644dea5638fcc2337de5dd1b466dcbc.jpg)

## Why PageIndex Works Well

Several key factors explain why PageIndex delivers state-of-the-art accuracy in this financial QA use case:

1. **Preservation of Document Structure**

   Financial reports are inherently hierarchical — sections, tables, footnotes, appendices. PageIndex preserves that hierarchy directly, rather than breaking it into artificial text chunks.
2. **Traceable Retrieval**

   Each node in the PageIndex tree may carry metadata (page range, section title), making every retrieval step traceable and explainable.
3. **Reasoning-Driven Search**

   Instead of relying on semantic similarity, PageIndex guides the model to *reason* about where the answer should be — much like how an analyst navigates a 10-K report.

If you work with long, professional domain documents — such as financial reports, legal contracts, or technical manuals — PageIndex enables more precise, transparent, and reliable retrieval.