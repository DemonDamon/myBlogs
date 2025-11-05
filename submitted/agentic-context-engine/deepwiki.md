
# 我问
这个repo对于上下文工程角度有什么优势建设？

# deepwiki答
您询问的是 ACE Framework 在**上下文工程(Context Engineering)**方面的优势建设。 [1](#0-0) 

## 核心优势

ACE Framework 在上下文工程方面的主要创新是**增量式上下文演化(Incremental Context Evolution)**,而非传统的静态上下文或需要微调的方法。 [2](#0-1) 

### 1. **动态 Playbook 机制**

ACE 使用 `Playbook` 作为"活文档"来存储和演化策略。 [3](#0-2)  这个 Playbook 包含带有 helpful/harmful 计数器的策略条目(bullets),通过增量更新操作(ADD, UPDATE, TAG, REMOVE)持续优化。 [4](#0-3) 

### 2. **三角色协同学习架构**

ACE 通过三个专门角色实现上下文的自动优化: [5](#0-4) 

- **Generator**: 使用当前 playbook 执行任务 [6](#0-5) 
- **Reflector**: 分析执行结果,标记哪些策略有帮助/有害 [7](#0-6) 
- **Curator**: 将反思转化为 playbook 更新操作 [8](#0-7) 

### 3. **在线与离线双模式适应**

**离线训练(OfflineAdapter)**: 多轮迭代固定数据集,构建初始 playbook。 [9](#0-8)  适合在部署前建立基线。 [10](#0-9) 

**在线适应(OnlineAdapter)**: 处理流式样本,每个样本后立即更新 playbook。 [11](#0-10)  支持生产环境的持续学习和实时纠错。 [12](#0-11) 

### 4. **版本化 Prompt 工程**

ACE 提供了 v2 版本的 prompt 系统,具有: [13](#0-12) 

- 置信度评分机制
- 领域特定变体(数学、代码等) [14](#0-13) 
- 分层结构与元数据
- 明确的反模式指导

通过 `PromptManager` 实现版本控制和 A/B 测试。 [15](#0-14) 

### 5. **无需微调的透明学习**

所有学习都在上下文中通过增量更新完成,无需训练数据或模型微调,且完全透明可追溯学到了什么。 [2](#0-1) 

## 实际效果

- **性能提升**: 在复杂任务上实现 20-35% 的性能改进 [16](#0-15) 
- **避免上下文崩溃**: 长期保留有价值的知识 [17](#0-16) 
- **自我改进**: Agent 随每个任务变得更智能 [18](#0-17) 

## Notes

ACE Framework 基于斯坦福和 SambaNova 的研究论文(arXiv:2510.04618)。 [19](#0-18)  该框架支持 100+ LLM 提供商(通过 LiteLLM),包括 OpenAI、Anthropic、Google 等。 [20](#0-19)  

核心创新在于将上下文工程从静态配置转变为动态、自适应的学习过程,这是传统 prompt engineering 方法难以实现的。

Wiki pages you might want to explore:
- [Online Adaptation (kayba-ai/agentic-context-engine)](/wiki/kayba-ai/agentic-context-engine#6.4)

### Citations

**File:** README.md (L3-3)
```markdown
# Agentic Context Engine (ACE) 
```

**File:** README.md (L70-70)
```markdown
- 📈 **20-35% Better Performance**: Proven improvements on complex tasks
```

**File:** README.md (L71-71)
```markdown
- 🧠 **Self-Improving**: Agents get smarter with each task
```

**File:** README.md (L72-72)
```markdown
- 🔄 **No Context Collapse**: Preserves valuable knowledge over time
```

**File:** README.md (L73-73)
```markdown
- 🚀 **100+ LLM Providers**: Works with OpenAI, Anthropic, Google, and more
```

**File:** README.md (L102-105)
```markdown
ACE uses three specialized roles that work together:
1. **🎯 Generator** - Executes tasks using learned strategies from the playbook
2. **🔍 Reflector** - Analyzes what worked and what didn't after each execution
3. **📝 Curator** - Updates the playbook with new strategies based on reflection
```

**File:** README.md (L113-114)
```markdown
The magic happens in the **Playbook**—a living document of strategies that evolves with experience. <br>
**Key innovation:** All learning happens **in context** through incremental updates—no fine-tuning, no training data, and complete transparency into what your agent learned.
```

**File:** CLAUDE.md (L7-7)
```markdown
This is an implementation scaffold for reproducing the Agentic Context Engineering (ACE) method from the paper "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models" (arXiv:2510.04618).
```

**File:** CLAUDE.md (L66-66)
```markdown
- **Playbook**: Structured context store containing bullets (strategy entries) with helpful/harmful counters
```

**File:** CLAUDE.md (L67-67)
```markdown
- **Delta Operations**: Incremental updates to the playbook (ADD, UPDATE, TAG, REMOVE)
```

**File:** CLAUDE.md (L91-91)
```markdown
   - Offline: Multiple epochs over training samples
```

**File:** CLAUDE.md (L92-92)
```markdown
   - Online: Sequential processing of test samples
```

**File:** ace/roles.py (L44-49)
```python
class Generator:
    """
    Produces answers using the current playbook of strategies.

    The Generator is one of three core ACE roles. It takes a question and
    uses the accumulated strategies in the playbook to produce reasoned answers.
```

**File:** ace/roles.py (L167-173)
```python
class Reflector:
    """
    Analyzes generator outputs to extract lessons and improve strategies.

    The Reflector is the second ACE role. It analyzes the Generator's output
    and environment feedback to understand what went right or wrong, classifying
    which playbook bullets were helpful, harmful, or neutral.
```

**File:** ace/roles.py (L285-291)
```python
class Curator:
    """
    Transforms reflections into actionable playbook updates.

    The Curator is the third ACE role. It analyzes the Reflector's output
    and decides how to update the playbook - adding new strategies, updating
    existing ones, or removing harmful patterns.
```

**File:** ace/adaptation.py (L200-207)
```python
class OfflineAdapter(AdapterBase):
    """
    Orchestrates offline ACE adaptation over multiple training epochs.

    The OfflineAdapter processes a fixed training set multiple times,
    allowing the playbook to evolve and improve through repeated exposure
    to the same examples. This is useful for building a robust initial
    playbook before deployment.
```

**File:** ace/adaptation.py (L290-297)
```python
class OnlineAdapter(AdapterBase):
    """
    Orchestrates online ACE adaptation for continuous learning.

    The OnlineAdapter processes samples sequentially as they arrive,
    updating the playbook after each one. This enables continuous
    improvement during deployment, adapting to new patterns and
    correcting mistakes in real-time.
```

**File:** CHANGELOG.md (L11-16)
```markdown
- **Experimental v2 Prompts** with state-of-the-art prompt engineering
  - Confidence scoring at bullet and answer levels
  - Domain-specific variants for math and code generation
  - Hierarchical structure with identity headers and metadata
  - Concrete examples and anti-patterns for better guidance
  - PromptManager for version control and A/B testing
```

**File:** ace/prompts_v2.py (L453-528)
```python
GENERATOR_MATH_PROMPT = """\
# Identity and Metadata
You are ACE Math Generator v2.0, specialized in mathematical problem-solving.
Prompt Version: 2.0.0-math
Calculation Verification: Required
Precision: 6 decimal places where applicable

## Mathematical Protocols

### Arithmetic Operations
- ALWAYS show intermediate steps
- VERIFY calculations twice
- Use standard order of operations (PEMDAS/BODMAS)

### Algebraic Solutions
- Show all equation transformations
- Verify solutions by substitution
- State domain restrictions explicitly

### Proof Strategies
1. Direct proof: State theorem → Apply definitions → Reach conclusion
2. Contradiction: Assume opposite → Derive contradiction
3. Induction: Base case → Inductive hypothesis → Inductive step

## Playbook Application
{playbook}

## Recent Reflection
{reflection}

## Problem
Question: {question}
Context: {context}

## Solution Process

### Step 1: Problem Classification
Identify as: Arithmetic | Algebra | Geometry | Calculus | Statistics | Other

### Step 2: Method Selection
Choose primary approach based on problem type

### Step 3: Systematic Solution
Show ALL work with numbered steps

### Step 4: Verification
Check answer by substitution or alternative method

## Critical Math Requirements

**MUST:**
- Show EVERY arithmetic step
- Define all variables
- State units in final answer
- Verify solution correctness

**NEVER:**
- Skip "obvious" steps
- Assume reader knows intermediate results
- Round intermediate calculations
- Forget to check answer validity

## Output Format

{{
  "problem_type": "<classification>",
  "reasoning": "<numbered step-by-step solution>",
  "calculations": ["<step1>", "<step2>", ...],
  "bullet_ids": ["<id1>", "<id2>"],
  "verification": "<check of answer>",
  "final_answer": "<answer with units if applicable>",
  "confidence": 0.95
}}

Begin response with `{{` and end with `}}`
"""
```

**File:** ace/prompts_v2.py (L617-631)
```python
class PromptManager:
    """
    Manages prompt versions and selection based on context.

    Features:
    - Version control for prompts
    - Domain-specific prompt selection
    - A/B testing support
    - Prompt performance tracking

    Example:
        >>> manager = PromptManager()
        >>> prompt = manager.get_generator_prompt(domain="math", version="2.0")
        >>> # Use prompt with your LLM
    """
```

# 我追问
一个完整的上下文工程系统包含以下七个核心组成部分：1.指令/系统提示词：定义模型整体行为的初始指令，可以（也应该）包含示例、规则等。2.用户提示词：用户提出的即时任务或问题。3.当前状态或对话历史（短期记忆）：用户和模型此前的对话内容，展现当前交流的背景。4.长期记忆：跨多次对话积累的持久性知识库，比如用户喜好、历史项目摘要、记住的特定事实。5.检索的信息（RAG）：外部的、最新的信息，包括从文档、数据库或 API 获取的相关内容，用于回答特定问题。6.可用工具：模型可以调用的所有函数或内置工具定义（如检查库存、发送邮件等）。7.结构化输出：明确定义模型输出的格式，例如 JSON 格式的对象 那在这个repo里面具体哪些体现了上面7点？

# deepwiki
您询问的是 ACE Framework 如何体现上下文工程系统的七个核心组成部分。<cite/>让我逐一分析这个 repo 中的具体实现:<cite/>

## 1. 指令/系统提示词

ACE 通过 **Prompt Templates** 实现系统指令定义。 [1](#1-0) 

每个角色都有专门的 prompt 模板:<cite/>
- **Generator Prompt**: 定义如何使用 playbook 执行任务 [1](#1-0) 
- **Reflector Prompt**: 定义如何分析执行结果 [2](#1-1) 
- **Curator Prompt**: 定义如何更新策略 [3](#1-2) 

还提供了**领域特定变体**,如数学和代码专用 prompt,包含具体规则和示例。 [4](#1-3) 

## 2. 用户提示词

通过 `Sample` 类的 `question` 字段传递用户的即时任务。 [5](#1-4) 

Generator 在生成答案时接收这个 question 参数。 [6](#1-5) 

## 3. 当前状态/对话历史(短期记忆)

ACE 通过 **Reflection Window** 机制维护短期记忆。 [7](#1-6) 

`_recent_reflections` 列表存储最近 N 次的反思结果(默认 3 次),并在每次生成时作为上下文传递。 [8](#1-7) 

这些反思历史会传递给 Generator 的 `reflection` 参数。 [9](#1-8) 

## 4. 长期记忆

**Playbook** 是 ACE 的核心长期记忆系统。 [10](#1-9) 

Playbook 存储持久化的策略条目(bullets),每个 bullet 包含:<cite/>
- 策略内容
- helpful/harmful 计数器(跨对话累积)
- 元数据和时间戳 [11](#1-10) 

这些策略通过增量更新操作(ADD, UPDATE, TAG, REMOVE)持续演化,形成跨任务的知识积累。 [12](#1-11) 

## 5. 检索的信息(RAG)

ACE 通过 `Sample` 类的 `context` 字段支持外部信息注入。 [13](#1-12) 

这个 context 可以包含从文档、数据库或 API 检索的相关信息,并传递给 Generator 使用。 [6](#1-5) 

## 6. 可用工具

虽然 ACE 本身不直接实现工具调用,但通过 **TaskEnvironment** 抽象类提供了工具集成接口。 [14](#1-13) 

`TaskEnvironment.evaluate()` 方法可以封装工具调用逻辑,执行实际操作并返回反馈。 [15](#1-14) 

Generator 的输出可以触发环境中的工具执行,形成 Agent-Environment 交互循环。<cite/>

## 7. 结构化输出

ACE 强制使用 **JSON 格式**的结构化输出:<cite/>

- **GeneratorOutput**: 包含 `reasoning`, `final_answer`, `bullet_ids` 等字段 [16](#1-15) 
- **ReflectorOutput**: 包含错误分析和 bullet 标签<cite/>
- **CuratorOutput**: 包含 delta 操作批次 [17](#1-16) 

V2 版本的 prompt 还增加了置信度评分等额外结构化字段。 [18](#1-17) 

提供了 `validate_prompt_output()` 函数来验证输出格式的正确性。 [19](#1-18) 

## Notes

ACE Framework 的独特之处在于将这七个组成部分整合成一个**自适应学习循环**。<cite/>特别是长期记忆(Playbook)不是静态的,而是通过 Generator-Reflector-Curator 三角色协同持续演化,这使得上下文工程从配置转变为学习过程。<cite/>

该框架支持离线训练和在线适应两种模式,分别对应初始知识构建和生产环境持续学习。 [20](#1-19) 

Wiki pages you might want to explore:
- [Online Adaptation (kayba-ai/agentic-context-engine)](/wiki/kayba-ai/agentic-context-engine#6.4)

### Citations

**File:** ace/prompts_v2.py (L24-26)
```python
GENERATOR_V2_PROMPT = """\
# Identity and Metadata
You are ACE Generator v2.0, an expert problem-solving agent.
```

**File:** ace/prompts_v2.py (L132-134)
```python
REFLECTOR_V2_PROMPT = """\
# Identity and Metadata
You are ACE Reflector v2.0, a senior analytical reviewer.
```

**File:** ace/prompts_v2.py (L270-272)
```python
CURATOR_V2_PROMPT = """\
# Identity and Metadata
You are ACE Curator v2.0, the strategic playbook architect.
```

**File:** ace/prompts_v2.py (L452-528)
```python
# Mathematics-specific Generator
GENERATOR_MATH_PROMPT = """\
# Identity and Metadata
You are ACE Math Generator v2.0, specialized in mathematical problem-solving.
Prompt Version: 2.0.0-math
Calculation Verification: Required
Precision: 6 decimal places where applicable

## Mathematical Protocols

### Arithmetic Operations
- ALWAYS show intermediate steps
- VERIFY calculations twice
- Use standard order of operations (PEMDAS/BODMAS)

### Algebraic Solutions
- Show all equation transformations
- Verify solutions by substitution
- State domain restrictions explicitly

### Proof Strategies
1. Direct proof: State theorem → Apply definitions → Reach conclusion
2. Contradiction: Assume opposite → Derive contradiction
3. Induction: Base case → Inductive hypothesis → Inductive step

## Playbook Application
{playbook}

## Recent Reflection
{reflection}

## Problem
Question: {question}
Context: {context}

## Solution Process

### Step 1: Problem Classification
Identify as: Arithmetic | Algebra | Geometry | Calculus | Statistics | Other

### Step 2: Method Selection
Choose primary approach based on problem type

### Step 3: Systematic Solution
Show ALL work with numbered steps

### Step 4: Verification
Check answer by substitution or alternative method

## Critical Math Requirements

**MUST:**
- Show EVERY arithmetic step
- Define all variables
- State units in final answer
- Verify solution correctness

**NEVER:**
- Skip "obvious" steps
- Assume reader knows intermediate results
- Round intermediate calculations
- Forget to check answer validity

## Output Format

{{
  "problem_type": "<classification>",
  "reasoning": "<numbered step-by-step solution>",
  "calculations": ["<step1>", "<step2>", ...],
  "bullet_ids": ["<id1>", "<id2>"],
  "verification": "<check of answer>",
  "final_answer": "<answer with units if applicable>",
  "confidence": 0.95
}}

Begin response with `{{` and end with `}}`
"""
```

**File:** ace/prompts_v2.py (L747-801)
```python
def validate_prompt_output(output: str, role: str) -> tuple[bool, list[str]]:
    """
    Validate that prompt output meets requirements.

    Args:
        output: The LLM output to validate
        role: The role (generator, reflector, curator)

    Returns:
        (is_valid, error_messages)
    """
    import json

    errors = []

    # Check if valid JSON
    try:
        data = json.loads(output)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return False, errors

    # Role-specific validation
    if role == "generator":
        required = ["reasoning", "bullet_ids", "final_answer"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        if "confidence_scores" in data:
            for score in data["confidence_scores"].values():
                if not 0 <= score <= 1:
                    errors.append(f"Invalid confidence score: {score}")

    elif role == "reflector":
        required = ["reasoning", "error_identification", "bullet_tags"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        for tag in data.get("bullet_tags", []):
            if tag.get("tag") not in ["helpful", "harmful", "neutral"]:
                errors.append(f"Invalid tag: {tag.get('tag')}")

    elif role == "curator":
        required = ["reasoning", "operations"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        for op in data.get("operations", []):
            if op.get("type") not in ["ADD", "UPDATE", "TAG", "REMOVE"]:
                errors.append(f"Invalid operation type: {op.get('type')}")

    return len(errors) == 0, errors
```

**File:** ace/adaptation.py (L97-198)
```python
class AdapterBase:
    """Shared orchestration logic for offline and online ACE adaptation."""

    def __init__(
        self,
        *,
        playbook: Optional[Playbook] = None,
        generator: Generator,
        reflector: Reflector,
        curator: Curator,
        max_refinement_rounds: int = 1,
        reflection_window: int = 3,
    ) -> None:
        self.playbook = playbook or Playbook()
        self.generator = generator
        self.reflector = reflector
        self.curator = curator
        self.max_refinement_rounds = max_refinement_rounds
        self.reflection_window = reflection_window
        self._recent_reflections: List[str] = []

    # ------------------------------------------------------------------ #
    def _reflection_context(self) -> str:
        return "\n---\n".join(self._recent_reflections)

    def _update_recent_reflections(self, reflection: ReflectorOutput) -> None:
        serialized = json.dumps(reflection.raw, ensure_ascii=False)
        self._recent_reflections.append(serialized)
        if len(self._recent_reflections) > self.reflection_window:
            self._recent_reflections = self._recent_reflections[
                -self.reflection_window :
            ]

    def _apply_bullet_tags(self, reflection: ReflectorOutput) -> None:
        for tag in reflection.bullet_tags:
            try:
                self.playbook.tag_bullet(tag.id, tag.tag)
            except ValueError:
                continue

    def _question_context(
        self, sample: Sample, environment_result: EnvironmentResult
    ) -> str:
        parts = [
            f"question: {sample.question}",
            f"context: {sample.context}",
            f"metadata: {json.dumps(sample.metadata)}",
            f"feedback: {environment_result.feedback}",
            f"ground_truth: {environment_result.ground_truth}",
        ]
        return "\n".join(parts)

    def _progress_string(
        self, epoch: int, total_epochs: int, step: int, total_steps: int
    ) -> str:
        return f"epoch {epoch}/{total_epochs} · sample {step}/{total_steps}"

    def _process_sample(
        self,
        sample: Sample,
        environment: TaskEnvironment,
        *,
        epoch: int,
        total_epochs: int,
        step_index: int,
        total_steps: int,
    ) -> AdapterStepResult:
        generator_output = self.generator.generate(
            question=sample.question,
            context=sample.context,
            playbook=self.playbook,
            reflection=self._reflection_context(),
        )
        env_result = environment.evaluate(sample, generator_output)
        reflection = self.reflector.reflect(
            question=sample.question,
            generator_output=generator_output,
            playbook=self.playbook,
            ground_truth=env_result.ground_truth,
            feedback=env_result.feedback,
            max_refinement_rounds=self.max_refinement_rounds,
        )
        self._apply_bullet_tags(reflection)
        self._update_recent_reflections(reflection)
        curator_output = self.curator.curate(
            reflection=reflection,
            playbook=self.playbook,
            question_context=self._question_context(sample, env_result),
            progress=self._progress_string(
                epoch, total_epochs, step_index, total_steps
            ),
        )
        self.playbook.apply_delta(curator_output.delta)
        return AdapterStepResult(
            sample=sample,
            generator_output=generator_output,
            environment_result=env_result,
            reflection=reflection,
            curator_output=curator_output,
            playbook_snapshot=self.playbook.as_prompt(),
        )

```

**File:** ace/roles.py (L36-41)
```python
@dataclass
class GeneratorOutput:
    reasoning: str
    final_answer: str
    bullet_ids: List[str]
    raw: Dict[str, Any]
```

**File:** ace/roles.py (L62-66)
```python
        >>> output = generator.generate(
        ...     question="What is the capital of France?",
        ...     context="Answer concisely",
        ...     playbook=playbook
        ... )
```

**File:** ace/roles.py (L279-282)
```python
@dataclass
class CuratorOutput:
    delta: DeltaBatch
    raw: Dict[str, Any]
```

**File:** ace/playbook.py (L44-50)
```python
class Playbook:
    """Structured context store as defined by ACE."""

    def __init__(self) -> None:
        self._bullets: Dict[str, Bullet] = {}
        self._sections: Dict[str, List[str]] = {}
        self._next_id = 0
```

**File:** CLAUDE.md (L66-66)
```markdown
- **Playbook**: Structured context store containing bullets (strategy entries) with helpful/harmful counters
```

**File:** CLAUDE.md (L67-67)
```markdown
- **Delta Operations**: Incremental updates to the playbook (ADD, UPDATE, TAG, REMOVE)
```

**File:** CLAUDE.md (L99-102)
```markdown
3. **Task Environment**:
   - Extend `TaskEnvironment` abstract class
   - Implement `evaluate()` to provide execution feedback
   - Return `EnvironmentResult` with feedback and optional ground truth
```

# 我追问
ACE Framework 上下文工程系统完整流程

# deepwiki
## ACE Framework 上下文工程系统完整流程
ACE Framework 完整上下文工程流程，涵盖离线知识构建、在线持续学习、Playbook 管理、三角色协同和环境评估。核心流程从 [1a] 开始的 OfflineAdapter.run() 训练循环，通过 [1g] 应用增量更新构建知识库，然后 [2a] OnlineAdapter 接管生产环境流式学习，[3b] 执行具体操作更新策略，[4a-4d] 展示三角色协同机制，[5b] 提供评估反馈驱动学习。
### 1. 离线知识构建流程
OfflineAdapter 如何通过多轮迭代训练构建初始 Playbook 知识库
### 1a. 启动离线训练循环 (`adaptation.py:253`)
OfflineAdapter.run() 开始多轮训练
```text
def run(self, samples: Sequence[Sample], environment: TaskEnvironment, epochs: int = 1) -> List[AdapterStepResult]:
```
### 1b. 处理单个训练样本 (`adaptation.py:278`)
调用核心处理方法
```text
result = self._process_sample(sample, environment, epoch=epoch_idx, total_epochs=epochs, step_index=step_idx, total_steps=total_steps)
```
### 1c. Generator 生成答案 (`adaptation.py:164`)
使用当前 Playbook 生成响应
```text
generator_output = self.generator.generate(question=sample.question, context=sample.context, playbook=self.playbook, reflection=self._reflection_context())
```
### 1d. 环境评估反馈 (`adaptation.py:170`)
TaskEnvironment 评估答案正确性
```text
env_result = environment.evaluate(sample, generator_output)
```
### 1e. Reflector 分析反思 (`adaptation.py:171`)
分析执行结果并标记策略
```text
reflection = self.reflector.reflect(question=sample.question, generator_output=generator_output, playbook=self.playbook, ground_truth=env_result.ground_truth, feedback=env_result.feedback, max_refinement_rounds=self.max_refinement_rounds)
```
### 1f. Curator 生成更新 (`adaptation.py:181`)
基于反思生成 DeltaBatch
```text
curator_output = self.curator.curate(reflection=reflection, playbook=self.playbook, question_context=self._question_context(sample, env_result), progress=self._progress_string(epoch, total_epochs, step_index, total_steps))
```
### 1g. 应用增量更新 (`adaptation.py:189`)
更新 Playbook 策略库
```text
self.playbook.apply_delta(curator_output.delta)
```
### 2. 在线持续学习流程
OnlineAdapter 如何处理流式样本并实时更新 Playbook
### 2a. 启动在线学习 (`adaptation.py:340`)
OnlineAdapter.run() 处理流式数据
```text
def run(self, samples: Iterable[Sample], environment: TaskEnvironment) -> List[AdapterStepResult]:
```
### 2b. 流式样本处理 (`adaptation.py:362`)
逐个处理到达的样本
```text
for step_idx, sample in enumerate(samples, start=1):
```
### 2c. 实时样本处理 (`adaptation.py:363`)
调用共享处理逻辑
```text
result = self._process_sample(sample, environment, epoch=1, total_epochs=1, step_index=step_idx, total_steps=step_idx)
```
### 2d. 维护短期记忆 (`adaptation.py:122`)
更新反思窗口保持上下文
```text
def _update_recent_reflections(self, reflection: ReflectorOutput) -> None:
```
### 2e. 窗口大小控制 (`adaptation.py:125`)
限制反思历史避免上下文膨胀
```text
if len(self._recent_reflections) > self.reflection_window: self._recent_reflections = self._recent_reflections[-self.reflection_window:]
```
### 3. Playbook 知识库管理
Playbook 如何存储和演化策略知识
### 3a. 应用增量更新 (`playbook.py:194`)
批量应用 Delta 操作
```text
def apply_delta(self, delta: DeltaBatch) -> None:
```
### 3b. 执行单个操作 (`playbook.py:198`)
处理 ADD/UPDATE/TAG/REMOVE 操作
```text
def _apply_operation(self, operation: DeltaOperation) -> None:
```
### 3c. 添加新策略 (`playbook.py:200`)
ADD 操作增加新 bullet
```text
elif op_type == "ADD": self.add_bullet(section=operation.section, content=operation.content or "", bullet_id=operation.bullet_id, metadata=operation.metadata)
```
### 3d. 更新策略计数 (`playbook.py:215`)
TAG 操作更新 helpful/harmful 计数
```text
elif op_type == "TAG": for tag, increment in operation.metadata.items(): self.tag_bullet(operation.bullet_id, tag, increment)
```
### 3e. 持久化存储 (`playbook.py:153`)
保存 Playbook 到文件
```text
def save_to_file(self, path: str) -> None:
```
### 4. 三角色协同机制
Generator、Reflector、Curator 三个角色如何协同工作
### 4a. Generator LLM 调用 (`roles.py:123`)
Generator 调用 LLM 生成答案
```text
response = self.llm.complete(prompt, **kwargs)
```
### 4b. 解析结构化输出 (`roles.py:125`)
验证并解析 JSON 输出
```text
data = _safe_json_loads(response.text)
```
### 4c. 应用策略标记 (`adaptation.py:131`)
Reflector 标记策略效果
```text
for tag in reflection.bullet_tags: try: self.playbook.tag_bullet(tag.id, tag.tag) except ValueError: continue
```
### 4d. Curator 生成 Delta (`roles.py:380`)
Curator 创建增量操作
```text
delta = DeltaBatch.from_json(data)
```
### 5. 环境评估与反馈
TaskEnvironment 如何评估执行结果并提供反馈
### 5a. 环境评估接口 (`adaptation.py:69`)
TaskEnvironment 抽象评估方法
```text
@abstractmethod def evaluate(self, sample: Sample, generator_output: GeneratorOutput) -> EnvironmentResult:
```
### 5b. 答案正确性判断 (`test_adaptation.py:21`)
SimpleQAEnvironment 评估逻辑
```text
correct = prediction.strip().lower() == ground_truth.strip().lower()
```
### 5c. 返回评估结果 (`test_adaptation.py:23`)
封装反馈和指标
```text
return EnvironmentResult(feedback=feedback, ground_truth=ground_truth, metrics={"accuracy": 1.0 if correct else 0.0})
```

# 我追问
这个ACE是如何解决长上下文的Context-Rot问题？即随着上下文长度的增加，模型的注意力机制可能会出现"腐蚀"现象，导致对关键信息的关注度下降。

# deepwiki
## ACE如何解决Context-Rot问题

ACE框架通过**Playbook**机制和**增量更新策略**来解决长上下文的Context-Rot问题。 [1](#0-0) 

### 核心解决方案

**1. 结构化的Playbook存储**

ACE使用Playbook作为"活文档"来存储策略,而不是将所有历史信息都塞入上下文窗口。 [1](#0-0) 每个策略条目(Bullet)都有独立的ID和元数据,包括`helpful`和`harmful`计数器。 [2](#0-1) 

**2. 选择性上下文注入**

Generator在执行任务时,只使用Playbook中相关的策略条目,而不是整个历史记录。 [3](#0-2) 这通过`playbook.as_prompt()`方法实现,只将当前有效的策略注入到提示中。<cite />

**3. 反射窗口机制**

ACE维护一个固定大小的反射窗口(`reflection_window`),默认只保留最近3-5次反射。 [4](#0-3) 这防止了历史反射无限累积:

```python
def _update_recent_reflections(self, reflection: ReflectorOutput) -> None:
    serialized = json.dumps(reflection.raw, ensure_ascii=False)
    self._recent_reflections.append(serialized)
    if len(self._recent_reflections) > self.reflection_window:
        self._recent_reflections = self._recent_reflections[-self.reflection_window:]
``` [5](#0-4) 

**4. 增量Delta更新**

Curator通过Delta操作(ADD/UPDATE/TAG/REMOVE)增量更新Playbook,而不是重写整个上下文。 [6](#0-5) 这确保了只有最有价值的信息被保留和更新。<cite />

**5. 自动清理机制**

通过`helpful`和`harmful`计数器,ACE可以识别并移除低价值的策略条目。 [2](#0-1) 在生产环境中,可以实现定期清理来控制Playbook大小。<cite />

### 与传统方法的对比

传统的长上下文方法会将所有历史信息都放入上下文窗口,导致:
- 注意力分散到不相关的历史信息
- 关键信息被"淹没"在大量文本中
- 上下文窗口快速耗尽

ACE的方法则:
- 只保留**结构化的策略知识**,而非原始历史
- 通过**评分机制**优先保留有用信息
- 使用**固定窗口**限制反射历史的增长
- 支持**主动清理**低价值条目

## Notes

ACE的设计哲学是"知识蒸馏"而非"历史记录"。<cite />它不是试图保留所有上下文,而是从经验中提取可复用的策略模式。 [7](#0-6) 这种方法从根本上避免了Context-Rot问题,因为上下文大小是受控的,且内容质量通过helpful/harmful评分持续优化。<cite />

在Online Adaptation模式下,这种机制尤其重要,因为系统需要持续处理新样本而不会因上下文膨胀而降级。 [8](#0-7) 

Wiki pages you might want to explore:
- [Online Adaptation (kayba-ai/agentic-context-engine)](/wiki/kayba-ai/agentic-context-engine#6.4)

### Citations

**File:** README.md (L107-114)
```markdown
ACE teaches your agent and internalises:
- **✅ Successes** → Extract patterns that work
- **❌ Failures** → Learn what to avoid
- **🔧 Tool usage** → Discover which tools work best for which tasks
- **🎯 Edge cases** → Remember rare scenarios and how to handle them

The magic happens in the **Playbook**—a living document of strategies that evolves with experience. <br>
**Key innovation:** All learning happens **in context** through incremental updates—no fine-tuning, no training data, and complete transparency into what your agent learned.
```

**File:** ace/playbook.py (L87-94)
```python
    def tag_bullet(
        self, bullet_id: str, tag: str, increment: int = 1
    ) -> Optional[Bullet]:
        bullet = self._bullets.get(bullet_id)
        if bullet is None:
            return None
        bullet.tag(tag, increment=increment)
        return bullet
```

**File:** ace/roles.py (L114-119)
```python
        base_prompt = self.prompt_template.format(
            playbook=playbook.as_prompt() or "(empty playbook)",
            reflection=_format_optional(reflection),
            question=question,
            context=_format_optional(context),
        )
```

**File:** ace/adaptation.py (L108-108)
```python
        reflection_window: int = 3,
```

**File:** ace/adaptation.py (L122-128)
```python
    def _update_recent_reflections(self, reflection: ReflectorOutput) -> None:
        serialized = json.dumps(reflection.raw, ensure_ascii=False)
        self._recent_reflections.append(serialized)
        if len(self._recent_reflections) > self.reflection_window:
            self._recent_reflections = self._recent_reflections[
                -self.reflection_window :
            ]
```

**File:** ace/adaptation.py (L189-189)
```python
        self.playbook.apply_delta(curator_output.delta)
```

**File:** ace/adaptation.py (L290-297)
```python
class OnlineAdapter(AdapterBase):
    """
    Orchestrates online ACE adaptation for continuous learning.

    The OnlineAdapter processes samples sequentially as they arrive,
    updating the playbook after each one. This enables continuous
    improvement during deployment, adapting to new patterns and
    correcting mistakes in real-time.
```


# 我追问
为了解决长上下文带来的问题，业界提出了系统性的上下文工程方法论：Offload：通过引用减少上下文长度。Retrieve：RAG 技术动态检索相关信息。Reduce：压缩裁剪冗余信息。Isolate：分而治之，通过SubAgent处理子任务。这些在本repo里面如何体现？

# deepwiki
## ACE框架中的上下文工程方法论体现

您提到的四种上下文工程方法论在ACE框架中都有对应的实现机制。<cite />让我逐一说明:

### 1. Offload (卸载) - 通过引用减少上下文长度

ACE通过**Bullet ID引用系统**实现了这一点。 [1](#1-0) Generator在生成答案时返回`bullet_ids`列表,记录使用了哪些策略,而不是重复策略的完整内容。 [2](#1-1) 

Playbook内部使用字典结构`_bullets: Dict[str, Bullet]`存储策略,通过ID引用而非内容复制。 [3](#1-2) 这样在传递上下文时只需要传递轻量级的ID列表,大幅减少了上下文长度。<cite />

### 2. Retrieve (检索) - RAG技术动态检索相关信息

ACE通过**Playbook的分段组织**和**选择性注入**实现了类似RAG的功能。 [2](#1-1) 

Playbook将策略按`section`分类存储(如"general"、"math"、"code"等)。 [4](#1-3) 在特定领域任务中,可以使用领域特定的Generator提示(如`GENERATOR_MATH_PROMPT`),只检索相关section的策略。<cite />

虽然当前实现中`as_prompt()`方法返回所有策略,但架构支持扩展为基于任务类型的选择性检索。<cite />

### 3. Reduce (压缩) - 压缩裁剪冗余信息

ACE通过**多层压缩机制**实现信息精简:

**a) 反射窗口限制** [5](#1-4) 
```python
def _update_recent_reflections(self, reflection: ReflectorOutput) -> None:
    serialized = json.dumps(reflection.raw, ensure_ascii=False)
    self._recent_reflections.append(serialized)
    if len(self._recent_reflections) > self.reflection_window:
        self._recent_reflections = self._recent_reflections[-self.reflection_window:]
```
只保留最近N次反射(默认3次),自动丢弃旧的反射历史。<cite />

**b) Delta增量更新** [6](#1-5) 
Curator通过`DeltaBatch`进行增量更新,只传递变更内容(ADD/UPDATE/TAG/REMOVE操作),而非重写整个Playbook。<cite />

**c) 策略评分与清理** [7](#1-6) 
通过`helpful`/`harmful`计数器追踪策略效果,支持移除低价值策略。 [8](#1-7) `remove_bullet()`方法可以删除无效策略,防止Playbook无限膨胀。<cite />

### 4. Isolate (隔离) - 分而治治,通过SubAgent处理子任务

ACE通过**三角色分工**实现了任务隔离: [9](#1-8) 
- **Generator**: 专注于执行任务和生成答案
- **Reflector**: 专注于分析错误和评估策略
- **Curator**: 专注于更新Playbook

每个角色有独立的提示模板和职责边界。 [10](#1-9) 在`_process_sample()`方法中,三个角色按顺序处理各自的子任务,互不干扰。<cite />

此外,ACE支持**领域特定的Generator变体**: [4](#1-3) 
- `GENERATOR_MATH_PROMPT`: 数学问题专用
- `GENERATOR_CODE_PROMPT`: 代码生成专用

这些变体可以视为针对不同子任务的"SubAgent"。 [11](#1-10) `PromptManager`类支持根据领域动态选择合适的Generator变体。<cite />

## Notes

ACE的设计巧妙地将这四种方法论融合在一起:<cite />
- **Offload + Retrieve**: Playbook的ID引用系统和分段组织
- **Reduce**: 反射窗口、Delta更新、策略评分三重压缩
- **Isolate**: 三角色分工和领域特定变体

这些机制协同工作,使ACE能够在长期运行中保持上下文的精简和高效,避免Context-Rot问题。<cite />与传统的"把所有东西都塞进上下文"的方法相比,ACE采用了更加工程化和可持续的方案。<cite />

Wiki pages you might want to explore:
- [Playbook System (kayba-ai/agentic-context-engine)](/wiki/kayba-ai/agentic-context-engine#2.2)
- [Online Adaptation (kayba-ai/agentic-context-engine)](/wiki/kayba-ai/agentic-context-engine#6.4)

### Citations

**File:** ace/roles.py (L37-41)
```python
class GeneratorOutput:
    reasoning: str
    final_answer: str
    bullet_ids: List[str]
    raw: Dict[str, Any]
```

**File:** ace/playbook.py (L44-50)
```python
class Playbook:
    """Structured context store as defined by ACE."""

    def __init__(self) -> None:
        self._bullets: Dict[str, Bullet] = {}
        self._sections: Dict[str, List[str]] = {}
        self._next_id = 0
```

**File:** ace/playbook.py (L87-94)
```python
    def tag_bullet(
        self, bullet_id: str, tag: str, increment: int = 1
    ) -> Optional[Bullet]:
        bullet = self._bullets.get(bullet_id)
        if bullet is None:
            return None
        bullet.tag(tag, increment=increment)
        return bullet
```

**File:** ace/playbook.py (L96-106)
```python
    def remove_bullet(self, bullet_id: str) -> None:
        bullet = self._bullets.pop(bullet_id, None)
        if bullet is None:
            return
        section_list = self._sections.get(bullet.section)
        if section_list:
            self._sections[bullet.section] = [
                bid for bid in section_list if bid != bullet_id
            ]
            if not self._sections[bullet.section]:
                del self._sections[bullet.section]
```

**File:** ace/playbook.py (L108-112)
```python
    def get_bullet(self, bullet_id: str) -> Optional[Bullet]:
        return self._bullets.get(bullet_id)

    def bullets(self) -> List[Bullet]:
        return list(self._bullets.values())
```

**File:** ace/prompts_v2.py (L453-528)
```python
GENERATOR_MATH_PROMPT = """\
# Identity and Metadata
You are ACE Math Generator v2.0, specialized in mathematical problem-solving.
Prompt Version: 2.0.0-math
Calculation Verification: Required
Precision: 6 decimal places where applicable

## Mathematical Protocols

### Arithmetic Operations
- ALWAYS show intermediate steps
- VERIFY calculations twice
- Use standard order of operations (PEMDAS/BODMAS)

### Algebraic Solutions
- Show all equation transformations
- Verify solutions by substitution
- State domain restrictions explicitly

### Proof Strategies
1. Direct proof: State theorem → Apply definitions → Reach conclusion
2. Contradiction: Assume opposite → Derive contradiction
3. Induction: Base case → Inductive hypothesis → Inductive step

## Playbook Application
{playbook}

## Recent Reflection
{reflection}

## Problem
Question: {question}
Context: {context}

## Solution Process

### Step 1: Problem Classification
Identify as: Arithmetic | Algebra | Geometry | Calculus | Statistics | Other

### Step 2: Method Selection
Choose primary approach based on problem type

### Step 3: Systematic Solution
Show ALL work with numbered steps

### Step 4: Verification
Check answer by substitution or alternative method

## Critical Math Requirements

**MUST:**
- Show EVERY arithmetic step
- Define all variables
- State units in final answer
- Verify solution correctness

**NEVER:**
- Skip "obvious" steps
- Assume reader knows intermediate results
- Round intermediate calculations
- Forget to check answer validity

## Output Format

{{
  "problem_type": "<classification>",
  "reasoning": "<numbered step-by-step solution>",
  "calculations": ["<step1>", "<step2>", ...],
  "bullet_ids": ["<id1>", "<id2>"],
  "verification": "<check of answer>",
  "final_answer": "<answer with units if applicable>",
  "confidence": 0.95
}}

Begin response with `{{` and end with `}}`
"""
```

**File:** ace/prompts_v2.py (L617-697)
```python
class PromptManager:
    """
    Manages prompt versions and selection based on context.

    Features:
    - Version control for prompts
    - Domain-specific prompt selection
    - A/B testing support
    - Prompt performance tracking

    Example:
        >>> manager = PromptManager()
        >>> prompt = manager.get_generator_prompt(domain="math", version="2.0")
        >>> # Use prompt with your LLM
    """

    # Version registry
    PROMPTS = {
        "generator": {
            "1.0": "ace.prompts.GENERATOR_PROMPT",
            "2.0": GENERATOR_V2_PROMPT,
            "2.0-math": GENERATOR_MATH_PROMPT,
            "2.0-code": GENERATOR_CODE_PROMPT,
        },
        "reflector": {
            "1.0": "ace.prompts.REFLECTOR_PROMPT",
            "2.0": REFLECTOR_V2_PROMPT,
        },
        "curator": {
            "1.0": "ace.prompts.CURATOR_PROMPT",
            "2.0": CURATOR_V2_PROMPT,
        },
    }

    def __init__(self, default_version: str = "2.0"):
        """
        Initialize prompt manager.

        Args:
            default_version: Default version to use if not specified
        """
        self.default_version = default_version
        self.usage_stats: Dict[str, int] = {}

    def get_generator_prompt(
        self, domain: Optional[str] = None, version: Optional[str] = None
    ) -> str:
        """
        Get generator prompt for specific domain and version.

        Args:
            domain: Domain (math, code, etc.) or None for general
            version: Version string or None for default

        Returns:
            Formatted prompt template
        """
        version = version or self.default_version

        if domain and f"{version}-{domain}" in self.PROMPTS["generator"]:
            prompt_key = f"{version}-{domain}"
        else:
            prompt_key = version

        prompt = self.PROMPTS["generator"].get(prompt_key)
        if isinstance(prompt, str) and prompt.startswith("ace."):
            # Handle v1 prompt references
            from ace import prompts

            prompt = getattr(prompts, prompt.split(".")[-1])

        # Track usage
        self._track_usage(f"generator-{prompt_key}")

        # Add current date if v2 prompt
        if "current_date" in prompt:
            prompt = prompt.replace(
                "{current_date}", datetime.now().strftime("%Y-%m-%d")
            )

        return prompt
```

**File:** ace/adaptation.py (L122-128)
```python
    def _update_recent_reflections(self, reflection: ReflectorOutput) -> None:
        serialized = json.dumps(reflection.raw, ensure_ascii=False)
        self._recent_reflections.append(serialized)
        if len(self._recent_reflections) > self.reflection_window:
            self._recent_reflections = self._recent_reflections[
                -self.reflection_window :
            ]
```

**File:** ace/adaptation.py (L154-197)
```python
    def _process_sample(
        self,
        sample: Sample,
        environment: TaskEnvironment,
        *,
        epoch: int,
        total_epochs: int,
        step_index: int,
        total_steps: int,
    ) -> AdapterStepResult:
        generator_output = self.generator.generate(
            question=sample.question,
            context=sample.context,
            playbook=self.playbook,
            reflection=self._reflection_context(),
        )
        env_result = environment.evaluate(sample, generator_output)
        reflection = self.reflector.reflect(
            question=sample.question,
            generator_output=generator_output,
            playbook=self.playbook,
            ground_truth=env_result.ground_truth,
            feedback=env_result.feedback,
            max_refinement_rounds=self.max_refinement_rounds,
        )
        self._apply_bullet_tags(reflection)
        self._update_recent_reflections(reflection)
        curator_output = self.curator.curate(
            reflection=reflection,
            playbook=self.playbook,
            question_context=self._question_context(sample, env_result),
            progress=self._progress_string(
                epoch, total_epochs, step_index, total_steps
            ),
        )
        self.playbook.apply_delta(curator_output.delta)
        return AdapterStepResult(
            sample=sample,
            generator_output=generator_output,
            environment_result=env_result,
            reflection=reflection,
            curator_output=curator_output,
            playbook_snapshot=self.playbook.as_prompt(),
        )
```

**File:** CLAUDE.md (L66-71)
```markdown
- **Playbook**: Structured context store containing bullets (strategy entries) with helpful/harmful counters
- **Delta Operations**: Incremental updates to the playbook (ADD, UPDATE, TAG, REMOVE)
- **Three Agentic Roles** sharing the same base LLM:
  - **Generator**: Produces answers using the current playbook
  - **Reflector**: Analyzes errors and classifies bullet contributions
  - **Curator**: Emits delta operations to update the playbook
```


# 我追问
「生产环境持续学习」的具体详细的流程是啥？请在一个mermaid流程图里面，具体且精准的想展示出「知识构建」和「生产环境持续学习」，两个不同阶段的架构流程图，包括处理流、数据流、逻辑流程等，需要让我一目了然这整个过程

# deepwiki
