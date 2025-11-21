# v0.3.9 Latest
What's Changed
fix(docs): add missing line break so the step title and description a… by @nkch1k in #2391
Migrate SummaryScore by @rhlbhatnagar in #2376
feat: add metadata fields for synthetic data traceability by @dev-jonathan in #2389
Migrate noise sensitivity by @rhlbhatnagar in #2379
docs: quickstart guide with interactive LLM and project structure by @anistark in #2380
Migrate Faithfullness by @rhlbhatnagar in #2384
fix: docs for discrete, numeric and ranking using instructor by @anistark in #2397
Migrate Answer Accuracy + Context Relevance by @rhlbhatnagar in #2390
refactor: remove aspect critic and simple criteria metrics with discrete metric examples by @anistark in #2399
Migrate Context Pricision with + without ref by @rhlbhatnagar in #2398
docs: fix recall formula label in SQL metrics by @tysoncung in #2405
chore: remove deprecated ground_truths by @anistark in #2402
docs: Add documentation for metrics.collections API by @sanjeed5 in #2407
Migrate factual correctness by @rhlbhatnagar in #2401
refactor: remove redundant AnswerSimilarity from collections API in favor of SemanticSimilarity by @anistark in #2410
docs: Update documentation structure to reflect experiments-first paradigm by @sanjeed5 in #2394
Response Groundedness by @rhlbhatnagar in #2403
fix: office hours link update by @anistark in #2415
Refactor/removing deprecated by @anistark in #2412
fix: handle max_completeion_tokens error for newer openai models by @anistark in #2413
refactor: make embeddings optional in AnswerCorrectness when using pure factuality mode by @anistark in #2414
Feat/migrate context recall by @jjmachan in #2372
chore: update quickstart llm config by @anistark in #2417

# v0.3.8
What's Changed
feat: semantic similarity migrated to collections by @anistark in #2361
feat: Add reusable testing infrastructure for metrics migration by @jjmachan in #2370
add: console scripts for ragas_examples by @anistark in #2367
feat: add quickstart cmd with templates to run by @anistark in #2374
fix: detect uvloop and skip nest_asyncio to prevent patching errors by @anistark in #2369
Remove import not used by @ChenyangLi4288 in #2364
Migrate answer_correctness by @rhlbhatnagar in #2365
Migrate context_entity_recall by @rhlbhatnagar in #2366
feat: aspect critic metric for coherence, harmfulness, maliciousness, correctness by @anistark in #2375
Fixed: NameError during evalutation of llamaindex query engine by @Prigoistic in #2331
Remove error suppressor in async_utils.py and engine.py by @ChenyangLi4288 in #2362
docs: clarify Context Relevance implementation differs from paper design by @anistark in #2378
fix: add missing metrics (ToolCallF1, ChrfScore) to sidebar and document deprecated ContextUtilization by @anistark in #2381
refactor: instructor_llm_factory merge with llm_factory by @anistark in #2382
fix: handle tuple-formatted entities in SingleHopSpecificQuerySynthesizer by @anistark in #2377
feat: simple criteria migrated to collections by @anistark in #2386
chore: remove deprecation warnings for LangchainLLMWrapper, LlamaIndexLLMWrapper, and embedding wrappers by @anistark in #2387

# v0.3.7
What's Changed
refactor: improve metrics code quality by @anistark in #2337
chore: remove old analtyics by @jjmachan in #2338
Fix/query distribution robustness by @yatoyun in #2340
Simplify earlier how to guides in docs by @sanjeed5 in #2319
docs: reorganize prompt evaluation guides in navigation by @sanjeed5 in #2346
Metrics migration, migrate rouge + answer relevance by @rhlbhatnagar in #2335
fix: streamline theme extraction from overlaps in MultiHopSpecificQue… by @kenzoyan in #2347
Test/metric new compare by @anistark in #2349
feat: bleu score migrated to collections by @anistark in #2352
fix: Add List[List[str]] formats for overlapped items in theme extration (Continuation in #2347) by @kenzoyan in #2355
feat: string metrics migrated to collections by @anistark in #2356
feat: answer similarity migrated to collections by @anistark in #2358
fix: add missing props token_usage_parser for test generation methods #2359 by @bhkj9999 in #2360
feat: add bypass_n option to LangchainLLMWrapper for n-completion control by @SimFG in #2354
docs: Add how-to guide for aligning LLM-as-Judge by @sanjeed5 in #2348

# v0.3.6
What's Changed
Feature/chrf score by @kauabh in #2221
Fix/asyncio by @anistark in #2294
Fix: update simple RAG init to use embed_text(s) (docs) by @s3pi in #2292
Update _bleu_score.py by @kauabh in #2297
Refactor/update gemini to genai sdk by @sahusiddharth in #2240
Feature/metrics input flexibility by @anistark in #2298
Ensure old_temperature is set correctly. Fixes #1937 and #2110 by @claudepi in #2295
Enhance EmbeddingExtractor to support both async and sync methods for… by @telesoho in #2286
Tokens counting by @anistark in #2299
Fix/tool call accuracy by @anistark in #2300
fix: coroutine warning for bleu by @anistark in #2301
Add base_url parameter to embedding_factor by @anistark in #2303
fix: add disallowed_special on tiktoken encode by @anistark in #2304
Feat/tool call f1 1893 by @anistark in #2305
Feature/azure token usage extraction by @anistark in #2306
fix: improve metric decorators with better validation and error handling by @jjmachan in #2302
Metric/parallel tool call by @anistark in #2307
Fix: avoid ambiguous truth value for empty numpy array in HuggingfaceEmbeddings (fixes #2080) by @Rahul2512Chauhan in #2308
Devpod cn/main by @anistark in #2309
Feat/quoted spans metric by @anistark in #2311
Fix noise sensitivity compute by @anistark in #2312
Corrected numerous typos in Markdown files. by @ker2xu in #1994
Deprecation warnings for LLMs and Prompts by @rhlbhatnagar in #2253
Docs/eval_rag_agent - how to evaluate and improve rag app by @sanjeed5 in #2293
Add llamaindex agentic evals gemini by @anistark in #2317
fix: type str in tests by @anistark in #2318
Fix generate_multiple caching issue (#1980) by @Rahul2512Chauhan in #2314
fix: metric inheritance patterns: separate factory-created metrics from class-instantiated metrics by @jjmachan in #2316
fix: concurrent ResponseRelevancy by @anistark in #2328
fix: answer_relevancy scoring logic to prevent false zero by @anistark in #2327
feat: Add OCI Gen AI Integration for Direct LLM Support by @harshil-sanghvi in #2321
feat: Add save/load functionality and improved repr for LLM-based metrics by @jjmachan in #2320
Fix: Fixed the Numpy 3.13 issue by @Prigoistic in #2282
refactor: docs and warnings for metric base new structure by @anistark in #2333
fix: typing by @anistark in #2334

# v0.3.5
What's Changed
Docs/howto-texttosqlagent by @sanjeed5 in #2264
fix: preview logo was too small. by @anistark in #2277
modified the documentation to be in sync with current output format by @kotalaraghava in #2281
removed some meta properties to test by @jjmachan in #2278
feature: improve async / executor functionality by @ahgraber in #2070
modification of the translate instruction by @anistark in #2284
Remove experimental from docs and fix examples in docs by @sanjeed5 in #2270
fix: resolve TypeError in TopicAdherenceScore bitwise operations by @anistark in #2258
Knowledge graph/optimize for large corpus by @anistark in #2267
Update _nv_metrics.py by @titericz in #2053
Add telemetry by @rhlbhatnagar in #2260
OpenAI model cost by @anistark in #2287
docs: agent metrics code examples improvement by @yesidc in #1983
Prompt Optimization Tutorial by @sahusiddharth in #1993
Feature/metric type checking by @anistark in #2288
improved the release script for ragas-examples by @jjmachan in #2289
fix: removed the need for regex patterns by @jjmachan in #2290

# v0.3.4
What's Changed
Update context_precision.md by @anupamck in #2262
Reduce find_indirect_clusters() runtime through neighborhood detection and sampling by @ahgraber in #2144
fix: handle langchain multiple batching by @anistark in #2257
chore: fix the dead space in the header for docsite by @jjmachan in #2265
total bin coverage for default_transform() in Knowledge Graph transformations by @tolgaerdonmez in #1950
Improved context precision documentation by @anupamck in #2266
Fix docs: correct inheritance class for Non-LLM metrics by @AlanPonnachan in #2272
added rb2b analytics by @jjmachan in #2273