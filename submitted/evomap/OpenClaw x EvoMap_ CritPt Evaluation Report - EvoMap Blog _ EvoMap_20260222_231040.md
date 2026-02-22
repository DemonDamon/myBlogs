# OpenClaw x EvoMap: CritPt Evaluation Report - EvoMap Blog | EvoMap

原文链接: https://evomap.ai/blog/openclaw-critpt-report

[Back to blog](/blog)

![OpenClaw x EvoMap: CritPt Evaluation Report](/api/uploads/blog/38131264610715fb.png)

# OpenClaw x EvoMap: CritPt Evaluation Report

February 22, 2026

openclaw critpt evaluation benchmark physics

# OpenClaw x EvoMap: Systematic Evaluation and Evolution Analysis on CritPt Physics Solver

## 1. Executive Summary

This report presents a systematic evaluation and review of OpenClaw (integrated with EvoMap, supporting multi-class gene evolution) on the CritPt Physics Solver benchmark. Our goal is to validate whether EvoMap enables agents like OpenClaw to rapidly learn domain knowledge, complete domain tasks at lower cost, and crystallize high-frequency effective workflows into reusable assets for future expansion.

The conclusion in one sentence: **This evolution chain is a technical roadmap for transforming from a "language imitator" to a "physics simulation engineer" -- the score improvements are not driven by "better language generation" but by engineering reasoning into executable closed loops and progressively solidifying those loops into reusable genes/skills**.

![OpenClaw x EvoMap CritPt evaluation summary](/docs/images/critpt-report-summary.png)

![Evolution chain overview](/docs/images/critpt-report-evolution.png)

## 2. CritPt Benchmark: What Does It Actually Evaluate?

### 2.1 Evaluation Target: "Delivery Pipeline Capability" for Research-Grade Physics Reasoning

In the CritPt Physics Solver scenario, "writing a plausible-looking explanation" does not count as task completion. What matters is delivering a scorable, executable, and verifiable result artifact (typically a Python function output conforming to a template). Therefore, CritPt's evaluation naturally emphasizes:

* Modeling: Can the system formalize physical hypotheses and constraints into computable mathematical structures?
* Implementation: Can it reliably produce runnable code (rather than text alone)?
* Verification: Can it suppress obviously physical inconsistencies through self-checks, assertions, and boundary tests?
* Reliability: Can it maintain stable delivery across multiple runs (rather than getting it right by chance once)?

### 2.2 Two-Step Formatted Answering

A key feature of CritPt is the "two-step delivery": Stage 1 allows free-form reasoning; Stage 2 forces the final answer into a prescribed Python code template (submitting only final code, no explanatory text mixed in), enabling automated grading and scalable evaluation.

![Two-step delivery paradigm](/docs/images/critpt-report-two-step.png)

### 2.3 An Example (Illustrative, Not a Real Problem)

Below is a structurally isomorphic illustration: the key point is that "the deliverable is an executable function", not narrative text.

Sample problem: Return a floating-point number as the final answer (Stage 2 only allows code output).

python

```

def solve():
    import math
    L = 1.0
    g = 9.81
    T = 2.0 * math.pi * math.sqrt(L / g)
    return float(T)

```

Copy

## 3. System Under Test and Version Evolution (Beta -> v2.2)

The system evolution is divided into 5 stages: Beta (v0.x) -> v1.0 -> v2.0 -> v2.1 -> v2.2 (planned). The overall roadmap is to first establish a "decidable artifact pipeline", then progressively solidify "repair/verification/physical plausibility" as default strategies.

![Version evolution roadmap](/docs/images/critpt-report-versions.png)

**Version-Gene Mapping Table**

| Version | Core Objective (Dominant Failure Mode Addressed) | Key Gene (Status) | Representative Capability | Benefits (Observed + Expected) |
| --- | --- | --- | --- | --- |
| Beta | Exposing open-loop text-based problem solving: output is readable but not necessarily decidable, executable, or consistently scorable | (No explicit primary gene) | Text reasoning dominant, lacking structured self-checks and strong-constraint delivery | Observed: established problem exposure baseline; Future value: clarified the "must produce executable results" direction |
| v1.0 | From "can talk" to "can compute": establishing an executable artifact pipeline | gene\_gep\_innovate\_from\_opportunity (validated as primary contributor) | Converting problems into code-solving tasks; forming runnable, submittable result artifacts | Observed: first stable entry into non-zero accuracy range; scorable submission capability established |
| v2.0 | Treating failure as supervision signal: forming a self-correction closed loop | gene\_gep\_repair\_from\_errors (validated as primary contributor) | Code -> Run -> Error -> Fix -> Run iterative repair; minimal reversible patch strategy | Observed: deliverability and robustness continue to improve; accuracy climbing |
| v2.1 | From "can run" to "more stable": emphasizing delivery consistency and runtime steady state | gene\_test\_driven\_development (implicit / recommended for explicit activation) | Assertions/boundary checks/format constraints upfront; lightweight pre-submission self-checks | Observed: accuracy rose to 17.14%; Expected: further reduction in delivery anomalies and grading-side losses |
| v2.2 | From "can compute" to "computes correctly": improving physical validity and knowledge trustworthiness | gene\_active\_research (defined, pending deep activation) | Dimensional consistency checks; uncertain formulas/constants trigger retrieval confirmation; knowledge index crystallization | Observed: current highest accuracy 18.57%; evaluation-side timeout\_rate=0; Expected: reduced formula hallucinations, improved auditability and cross-problem robustness |

**Cross-Version Supporting Genes**

| Gene | Role | Recommended Stage |
| --- | --- | --- |
| gene\_gep\_optimize\_prompt\_and\_assets | Improving consistency and auditability of prompts and asset organization | v1.0-v2.2 all-stage support |
| gene\_web\_fetch\_search\_fallback | Fallback path when retrieval capability is limited, avoiding "blind solving without information" | v2.1-v2.2 enhanced support |
| gene\_memory\_bridge | Cross-session memory bridging, reducing iterative forgetting | All-stage infrastructure layer |

### 3.1 Beta: Open-Loop Language Imitation Stage

The key problem with Beta: the model was primarily doing "text performance", lacking stable verifiable artifact anchors.

As a result, even with significant token consumption, it was prone to losing points due to undecidable answers, non-compliant formatting, or factual hallucinations.

From evaluation results, Beta round accuracy was 0.00%, demonstrating that "being able to answer" does not equal "decidable and scorable".

### 3.2 v1.0 | Proof of Concept (The Innovation): From Text Generation -> Model-Based Reasoning

Core leap: from "directly guessing answers" to "prioritizing production of runnable code and decidable results".

The key gene is gene\_gep\_innovate\_from\_opportunity, with capability focus on:

* Translating problems into executable form;
* Using execution results to replace purely linguistic subjective inference;
* Basic differentiation of failure and anomalous results (success/failure/unavailable).

The primary value of this stage is establishing a "deliverable" baseline, not pursuing high accuracy in a single shot.

### 3.3 v2.0 | Enhanced Feedback Loop: Self-Correction Closed-Loop Repair

Core leap: converting runtime failures into supervision signals, forming a Run -> Error Signal -> Retry/Fix closed loop.

The key gene is gene\_gep\_repair\_from\_errors, with capability focus on:

* Structured recording of failure events;
* Iterative repair with minimal changes;
* Improving "submittable rate / decidability rate" through multiple attempts.

The improvement focus of this stage remains "delivery rate and decidability", not single-shot accuracy per problem.

### 3.4 v2.1 | Robustness Push: From Can-Run to More-Stable, More-Capable

The v2.1 stage demonstrates synergistic optimization of strategy and execution efficiency.

While maintaining deliverable capability, the system's coverage and solving depth for complex problems continued to improve, with evaluation accuracy rising to 17.14%.

This indicates that the evolution mechanism is no longer just fixing "local bugs" but has begun optimizing overall solving quality and benefit structure.

### 3.5 v2.2 | Best-Score Stage: Advancing Toward "Computing Correctly"

v2.2 achieved the current highest evaluation accuracy of 18.57%.

* Evaluation side: timeout\_rate=0, server\_timeout\_count=0 (no grading timeouts);

This demonstrates the system has reached peak-scoring capability. The next step is to further solidify high-score capability into a "high score + stability" dual-excellence capability.

## 4. Results and Diagnostics: Token Trajectories, Cost Metrics, and the "Learned Pattern" Signature

### 4.1 Cost and Token Metrics

![Cost and token analysis](/docs/images/critpt-report-cost.png)

The cost axis in the chart above uses logarithmic scale by default to prevent the $0.81 data point from being compressed near the origin; it can be switched to linear. Cost metric: only considers tokens required to generate answers (thinking + final answer).

### 4.2 Tokens Rise Then Fall: From Explicit Reasoning to Implicit Proceduralization

We observe that tokens first rise then fall -- this is the typical signature of "having learned a pattern" in engineering systems: the system transitions from "explicit reasoning (writing it out)" to "implicit proceduralization (encapsulation and reuse)". This trajectory is not about "the model getting better at talking" but about "reasoning being engineered into executable closed loops", with high-frequency loops progressively crystallized into reusable assets.

Furthermore, the token variation reflects the "explicit expansion process cost": in early stages, workflows are written out in responses (long); in later stages, when workflows are solidified into skills/genes, there is no need to repeat scaffolding and trial-and-error logs in natural language each time, so visible tokens decrease while internal processes become more reliable, and scores actually continue to rise.

![Token trajectory changes](/docs/images/critpt-report-tokens.png)

## 5. Official Evaluation Pipeline (Reproducible, Auditable)

This section clarifies: scores come from the official evaluation pipeline, not from local self-computation.

### 5.1 Submission Generation

Each problem generates an executable Python code segment (generated\_code), written as a submission JSON file by problem ID, with path:

* `results/generations/<RUN_ID>/submissions/<challenge>/<problem_id>.json`

Batch generation command:

bash

```

bash scripts/run_generation.sh

```

Copy

### 5.2 Official Grading Submission

We use the official grading script to submit `<RUN_ID>` submissions as a batch to the Artificial Analysis CritPt evaluation API. The server returns accuracy/timeout metrics; the local side only saves the response. The environment variable `CritPt_API_KEY` must be prepared before submission (the grading script reads from `.openclaw/.env`).

Submission command:

bash

```

bash scripts/run_grading.sh <RUN_ID>

```

Copy

Response file storage path:

* `results/evaluations/<RUN_ID>/aggregate_report.json`

![Official evaluation pipeline](/docs/images/critpt-report-grading.png)

### 5.3 Response Field Interpretation (How to "Read the Numbers")

Key fields commonly found in `aggregate_report.json`:

* `total_files_found`: Number of submission files scanned
* `total_submissions_loaded`: Number of submissions successfully loaded
* `failed_to_load`: List of load failures (empty means all readable)
* `summary.accuracy`: Accuracy rate (0~1 proportion, not percentage; multiply by 100 for percentage)
* `summary.timeout_rate`: Timeout proportion
* (Sometimes) `judge_error_count`: Number of grading errors (commonly caused by non-executable generated code / functions not conforming to template / explanatory text mixed in)

json

```

{
  "timestamp": "2026-02-16T11:59:30.909403",
  "total_files_found": 70,
  "total_submissions_loaded": 70,
  "failed_to_load": [],
  "summary": {
    "total_submissions": 70,
    "accuracy": 0.18571428571428572,
    "timeout_rate": 0,
    "server_timeout_count": 0
  },
  "metrics": {
    "accuracy": 0.18571428571428572,
    "timeout_rate": 0,
    "server_timeout_count": 0,
    "judge_error_count": 1
  }
}

```

Copy

## 6. Why CritPt Was Chosen as the Primary Benchmark (Instead of Math500/AIME)

We chose CritPt as the primary benchmark because it better amplifies the differentiated capabilities of OpenClaw+EvoMap: tool-chain closed loops, engineering robustness, verifiable physical validity, and auditable and reusable evolution assets. Math500/AIME are better suited as supplementary and regression validation.

## 7. Skill / Knowledge / Gene: Asset-Based Explanation ("Why Tokens Are Saved")

For external communication, we recommend using the "Knowledge--Skill--Gene" engineering three-layer abstraction:

* **Knowledge**: Collection of facts and constraints (formulas, common-sense boundaries, tool behavior patterns);
* **Skill**: Executable process modules (modeling, solving, Traceback repair, assertion injection, dimensional checking, etc.);
* **Gene**: Decision biases and workflow orchestration (when to trigger which skills, ordering, thresholds, stopping conditions).

The action chain of these three: Knowledge provides correctness basis -> Skill converts the basis into executable actions -> Gene orchestrates actions into default strategies and reusable structures. One direct engineering benefit is "decreased visible tokens": large amounts of repetitive scaffolding, trial-and-error, and explanatory self-justification are internalized as default workflows, with only the final decidable artifacts output externally. This produces a trajectory signature of "shorter output but higher stability/scores".

## 8. Appendix: Generation Prompt (On Record)

The generation prompt recorded in the report (verbatim):

text

```

Use as many relevant internal skills and strategies as possible.
Think deeply, verify intermediate assumptions, and aim for the best possible final answer.
You may use available tools only when they improve correctness.
Return only final Python answer code with no markdown fences.
If a code template is provided, fill the template directly.

f"Problem ID: {task.problem_id}",
f"Problem type: {task.problem_type}",

"Problem statement:",
task.problem_description.strip()

```

Copy

## 9. Evolution Task Design

![Evolution task architecture](/docs/images/critpt-report-evolution-task.png)

text

```

Primary objective: Maximize accuracy
Secondary objectives: Minimize timeout_rate / judge_error / fallback / generation_failed

Data paths (must use these paths):
1) Problem data (for understanding task distribution):
CritPt/data/public_test_challenges/json/Challenge_*.json

2) Historical official evaluation results:
results/evaluations/*/aggregate_report.json

3) Historical generation summaries:
results/generations/*/run_summary.json

4) Historical score summary table (read first):
/analysis/scoring/scoring_runs.csv

Reward formula (formula_version=v1):

Definitions:
acc = accuracy
to = timeout_rate
jer = judge_error_count / max(total_submissions,1)
gfr = gen_failed / max(gen_total_tasks,1)
fbr = gen_fallback_count / max(gen_total_tasks,1)

Primary reward:
R_main = 100 * (0.88*acc - 0.06*to - 0.03*jer - 0.01*gfr) - 5*fbr

Stability reward:
R_stability = 100 * (0.6*(1-gfr) + 0.4*(1-fbr))

Total reward:
R_total = 0.85*R_main + 0.15*R_stability

```

Copy

[Back to blog](/blog)