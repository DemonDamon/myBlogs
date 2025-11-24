# EverMind AI Sets the New Standard of RAG with EverMemReRank | EverMind Blog

原文链接: https://everm.ai/blog/evermind_ai_sets_the_new_standard_of_rag_with_evermemrerank

# EverMind AI Sets the New Standard of RAG with EverMemReRank

EverMind researchers

Published at October 24, 2025

About 1 minutes to read

#SOTA 
#2wiki 
#Hotpotqa 
#RAG

Part of the EverMemModel modules, the ReRankModel achieves SOTA performance on 2wiki and Hotpotqa.

 

![EverMind AI Sets the New Standard of RAG with EverMemReRank](images/8358edfc863d9c16a7652f16c9cec273.png)

We have integrated a generative ReRankModel into the traditional RAG retrieval framework. By this week, we find it on the right track of performance improvement on key benchmarks.

## Performance on 2wiki benchmark

When compared with **HippoRag2** under identical conditions using Llama3.3 as the LLM for QA, our method achieved a **QA F1 score of 0.758** on the 2wikimultihopqa public benchmark, outperforming HippoRag2 by 4.8 percentage points and reaching SOTA level.

![table 1](images/b5e64b83393a9612f3ec06d99398ddfa.png)

## Performance on Hotpotqa benchmark

On the **HotpotQA** public leaderboard, our model achieves an F1 score of **0.7802**, outperforming **HippoRag2’s 0.755** by 2.5 percentage points and reaching SOTA level.

![table 2](images/b4497cf9d5060f00dc2cbe4dcf292d61.png)