# Train SQL Agent with RL - Agent-lightning

原文链接: https://microsoft.github.io/agent-lightning/latest/how-to/train-sql-agent/

⚠️ You are viewing development documentation. For stable documentation, please visit
<https://microsoft.github.io/agent-lightning/stable/>










2025-10-31




2025-08-10



# Train SQL Agent with Agent-lightning and VERL[¶](#train-sql-agent-with-agent-lightning-and-verl "Permanent link")

This walkthrough builds upon the **Agent-lightning v0.2 SQL Agent** example and explains how the system components integrate: a **LangGraph-based SQL agent** wrapped as a [`LitAgent`](../../reference/agent/#agentlightning.LitAgent "            agentlightning.LitAgent"), the **[`VERL`](../../algorithm-zoo/verl/#agentlightning.algorithm.verl.VERL "            VERL") reinforcement learning (RL) algorithm**, and the **[`Trainer`](../../reference/trainer/#agentlightning.Trainer "            agentlightning.Trainer")**, which coordinates both training and debugging.

The command-line interface in [`examples/spider/train_sql_agent.py`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider/train_sql_agent.py) provides a complete runnable example. However, this document focuses on understanding the underlying architecture so you can effectively adapt the workflow to your own agents.

## SQL Agent Architecture[¶](#sql-agent-architecture "Permanent link")

Agent-lightning integrates seamlessly with various orchestration frameworks, including [Agent Framework](https://github.com/microsoft/agent-framework), [AutoGen](https://github.com/microsoft/autogen), [CrewAI](https://www.crewai.com/), [LangGraph](https://github.com/langchain-ai/langgraph), and the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). It can also interoperate with custom Python logic.

In this example, **LangGraph** defines a cyclic workflow that mirrors an analyst’s iterative SQL development process. The following graph (rendered directly from [`sql_agent.py`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider/sql_agent.py)) illustrates how the agent drafts, executes, critiques, and refines queries until a satisfactory result is achieved.

```
---
config:
  flowchart:
    curve: linear
---
graph LR;
        __start__([<p>__start__</p>]):::first
        write_query(write_query)
        execute_query(execute_query)
        check_query(check_query)
        rewrite_query(rewrite_query)
        __end__([<p>__end__</p>]):::last
        __start__ --> write_query;
        check_query -.-> __end__;
        check_query -.-> rewrite_query;
        execute_query --> check_query;
        rewrite_query --> execute_query;
        write_query --> execute_query;
        classDef default fill:#f2f2f2,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#cccccc
```

Note

The workflow proceeds through the following stages:

1. **write\_query** – Generates an initial SQL query from the user’s question and the database schema.
2. **execute\_query** – Executes the generated query against the target database.
3. **check\_query** – Evaluates the query and its results (or errors) using a specialized prompt (`CHECK_QUERY_PROMPT`) to detect issues.
4. **rewrite\_query** – If issues are identified, the agent rewrites the query using feedback from the previous step and re-enters the loop.
5. **END** – The cycle terminates when the query is validated or the maximum iteration count (`max_turns`) is reached. Each *turn* consists of one full loop through the `write_query`, `execute_query`, `check_query`, and (if applicable) `rewrite_query` stages.

In this tutorial, **reinforcement learning (RL)** is used to optimize the `write_query` and `rewrite_query` stages. While the `check_query` step shares the same underlying LLM weights, its trace data is not used for learning.

To keep the design modular and maintainable, it is recommended to define the LangGraph-based SQL Agent in a separate file and expose it via a builder function such as:

```
def build_langgraph_sql_agent(
    database_path: str,
    openai_base_url: str,
    model: str,
    sampling_parameters: Dict[str, Any],
    max_turns: int,
    truncate_length: int
):
    builder = StateGraph(State)
    builder.add_node(write_query)
    ...

    builder.add_edge(START, "write_query")
    ...

    return builder.compile().graph()
```

This approach isolates your LangGraph logic from Agent-lightning version changes, improving both readability and debuggability.

## Bridging LangGraph and Agent-lightning[¶](#bridging-langgraph-and-agent-lightning "Permanent link")

Tip

Keep [`sql_agent.py`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider/sql_agent.py) open on the side while reading this section. This will help you understand how the code snippets shown here work in practice.

The **`LitSQLAgent`** class defined in [`sql_agent.py`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider/sql_agent.py) acts as the bridge. It subclasses [`agl.LitAgent`](../../reference/agent/#agentlightning.LitAgent "            agentlightning.LitAgent"), allowing the runner to provision shared resources (e.g., [LLMs](../../reference/types/#agentlightning.LLM "            agentlightning.LLM")) for each rollout.

Below is a simplified illustration of the key logic (note: this is conceptual pseudocode; the actual implementation includes dataset-specific details):

```
class LitSQLAgent(agl.LitAgent[Dict[str, Any]]):

    def __init__(self, max_turns: int, truncate_length: int):
        # Every turn here refers to a full cycle of write/exe/check/rewrite
        self.max_turns = max_turns
        self.truncate_length = truncate_length

    def rollout(
        self,
        task: Dict[str, Any],
        resources: agl.NamedResources,
        rollout: agl.Rollout
    ) -> float | None:
        llm: agl.LLM = resources["main_llm"]
        agent = build_langgraph_sql_agent(
            database_path="sqlite:///" + task["db_id"],
            max_turns=self.max_turns,
            truncate_length=self.truncate_length,
            openai_base_url=llm.get_base_url(rollout.rollout_id, rollout.attempt.attempt_id),
            model=llm.model,
            sampling_parameters=llm.sampling_parameters,
        )
        result = agent.invoke({"question": question}, {
            "callbacks": [self.tracer.get_langchain_handler()],
            "recursion_limit": 100,
        })
        reward = evaluate_query(result["query"], ground_truth, db_path, raise_on_error=False)
        return reward
```

The `LitSQLAgent` serves as a lightweight wrapper around the LangGraph agent, providing the correct interface for the [`rollout`](../../reference/agent/#agentlightning.LitAgent.rollout "            rollout(task, resources, rollout)") method. It constructs the LangGraph agent, invokes it, and returns the evaluation result as a reward signal.

The `"main_llm"` resource key is a convention between the agent and [VERL](../../algorithm-zoo/verl/#agentlightning.algorithm.verl.VERL "            VERL"). It is used to inject an OpenAI-compatible endpoint from the [VERL](../../algorithm-zoo/verl/#agentlightning.algorithm.verl.VERL "            VERL") algorithm during rollout. Two approaches are supported to use this [agentlightning.LLM](../../reference/types/#agentlightning.LLM "            agentlightning.LLM") resource:

1. **Direct access** – Use [`llm.endpoint`](../../reference/types/#agentlightning.LLM.endpoint "            endpoint

     
         instance-attribute
     ") for a simple integration (identical to the v0.1 example).
2. **Context-aware access** – Use [`get_base_url`](../../reference/types/#agentlightning.ProxyLLM.get_base_url "            get_base_url(rollout_id, attempt_id)") with [`rollout.rollout_id`](../../reference/types/#agentlightning.Rollout.rollout_id "            rollout_id

     
         instance-attribute
     ") and [`rollout.attempt.attempt_id`](../../reference/types/#agentlightning.Attempt.attempt_id "            attempt_id

     
         instance-attribute
     ").
   This approach enables per-caller trace attribution, improving trace collection per rollout or attempt when runner-side tracers are unavailable. For details, see [Working with Traces](../../tutorials/traces/).

## Reward Signal and Evaluation[¶](#reward-signal-and-evaluation "Permanent link")

The `evaluate_query` function provides the reward mechanism for RL training. In agent training, obtaining a consistent and meaningful reward signal is often challenging. Fortunately, this is simplified when using the [**Spider dataset**](https://yale-lily.github.io/spider). The dataset includes ~8k samples containing natural-language questions, database schemas, and ground-truth SQL queries.

Using the [**Spider evaluator**](https://github.com/taoyds/test-suite-sql-eval), the agent's generated query is executed and compared to the ground-truth query on the target database. The two queries are considered equivalent if they produce identical execution results.

Attention

The ground-truth queries must **never** be exposed to the agent during training to prevent data leakage.

In this setup, the reward is returned directly from the [`rollout`](../../reference/agent/#agentlightning.LitAgent.rollout "            rollout(task, resources, rollout)") method, enabling the runner to forward it back to the RL algorithm.

Warning

Avoid using [`emit_reward`](../../reference/agent/#agentlightning.emit_reward "            agentlightning.emit_reward(reward)") in conjunction with returning a reward value. Doing both will cause the algorithm to receive duplicate reward signals, leading to inconsistent training behavior.

## Configuring VERL for Reinforcement Learning[¶](#configuring-verl-for-reinforcement-learning "Permanent link")

View [`examples/spider/train_sql_agent.py`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider/train_sql_agent.py) for a full reinforcement learning configuration, which is a plain Python dictionary. It mirrors (and actually *is*) the [shell arguments](https://verl.readthedocs.io/en/latest/index.html) used to launch training in the VERL framework but is easier to tweak programmatically:

```
verl_config: Dict[str, Any] = {
    "algorithm": {"adv_estimator": "grpo", "use_kl_in_reward": False},
    "data": {
        # train_files and val_files are no longer needed here
        # because data are read in agl.Trainer
        ...,
        # Controls how many tasks are pooled per step
        # (multiplied by actor_rollout_ref.rollout.n)
        "train_batch_size": 32,
        # Prompt and responses larger than these lengths are truncated
        "max_prompt_length": 4096,
        "max_response_length": 2048,
    },
    "actor_rollout_ref": {
        "rollout": {
            # Only vLLM is supported currently
            "name": "vllm",
            # Equals to group size of GRPO
            "n": 4,
            # Used to enable tool call parser in vLLM
            "multi_turn": {"format": "hermes"},
            ...
        },
        "actor": {"ppo_mini_batch_size": 32, "optim": {"lr": 1e-6}, ...},
        "model": {
            # Config your preferred LLM here
            "path": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
            ...
        },
    },
    "trainer": {
        "n_gpus_per_node": 1,
        # Validation once before training starts
        "val_before_train": True,
        # Validation every N training steps
        "test_freq": 32,
        # Save checkpoints every N training steps
        "save_freq": 64,
        # Go through the train dataset this many times
        "total_epochs": 2
    },
}
```

This is equivalent to the following CLI invocation:

```
python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    algorithm.use_kl_in_reward=False \
    data.train_batch_size=32 \
    data.max_prompt_length=4096 \
    data.max_response_length=2048 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.n=4 \
    actor_rollout_ref.rollout.multi_turn.format=hermes \
    actor_rollout_ref.actor.ppo_mini_batch_size=32 \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.path=Qwen/Qwen2.5-Coder-1.5B-Instruct \
    trainer.n_gpus_per_node=1 \
    trainer.val_before_train=True \
    trainer.test_freq=32 \
    trainer.save_freq=64 \
    trainer.total_epochs=2
```

Warning

We used to provide a CLI called `python -m agentlightning.verl` to launch training in v0.1. This is no longer the recommended approach. Instead, use [`agl.Trainer`](../../reference/trainer/#agentlightning.Trainer "            agentlightning.Trainer") to run VERL and agent runners together, or follow the [debugging tutorial](../../tutorials/debug/) if you want an isolated experience similar to v0.1.

## Orchestrating Training with [`Trainer`](../../reference/trainer/#agentlightning.Trainer " agentlightning.Trainer")[¶](#orchestrating-training-with-trainer "Permanent link")

[`Trainer`](../../reference/trainer/#agentlightning.Trainer "            agentlightning.Trainer") is the high-level orchestrator that integrates the agent, algorithm, dataset, and distributed runners. The key benefits of using the [`Trainer`](../../reference/trainer/#agentlightning.Trainer "            agentlightning.Trainer") are:

1. It allows you to launch everything with a single line of code: `trainer.fit(...)`.
2. It exposes configuration options such as `n_runners` to control parallelism and `adapter` to define how algorithms interpret the trace data produced by the agent.

An example usage is shown below:

```
import agentlightning as agl

agent = LitSQLAgent()
algorithm = agl.VERL(verl_config)
trainer = agl.Trainer(
    n_runners=10,
    algorithm=algorithm,
    adapter={"agent_match": active_agent},
)
train_data = pd.read_parquet("data/train_spider.parquet").to_dict("records")
val_data = pd.read_parquet("data/test_dev_500.parquet").to_dict("records")
trainer.fit(agent, train_dataset=train_data, val_dataset=val_data)
```

First, `agl.VERL(verl_config)` launches the [`VERL`](../../algorithm-zoo/verl/#agentlightning.algorithm.verl.VERL "            VERL") algorithm and its OpenAI-compatible proxy. The `train_data` and `val_data` are passed into [`VERL`](../../algorithm-zoo/verl/#agentlightning.algorithm.verl.VERL "            VERL"), which enqueues tasks to a centralized task queue managed by the [`LightningStore`](../../reference/store/#agentlightning.LightningStore "            agentlightning.LightningStore"), accessible to all runners.

When [`Trainer.fit`](../../reference/trainer/#agentlightning.Trainer.fit "            fit(agent, train_dataset=None, *, val_dataset=None)") is called, it launches 10 concurrent runners (as specified by `n_runners=10`). Each runner pulls tasks from the centralized task queue, executes the agent’s [`rollout`](../../reference/agent/#agentlightning.LitAgent.rollout "            rollout(task, resources, rollout)") method, collects traces, and returns rewards to VERL for training.

The [`Adapter`](../../reference/algorithm/#agentlightning.Adapter "            agentlightning.Adapter"), as discussed earlier, is used at the algorithm side, and receives the traces emitted by the agent and runners. The `agent_match` parameter ensures [`VERL`](../../algorithm-zoo/verl/#agentlightning.algorithm.verl.VERL "            VERL") only ingests spans from the specific agent you want to optimize.
In the example above, there are at least three agents—`write_query`, `rewrite_query`, and `check_query`. By setting `agent_match` to a regex like `"write"`, both `write_query` and `rewrite_query` agents are optimized simultaneously. You can also set it to `"write|check"` or `None` to include all agents if desired.

## Dry-Run the Pipeline with [`Trainer.dev`](../../reference/trainer/#agentlightning.Trainer.dev " dev(agent, train_dataset=None, *, val_dataset=None)")[¶](#dry-run-the-pipeline-with-trainerdev "Permanent link")

Before committing hours of GPU time, you can **dry-run** the agent with [`Trainer.dev()`](../../reference/trainer/#agentlightning.Trainer.dev "            dev(agent, train_dataset=None, *, val_dataset=None)"). This method swaps in the lightweight [`Baseline`](../../reference/algorithm/#agentlightning.Baseline "            agentlightning.Baseline") algorithm, enqueues up to ten tasks, and prints every span emitted by the agent. Because it uses the same runner stack as full training, it’s ideal for verifying database connections and LangGraph control flow.

To begin, the agent needs a valid OpenAI-compatible endpoint since VERL is not active in this mode. You can use OpenAI’s official API or your own local LLM endpoint. Wrap it as follows:

```
trainer = agl.Trainer(
    n_workers=1,
    initial_resources={
        "main_llm": agl.LLM(
            endpoint=os.environ["OPENAI_API_BASE"],
            model="gpt-4.1-nano",
            sampling_parameters={"temperature": 0.7},
        )
    },
)
```

Then, call [`trainer.dev(...)`](../../reference/trainer/#agentlightning.Trainer.dev "            dev(agent, train_dataset=None, *, val_dataset=None)") with a small number of tasks:

```
dev_data = pd.read_parquet("data/test_dev_500.parquet").to_dict("records")[:10]
trainer.dev(agent, dev_dataset=dev_data)
```

Run this in a Python session or adapt your script to include a `--dev` flag. Once the spans appear healthy and the rewards are non-zero, switch back to [`trainer.fit(...)`](../../reference/trainer/#agentlightning.Trainer.fit "            fit(agent, train_dataset=None, *, val_dataset=None)") for full RL training. See the [debugging tutorial](../../tutorials/debug/) for more tips on how to debug the agent.

## Running the Sample Code[¶](#running-the-sample-code "Permanent link")

The following tutorial explains how to run the complete example in [`examples/spider`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider).

### Dataset[¶](#dataset "Permanent link")

The trainer expects three Parquet files inside `examples/spider/data`:
`train_spider.parquet`, `test_dev_500.parquet`, and `test_dev.parquet`.

Download the curated dataset bundle provided with the repository:

```
cd examples/spider
pip install gdown  # included in the 'experiment' optional dependency
gdown --fuzzy https://drive.google.com/file/d/1oi9J1jZP9TyM35L85CL3qeGWl2jqlnL6/view
unzip -q spider-data.zip -d data
rm spider-data.zip
```

If you prefer to generate the files yourself, download [Spider 1.0](https://yale-lily.github.io/spider) and run:

```
python spider_eval/convert_dataset.py
```

Set `VERL_SPIDER_DATA_DIR` if you store the dataset outside the default `data` directory.

### Dependencies[¶](#dependencies "Permanent link")

Create a clean virtual environment, activate it, and install Agent-lightning with the VERL extras required by [this tutorial](../../tutorials/installation/). Install LangChain-related dependencies as needed.

For full training profiles, plan to use a GPU with at least **40 GB** of memory.

### Launch Training[¶](#launch-training "Permanent link")

From [`examples/spider`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider), run one of the helper scripts depending on your model preference:

```
python train_sql_agent.py qwen   # Default Qwen-2.5-Coder-1.5B run
python train_sql_agent.py llama  # LLaMA-3.2-1B with llama3_json tool parser
```

The script instantiates `LitSQLAgent` and launches [`trainer.fit`](../../reference/trainer/#agentlightning.Trainer.fit "            fit(agent, train_dataset=None, *, val_dataset=None)").
Provide `--active-agent my_agent_variant` if you only want to train one of the agents in the graph.

For the LLaMA profile, export an `HF_TOKEN` before running so VERL can download the model weights.

Troubleshooting

If you have got some Ray worker errors on either `WANDB_API_KEY` not set, or `HF_TOKEN` not set, or data not found, please try to restart the Ray cluster with the helper script: [scripts/restart\_ray.sh](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/scripts/restart_ray.sh), which essentially stops the ray cluster if any, and starts a new one:

```
env RAY_DEBUG=legacy HYDRA_FULL_ERROR=1 VLLM_USE_V1=1 ray start --head --dashboard-host=0.0.0.0
```

### Debugging the Agent without VERL[¶](#debugging-the-agent-without-verl "Permanent link")

[`sql_agent.py`](https://github.com/microsoft/agent-lightning/tree/e49b75b7d836eeab35323ce36ed5f4e2f61009b9/examples/spider/sql_agent.py) also provides a `debug_sql_agent()` helper to run the LangGraph workflow directly against a local or hosted OpenAI-compatible endpoint before using VERL.

Set the following environment variables, then execute the file:

```
export OPENAI_API_BASE=<your_api_base>
export OPENAI_API_KEY=<your_api_key>
cd examples/spider
python sql_agent.py
```

This allows you to verify that the workflow and prompts behave as expected before reinforcement learning is introduced.

### Evaluation[¶](#evaluation "Permanent link")

The following results were obtained by running `python train_sql_agent.py qwen` on a single 80 GB GPU.
Training completes in approximately **12 hours**.
The training curves below are smoothed by aggregating every 16 steps for better visualization.

Additional evaluation results were collected with a legacy version — Agent-lightning v0.1.1, `verl==0.5.0`, and `vllm==0.10.0`.
You can find them in this write-up:
[Training AI Agents to Write and Self-Correct SQL with Reinforcement Learning](https://medium.com/@yugez/training-ai-agents-to-write-and-self-correct-sql-with-reinforcement-learning-571ed31281ad)