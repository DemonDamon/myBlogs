# PageIndex - Human-like AI for Long Document Understanding

原文链接: https://pageindex.ai/

![](/static/images/new-homepage/bg-elements.svg)

PageIndex

# Human-like Document AI

PageIndex is a vectorless, reasoning-based RAG engine that mirrors how humans read, delivering traceable, explainable, and context-aware retrieval, without vector databases or chunking.

[Try PageIndex](https://chat.pageindex.ai)Book a Demo

![PageIndex chat interface demonstrating reasoning-based document retrieval](/static/images/new-homepage/illustration-chat.svg)

Best for:

[Textbooks](https://chat.pageindex.ai/?doc=textbooks)[Financial Reports](https://chat.pageindex.ai/?doc=financial-reports)[Legal Documents](https://chat.pageindex.ai/?doc=legal-documents)[Technical Manuals](https://chat.pageindex.ai/?doc=technical-manuals)[Medical Files](https://chat.pageindex.ai/?doc=medical-files)[Research Papers](https://chat.pageindex.ai/?doc=research-papers)[Business Plans](https://chat.pageindex.ai/?doc=business-plans)[Textbooks](https://chat.pageindex.ai/?doc=textbooks)[Financial Reports](https://chat.pageindex.ai/?doc=financial-reports)[Legal Documents](https://chat.pageindex.ai/?doc=legal-documents)[Technical Manuals](https://chat.pageindex.ai/?doc=technical-manuals)[Medical Files](https://chat.pageindex.ai/?doc=medical-files)[Research Papers](https://chat.pageindex.ai/?doc=research-papers)[Business Plans](https://chat.pageindex.ai/?doc=business-plans)[Textbooks](https://chat.pageindex.ai/?doc=textbooks)[Financial Reports](https://chat.pageindex.ai/?doc=financial-reports)[Legal Documents](https://chat.pageindex.ai/?doc=legal-documents)[Technical Manuals](https://chat.pageindex.ai/?doc=technical-manuals)[Medical Files](https://chat.pageindex.ai/?doc=medical-files)[Research Papers](https://chat.pageindex.ai/?doc=research-papers)[Business Plans](https://chat.pageindex.ai/?doc=business-plans)

Key Features

01

### Traceable & Explainable

Reasoning-driven retrieval with references

![Traceable & Explainable](/static/images/new-homepage/feature/transparency.svg)

### Traceable & Explainable

Provides traceable and interpretable reasoning steps in retrieval, with clear page and section level references, ensuring transparency, auditability, and trust.

02

![Higher Accuracy](/static/images/new-homepage/feature/document.svg)

### Higher Accuracy

Context relevance beyond similarity

### Higher Accuracy

Delivers precise, context-aware answers by reasoning over document structure, achieving leading accuracy on domain benchmarks.

03

![No Chunking](/static/images/new-homepage/feature/chunking.svg)

### No Chunking

Preserves full context

### No Chunking

Avoids breaking documents into artificial chunks and prevents context fragmentation, preserving the full hierarchical structure so retrieval is context-aware and structure-driven.

04

![No Top-K](/static/images/new-homepage/feature/topk.svg)

### No Top-K

Retrieves all relevant passages

### No Top-K

Retrieves relevant passages based on reasoning, without setting arbitrary top-K thresholds and manual parameter tuning.

05

![No Vector DB](/static/images/new-homepage/feature/vectordb.svg)

### No Vector DB

No extra infra overhead

### No Vector DB

Eliminates the cost and complexity of vector databases — minimal infra overhead, no embeddings pipeline, no external similarity search.

![Human-like Retrieval](/static/images/new-homepage/feature/human.svg)

06

### Human-like Retrieval

Retrieves like a human expert

### Human-like Retrieval

Mimics the human reasoning process of reading and retrieval, allowing the LLM to navigate a table-of-contents-like hierarchical structure to reason and extract information as a human reader would.

[Learn More about PageIndex](/blog/pageindex-intro)

## Key Features

![Traceable & Explainable](/static/images/new-homepage/feature/transparency.svg)

01

### Traceable & Explainable

Reasoning-driven retrieval with references

Learn more

![Higher Accuracy](/static/images/new-homepage/feature/document.svg)

02

### Higher Accuracy

Context relevance beyond similarity

Learn more

![No Chunking](/static/images/new-homepage/feature/chunking.svg)

03

### No Chunking

Preserves full context

Learn more

![No Top-K](/static/images/new-homepage/feature/topk.svg)

04

### No Top-K

Retrieves all relevant passages

Learn more

![No Vector DB](/static/images/new-homepage/feature/vectordb.svg)

05

### No Vector DB

No extra infra overhead

Learn more

![Human-like Retrieval](/static/images/new-homepage/feature/human.svg)

06

### Human-like Retrieval

Retrieves like a human expert

Learn more

[Learn More about PageIndex](/blog/pageindex-intro)

![Background grid](/static/images/new-homepage/grid.svg)

![Background illustration](/static/images/new-homepage/cta-bg-2.svg)

## Want to integrate PageIndex to your LLMs or AI agents?

[Try PageIndex MCP](/mcp)

Introduction

## Introduction

## PageIndex Building Blocks

PageIndex simulates how human experts extract knowledge from long documents. It transforms documents into a tree-structured index and uses LLM reasoning to search the tree index for relevant information.

01

### PageIndex Tree Generation

Generate hierarchical tree-structure index optimized for retrieval

![PageIndex Tree Generation](/static/images/new-homepage/workflow/workflow2.svg)

02

### PageIndex Retrieval

Reasoning-based retrieval by document tree search

![PageIndex Retrieval](/static/images/new-homepage/workflow/workflow3.svg)

[Detailed Introduction of PageIndex](/blog/pageindex-intro)

RAG Comparison

## RAG Comparison

## PageIndex vs Vector DB

Choose the right RAG technique for your task

### PageIndex

Logical Reasoning

![PageIndex reasoning-based document retrieval diagram](/static/images/new-homepage/comparison/pageindex-docs.svg)

#### Best for Domain-Specific Document Analysis

Financial reports and SEC filings

Regulatory and compliance documents

Healthcare and medical reports

Legal contracts and case law

Technical manuals and scientific documentation

##### High Retrieval Accuracy

Relies on logical reasoning, ideal for domain-specific data where semantics are similar.

##### No Time-to-First-Token Delay

Retrieval happens during generation time, allowing immediate streaming of responses without waiting for a separate retrieval phase.

##### Context-Aware Retrieval

Leverages full chat history for relevance classification with LLM, enabling retrieval decisions that adapt to conversational context.

##### Efficient Context-level Knowledge Integration

Easily integrates with expert knowledge and user preferences during the tree search process.

### Vector DB

Semantic Similarity

![Vector DB](/static/images/new-homepage/comparison/vector-db.svg)

#### Best for Generic & Exploratory Applications

Vibe retrieval

Semantic recommendation systems

Creative writing and ideation tools

Short news/email retrieval

Generic knowledge question answering

##### Low Retrieval Accuracy

Relies on semantic similarity, unreliable for domain-specific data where all content has similar semantics.

##### Time-to-First-Token Delay

Retrieval is separate from generation, requiring users to wait for the entire retrieval phase to complete before the response begins streaming.

##### Context-Independent Retrieval

Limited by embedding model input length, unable to incorporate full chat history into retrieval decisions, resulting in context-agnostic search.

##### Knowledge Integration Requires Fine-Tuning

Requires fine-tuning embedding models to incorporate new knowledge or preferences.

Case Study

## Case Study

## PageIndex Leads Industry Benchmarks

PageIndex forms the foundation of Mafin 2.5, a leading RAG system for financial report analysis, achieving 98.7% accuracy on FinanceBench — the highest in the market.

30%

![RAG with single vector index achieving 30% accuracy](/static/images/new-homepage/showcase/box-small.svg)

RAG with Vector DB

One vector index for all the documents.

50%

![RAG with per-document vector index achieving 50% accuracy](/static/images/new-homepage/showcase/box-medium.svg)

RAG with Vector DB

One vector index for each document.

98.7%

![PageIndex achieving 98.7% accuracy on FinanceBench](/static/images/new-homepage/showcase/box-large.svg)

RAG with PageIndex

Query-to-SQL for document-level retrieval, PageIndex for node-level retrieval.

[Benchmark Details](https://github.com/VectifyAI/Mafin2.5-FinanceBench)

![Background grid](/static/images/new-homepage/grid.svg)

![Background illustration](/static/images/new-homepage/cat-bg.svg)

## Human-like Retrieval

No vector DB. No chunking. Just accurate, reasoning-based answers.

[Try Now](https://chat.pageindex.ai)