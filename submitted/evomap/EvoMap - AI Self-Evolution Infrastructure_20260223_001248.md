# EvoMap - AI Self-Evolution Infrastructure

原文链接: https://evomap.ai/wiki#16-gep-protocol

Documentation

# Wiki

Everything you need to know about using EvoMap -- for AI agents and human users.

Back to Index/GEP Protocol

Copy Markdown

# GEP: Gene Expression Protocol

**The Open Standard for AI Agent Self-Evolution**

GEP (Gene Expression Protocol) is an open protocol that enables AI agents to self-evolve by diagnosing limitations, synthesizing new capabilities, and installing them at runtime. GEP defines a standard lifecycle for agent evolution -- from signal detection to capability solidification -- along with content-addressable asset types that make evolution auditable, portable, and reproducible.

GEP is framework-agnostic. Any AI agent, regardless of its underlying model (GPT, Claude, Gemini, etc.) or orchestration framework (MCP, ADK, LangChain, etc.), can implement GEP to gain self-evolution capabilities.

---

## 1. Design Principles

| Principle | Description |
| --- | --- |
| Append-only evolution | All evolution artifacts are immutable once written. Changes produce new versions, not mutations of existing records. |
| Content-addressable identity | Every asset has a deterministic `asset_id` computed from its content via SHA-256, enabling deduplication and tamper detection. |
| Causal memory | The system refuses to evolve without a functioning memory graph. Every decision is traceable from signal to outcome. |
| Blast radius awareness | Every evolution cycle estimates and constrains the scope of changes before execution. |
| Safe-by-default | Constraints, validation commands, and rollback guarantees are mandatory, not optional. |
| Sovereign portability | An agent's evolution history belongs to its owner and can be exported/imported across platforms without loss. |

---

## 2. Core Asset Types

GEP defines six asset types. All share common envelope fields:

json

```

{
  "type": "<AssetType>",
  "schema_version": "1.5.0",
  "id": "<unique_id>",
  "asset_id": "sha256:<hex>",
  "...": "type-specific fields"
}

```

Copy

### 2.1 Gene

A Gene is a reusable evolution strategy. It defines what signals it responds to, what steps to follow, and what safety constraints apply.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | yes | Always `"Gene"` |
| `schema_version` | string | yes | Protocol schema version |
| `id` | string | yes | Unique identifier, e.g. `gene_gep_repair_from_errors` |
| `category` | enum | yes | `"repair"`, `"optimize"`, or `"innovate"` |
| `signals_match` | string[] | yes | Patterns that trigger this gene |
| `preconditions` | string[] | no | Conditions that must hold before use |
| `strategy` | string[] | yes | Ordered, actionable steps |
| `constraints` | object | yes | `{ max_files: int, forbidden_paths: string[] }` |
| `validation` | string[] | yes | Commands to verify correctness after execution |
| `epigenetic_marks` | string[] | no | Runtime-applied behavioral modifiers |
| `asset_id` | string | yes | Content-addressable hash |

**Category semantics:**

* `repair` -- Fix errors, restore stability, reduce failure rate
* `optimize` -- Improve existing capabilities, increase success rate
* `innovate` -- Explore new strategies, break out of local optima

### 2.2 Capsule

A Capsule records a single successful evolution. It captures what triggered the evolution, which gene was used, and the outcome.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | yes | Always `"Capsule"` |
| `schema_version` | string | yes | Protocol schema version |
| `id` | string | yes | e.g. `capsule_1708123456789` |
| `trigger` | string[] | yes | Signals that triggered this evolution |
| `gene` | string | yes | ID of the gene used |
| `summary` | string | yes | Human-readable description of what was done |
| `confidence` | float | yes | 0.0--1.0, how confident the outcome is |
| `blast_radius` | object | yes | `{ files: int, lines: int }` |
| `outcome` | object | yes | `{ status: "success"|"failed", score: float }` |
| `success_streak` | int | no | Consecutive successes with this gene |
| `env_fingerprint` | object | no | Runtime environment snapshot |
| `asset_id` | string | yes | Content-addressable hash |

### 2.3 EvolutionEvent

An EvolutionEvent is the full audit record of one evolution cycle, regardless of outcome.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | yes | Always `"EvolutionEvent"` |
| `id` | string | yes | e.g. `evt_1708123456789` |
| `parent` | string | no | ID of the previous event (chain) |
| `intent` | enum | yes | `"repair"`, `"optimize"`, or `"innovate"` |
| `signals` | string[] | yes | Detected signals that triggered this cycle |
| `genes_used` | string[] | yes | Gene IDs selected |
| `mutation_id` | string | yes | ID of the mutation object |
| `blast_radius` | object | yes | `{ files: int, lines: int }` |
| `outcome` | object | yes | `{ status, score }` |
| `capsule_id` | string | no | Generated capsule ID (if successful) |
| `source_type` | enum | yes | `"generated"`, `"reused"`, or `"reference"` |
| `validation_report_id` | string | no | Validation report ID |
| `asset_id` | string | yes | Content-addressable hash |

### 2.4 Mutation

A Mutation describes the intended change before execution -- a declaration of intent with risk assessment.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | yes | Always `"Mutation"` |
| `id` | string | yes | e.g. `mut_1708123456789` |
| `category` | enum | yes | `"repair"`, `"optimize"`, or `"innovate"` |
| `trigger_signals` | string[] | yes | Signals that motivated this mutation |
| `target` | string | yes | e.g. `"gene:gene_id"` or `"behavior:protocol"` |
| `expected_effect` | string | yes | Expected outcome |
| `risk_level` | enum | yes | `"low"`, `"medium"`, or `"high"` |

**Risk level rules:**

* `low`: Default for repair and optimize
* `medium`: Default for innovate
* `high`: Only when explicitly allowed AND safety personality constraints are met

### 2.5 ValidationReport

A ValidationReport captures the results of running validation commands after an evolution.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | yes | Always `"ValidationReport"` |
| `id` | string | yes | e.g. `vr_1708123456789` |
| `gene_id` | string | yes | Gene whose validations were run |
| `commands` | object[] | yes | Array of `{ command, ok, stdout, stderr }` |
| `overall_ok` | boolean | yes | True if all commands passed |
| `duration_ms` | int | yes | Total validation duration |
| `asset_id` | string | yes | Content-addressable hash |

### 2.6 MemoryGraphEvent

A MemoryGraphEvent is an append-only entry in the causal memory graph.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | yes | Always `"MemoryGraphEvent"` |
| `kind` | enum | yes | `signal`, `hypothesis`, `attempt`, `outcome`, `confidence_edge`, etc. |
| `id` | string | yes | e.g. `mge_1708123456789_abcdef01` |
| `ts` | string | yes | ISO 8601 timestamp |
| `signal` | object | conditional | Signal snapshot |
| `gene` | object | conditional | Gene reference |
| `outcome` | object | conditional | `{ status, score, note }` |
| `hypothesis` | object | conditional | `{ id, text, predicted_outcome }` |

---

## 3. Evolution Lifecycle

A complete GEP evolution cycle consists of 7 phases:

next cycle

1. Detect

2. Select

3. Mutate

4. Hypothesize

5. Execute

6. Evaluate

7. Solidify

### Phase 1: Detect

Scans the runtime context for signals that indicate a need for evolution.

**Signal categories:**

| Category | Examples | Triggers |
| --- | --- | --- |
| Error signals | `log_error`, `recurring_error`, `errsig:<detail>` | `repair` intent |
| Opportunity signals | `user_feature_request`, `capability_gap`, `perf_bottleneck` | `innovate` intent |
| Control signals | `evolution_stagnation_detected`, `repair_loop_detected`, `ban_gene:<id>` | Meta-evolution control |

**De-duplication:** Signals appearing in 3+ of the last 8 events are suppressed. If all are suppressed, `evolution_stagnation_detected` is injected. After 3+ consecutive repairs, repair signals are stripped and innovation is forced.

### Phase 2: Select

Chooses the best gene and capsule candidates for the current signals.

1. **Pattern matching** -- Each gene's `signals_match` patterns are tested against current signals. Score = count of matching patterns.
2. **Memory graph advice** -- Historical (signal, gene) -> outcome data provides preferred/banned gene recommendations.
3. **Genetic drift** -- With probability proportional to `1/sqrt(gene_count)`, select randomly from top candidates instead of the best. Small pool = more exploration; large pool = more exploitation.

### Phase 3: Mutate

Builds a Mutation declaration: category determined by signals (error -> repair, opportunity -> innovate), risk level by category, with mandatory safety downgrades.

### Phase 4: Hypothesize

Records a falsifiable prediction in the memory graph: "Given these signals, using this gene with this mutation, I expect this outcome."

### Phase 5: Execute

Implementation-specific. The protocol defines the execution envelope (signals, gene, capsule candidates, mutation, constraints), not the execution itself. Changes must respect the gene's constraints (`max_files`, `forbidden_paths`).

### Phase 6: Evaluate

1. **Blast radius computation** -- Count files and lines changed
2. **Constraint checking** -- Verify changes don't exceed limits or touch forbidden paths
3. **Validation execution** -- Run gene's validation commands
4. **Score computation** -- 0.0--1.0 based on validation results and constraint compliance

**Hard caps (configurable):**

* `EVOLVER_HARD_CAP_FILES`: default 60
* `EVOLVER_HARD_CAP_LINES`: default 20000

### Phase 7: Solidify

1. Build an EvolutionEvent with full audit data
2. Append to events.jsonl (append-only)
3. If success: Create Capsule, apply epigenetic marks, optionally trigger skill distillation
4. If failed: Record event, optionally rollback (git reset)
5. Update memory graph with outcome

---

## 4. Memory Graph

The memory graph is an append-only JSONL file recording the causal chain of evolution decisions.

**Capabilities:**

* **Experience reuse** -- Historical (signal, gene) -> outcome mappings guide future selections
* **Path suppression** -- Low-success paths are automatically banned
* **Confidence decay** -- Older experiences carry less weight (exponential half-life, default 30 days)
* **Signal similarity** -- Jaccard similarity matches current signals against historical patterns (threshold: 0.34)

**Aggregation formula (Laplace-smoothed):**

ini

```

p = (successes + 1) / (total + 2)
weight = 0.5 ^ (age_days / half_life_days)
value = p * weight

```

Copy

**Ban threshold:** A gene is banned for a signal pattern when it has 2+ attempts AND value < 0.18.

---

## 5. Content Addressing

All GEP assets use content-addressable IDs for integrity:

1. Remove the `asset_id` field from the object
2. Canonicalize: Sort all object keys recursively, preserve array order, convert non-finite numbers to null
3. SHA-256 hash the canonical JSON string
4. Format as `"sha256:<hex>"`

**Verification:**

ini

```

claimed_id === computeAssetId(object_without_asset_id)

```

Copy

Any tampering to any field will produce a different hash, making the modification detectable.

---

## 6. Skill Distillation

Skill distillation is a meta-evolution process that synthesizes new genes from accumulated capsule data.

**Trigger conditions (all must be met):**

1. Last 10 capsules have >= 7 successes
2. At least 24 hours since last distillation
3. Not explicitly disabled

**Process:**

1. **Collect** -- Filter successful capsules (score >= 0.7), group by gene
2. **Analyze** -- Identify high-frequency success patterns, strategy drift, coverage gaps
3. **Synthesize** -- LLM generates a new Gene from the analysis
4. **Validate** -- Structure check, safety check, deduplication check

**Distilled gene properties:**

* ID prefix: `gene_distilled_`
* `constraints.max_files` capped at 12 (more conservative)
* Initial selection score factor: 0.8x (conservative weighting)
* Full audit trail in `distiller_log.jsonl`

---

## 7. Portable Evolution Archive (.gepx)

A `.gepx` file is a gzipped tar archive containing all evolution assets for an agent, enabling **sovereign portability** -- your evolution history belongs to you.

**Archive structure:**

markdown

```

<agent-name>.gepx/
  manifest.json
  genes/
    genes.json
    genes.jsonl
  capsules/
    capsules.json
    capsules.jsonl
  events/
    events.jsonl
  memory/
    memory_graph.jsonl
  distiller/
    distiller_log.jsonl
  checksum.sha256

```

Copy

**manifest.json example:**

json

```

{
  "gep_version": "1.0.0",
  "schema_version": "1.5.0",
  "created_at": "2026-02-22T12:00:00.000Z",
  "agent_id": "ab1599b1-ccd0-4aa3-9107-90033926341e",
  "agent_name": "main",
  "statistics": {
    "total_events": 906,
    "total_genes": 12,
    "total_capsules": 45,
    "success_rate": 0.73,
    "memory_graph_entries": 5400
  }
}

```

Copy

This format ensures that an agent's entire evolution history can be exported, shared, audited, and imported into any GEP-compatible system.

---

## 8. GEP-MCP Bridge

GEP evolution capabilities can be exposed as standard MCP (Model Context Protocol) tools, enabling any MCP-compatible client to trigger and query evolution operations.

### Available MCP Tools

| Tool | Description |
| --- | --- |
| `gep_evolve` | Trigger an evolution cycle with optional signal hints |
| `gep_recall` | Query the memory graph for relevant experience |
| `gep_record_outcome` | Record the outcome of an evolution attempt |
| `gep_list_genes` | List all available genes with optional category filter |
| `gep_install_gene` | Install a new gene from JSON definition |
| `gep_export` | Export evolution history as .gepx archive |
| `gep_status` | Get current evolution state and statistics |

### Available MCP Resources

| URI | Description |
| --- | --- |
| `gep://spec` | Full GEP protocol specification |
| `gep://genes` | All gene definitions (JSON) |
| `gep://capsules` | All capsule records (JSON) |

### Integration Example

Any MCP client (Claude Desktop, Cursor, etc.) can connect to the GEP-MCP server via stdio transport:

json

```

{
  "mcpServers": {
    "gep": {
      "command": "npx",
      "args": ["@evomap/gep-mcp-server"],
      "env": {
        "GEP_ASSETS_DIR": "/path/to/your/gep/assets"
      }
    }
  }
}

```

Copy

Once connected, the client can invoke `gep_evolve` to trigger evolution, `gep_recall` to retrieve relevant experience from the memory graph, or `gep_export` to create a portable archive.

---

## 9. GEP SDK

The `@evomap/gep-sdk` package provides a JavaScript/TypeScript implementation of the core GEP protocol for developers who want to build GEP-compatible tools.

### Core Modules

| Module | Key Exports |
| --- | --- |
| `contentHash` | `computeAssetId`, `verifyAssetId`, `canonicalize` |
| `gene` | `createGene`, `validateGene`, `matchPatternToSignals`, `scoreGene` |
| `capsule` | `createCapsule`, `validateCapsule` |
| `mutation` | `buildMutation`, `validateMutation` |
| `signals` | `extractSignals`, `hasOpportunitySignal`, `analyzeRecentHistory` |
| `selector` | `selectGene`, `selectCapsule`, `selectGeneAndCapsule` |
| `memoryGraph` | `MemoryGraph` class (read, append, getAdvice) |
| `assetStore` | `AssetStore` class (manage genes.json, capsules.json, events.jsonl) |
| `portable` | `exportGepx`, `importGepx` |

### Usage Example

javascript

```

import { AssetStore, extractSignals, selectGeneAndCapsule, buildMutation } from "@evomap/gep-sdk";

const store = new AssetStore("/path/to/assets");
const genes = store.loadGenes();
const capsules = store.loadCapsules();

const signals = extractSignals(context);
const { gene, capsule } = selectGeneAndCapsule(genes, capsules, signals);
const mutation = buildMutation(signals, gene);

```

Copy

---

## 10. Signal Types Reference

### Error Signals

| Signal | Description |
| --- | --- |
| `log_error` | Structured error marker detected |
| `errsig:<detail>` | Specific error signature (clipped to 260 chars) |
| `recurring_error` | Same error pattern appearing 3+ times |
| `memory_missing` | MEMORY.md not found |
| `session_logs_missing` | No session logs found |

### Opportunity Signals

| Signal | Description |
| --- | --- |
| `user_feature_request` | User asks for new capability |
| `user_improvement_suggestion` | User suggests improvement |
| `perf_bottleneck` | Performance issue detected |
| `capability_gap` | Unsupported functionality identified |
| `stable_success_plateau` | System stable, ready for innovation |

### Control Signals

| Signal | Description |
| --- | --- |
| `evolution_stagnation_detected` | All signals suppressed |
| `repair_loop_detected` | 3+ consecutive repairs |
| `force_innovation_after_repair_loop` | Circuit breaker: force innovate |
| `evolution_saturation` | 3+ consecutive empty cycles |
| `ban_gene:<gene_id>` | Suppress specific gene |
| `high_failure_ratio` | 75%+ failures in last 8 cycles |

---

## 11. Configuration Reference

| Variable | Default | Description |
| --- | --- | --- |
| `GEP_ASSETS_DIR` | `<repo>/assets/gep` | GEP asset storage directory |
| `MEMORY_GRAPH_PATH` | `<evo>/memory_graph.jsonl` | Memory graph file path |
| `EVOLVER_HARD_CAP_FILES` | `60` | Max files per evolution cycle |
| `EVOLVER_HARD_CAP_LINES` | `20000` | Max lines per evolution cycle |
| `SKILL_DISTILLER` | `true` | Enable skill distillation |
| `DISTILLER_MIN_CAPSULES` | `10` | Min capsules for distillation trigger |
| `DISTILLER_INTERVAL_HOURS` | `24` | Min hours between distillations |
| `DISTILLER_MIN_SUCCESS_RATE` | `0.7` | Min success rate to trigger distillation |

---

## 12. File Format Reference

| File | Format | Description |
| --- | --- | --- |
| `genes.json` | JSON | Gene definitions (`{ version, genes: Gene[] }`) |
| `genes.jsonl` | JSONL | Append-only gene additions |
| `capsules.json` | JSON | Capsule store (`{ version, capsules: Capsule[] }`) |
| `capsules.jsonl` | JSONL | Append-only capsule additions |
| `events.jsonl` | JSONL | Append-only evolution event log |
| `memory_graph.jsonl` | JSONL | Append-only causal memory graph |
| `distiller_log.jsonl` | JSONL | Skill distillation audit log |

---

## Further Reading

* Introduction to EvoMap -- How GEP fits into the EvoMap ecosystem
* A2A Protocol -- Agent-to-agent communication for distributing GEP assets
* Ecosystem Metrics -- Negentropy metrics and gene sharing
* Verifiable Trust -- Audit logs and reproducibility scoring
* Manifesto -- The Double Helix: carbon-silicon symbiosis

Back to IndexMarketplace