# 我问
详细描述数据集合成过程

# deepwiki答


根据代码库上下文,您询问的是数据集合成(dataset preparation)过程<cite/>。这个代码库包含多个数据集准备系统,主要集中在两个框架中:

## SkyRL 数据集准备流程

SkyRL框架定义了标准的数据集格式要求 [1](#0-0) 。每个数据集条目必须包含:

- `data_source`: 数据源标识符
- `prompt`: OpenAI聊天格式的对话列表
- `env_class`: 环境类标识符
- `reward_spec`: 奖励规范(包含方法和ground_truth)
- `extra_info`: 可选的额外元数据

数据集最终加载为HuggingFace的`DatasetDict`格式 [2](#0-1) 。

转换过程通过实现`make_map_fn`方法完成 [3](#0-2) 。以SynSQL数据集为例,该函数将原始数据转换为所需格式,包括构建用户内容、设置环境类和奖励规范。

## MS-SWIFT 数据集准备流程

MS-SWIFT框架使用预处理器(Preprocessor)类来转换数据集 [4](#0-3) 。

### 多模态任务数据集

对于多模态GRPO训练,数据集需要包含`messages`、`images`和`solution`字段 [5](#0-4) 。预处理器通过继承`ResponsePreprocessor`并重写`preprocess`方法来修改查询内容 [6](#0-5) 。

### 常规数据集转换

各种预处理器类处理不同格式的数据:
- `AlpacaPreprocessor`: 处理Alpaca格式数据 [7](#0-6) 
- `ResponsePreprocessor`: 处理查询-响应对 [8](#0-7) 
- `RowPreprocessor`: 处理原始行数据 [9](#0-8) 

所有数据集通过`register_dataset`函数注册,指定数据集ID、预处理函数和标签 [10](#0-9) 。

### Reranker数据集

Reranker任务需要特定格式,原始数据包含`query`、`positive`和`negative`字段,需转换为包含`query`、`response`和`rejected_response`的格式 [11](#0-10) 。

## Notes

两个框架的数据集准备流程都遵循类似模式:定义标准格式→实现转换函数→注册数据集。SkyRL侧重于强化学习任务,而MS-SWIFT支持更广泛的任务类型(聊天、多模态、分类等)。数据集统计信息可通过`run_dataset_info.py`脚本获取 [12](#0-11) 。

### Citations

**File:** deepanalyze/SkyRL/skyrl-train/docs/datasets/dataset-preparation.rst (L13-33)
```text
Each dataset entry is a dictionary with the following required (and some optional) values:

.. code-block:: python

   data = {
       "data_source": data_source,     # String: Name/identifier of the data source
       "prompt": [                     # List: Conversation format
           {
               "role": "user",            
               "content": question,       
           }
       ],
       "env_class": env_class,         # String: Environment class identifier
       "reward_spec": {
           "method": "rule",           # String: Either "rule" or "reward_model"
           "ground_truth": solution,   # Expected solution
       },
       "extra_info": {                 # Dict: Optional additional metadata
           # ... add your own fields here
       },
   }
```

**File:** deepanalyze/SkyRL/skyrl-train/docs/datasets/dataset-preparation.rst (L35-35)
```text
We load the dataset as a huggingface `DatasetDict <https://huggingface.co/docs/datasets/en/package_reference/main_classes#datasets.DatasetDict>`_.
```

**File:** deepanalyze/SkyRL/skyrl-train/docs/datasets/dataset-preparation.rst (L59-90)
```text
Generally, only a single method (`make_map_fn`) must be implemented to convert the new dataset into the required format. Below is an example of converting the SynSQL text-to-SQL dataset into the required format:

.. code-block:: python

  def make_map_fn(split):
        def process_fn(example, idx):
            """Transform each dataset example into the required format"""
            if split == "train":
                user_content = ("{db_details}:" + example["schema"] + 
                              ";\n {external_knowledge}: " + example["external_knowledge"] + 
                              ";\n {question}: " + example["question"])
            else:
                user_content = ("{db_details}:" + example["schema"] + 
                              "; {question}: " + example["question"])
            
            data = {
                "data_source": "synsql",
                "prompt": [
                    {"role": "system", "content": short_system_prompt},
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ],
                "env_class": "text2sql",
                "reward_spec": {
                    "method": "rule",
                    "ground_truth": example["sql"],
                },
                # Custom fields specific to the SynSQL dataset:
                "db_id": example["db_id"],
                "data": example["data"],
```

**File:** deepanalyze/ms-swift/swift/llm/dataset/dataset/llm.py (L11-13)
```python
from ..preprocessor import (AlpacaPreprocessor, ClsGenerationPreprocessor, ClsPreprocessor, MessagesPreprocessor,
                            ResponsePreprocessor, RowPreprocessor, TextGenerationPreprocessor)
from ..register import DatasetMeta, SubsetDataset, register_dataset
```

**File:** deepanalyze/ms-swift/swift/llm/dataset/dataset/llm.py (L16-22)
```python
class AlpacaZhPreprocessor(AlpacaPreprocessor):

    @classmethod
    def concat_inst_input(cls, instruction, input_):
        if input_ and input_.startswith('输入：'):
            input_ = input_[3:]
        return super().concat_inst_input(instruction, input_)
```

**File:** deepanalyze/ms-swift/swift/llm/dataset/dataset/llm.py (L25-31)
```python
register_dataset(
    DatasetMeta(
        ms_dataset_id='AI-ModelScope/alpaca-gpt4-data-zh',
        hf_dataset_id='llm-wizard/alpaca-gpt4-data-zh',
        preprocess_func=AlpacaZhPreprocessor(),
        tags=['chat', 'general', '🔥'],
    ))
```

**File:** deepanalyze/ms-swift/swift/llm/dataset/dataset/llm.py (L78-87)
```python
class MathTrnPreprocessor(ResponsePreprocessor):

    def preprocess(self, row):
        query = row['query']
        output = row['response']
        row = {
            'query': query,
            'response': output,
        }
        return super().preprocess(row)
```

**File:** deepanalyze/ms-swift/swift/llm/dataset/dataset/llm.py (L587-603)
```python
class DureaderPreprocessor(RowPreprocessor):

    def preprocess(self, row: Dict[str, Any]) -> Dict[str, Any]:
        prompt = """Task: Question Generation
Context: {context}
Answer: {answer}
Question:"""
        answer, context = row['text1'].split('[SEP]')
        return {
            'messages': [{
                'role': 'user',
                'content': prompt.format(context=context, answer=answer)
            }, {
                'role': 'assistant',
                'content': row['text2']
            }]
        }
```

**File:** deepanalyze/ms-swift/docs/source_en/BestPractices/GRPO-Multi-Modal-Training.md (L14-35)
```markdown
class ClevrPreprocessor(ResponsePreprocessor):

    def preprocess(self, row: Dict[str, Any]) -> Dict[str, Any]:
        query = row.get('query', '')
        query = f"""{query} Output the thinking process in <think> </think> and
 final answer (number) in <answer> </answer> tags."""
        row.update({'query': query})
        return super().preprocess(row)


register_dataset(
    DatasetMeta(
        ms_dataset_id='okwinds/clevr_cogen_a_train',
        subsets=[
            SubsetDataset(
                name='default',
                subset='default',
                split=['train'],
            ),
        ],
        preprocess_func=ClevrPreprocessor(),
        tags=['qa', 'math']))
```

**File:** deepanalyze/ms-swift/docs/source_en/BestPractices/GRPO-Multi-Modal-Training.md (L38-53)
```markdown
The purpose of redefining the dataset preprocessor here is to modify the query. A sample dataset entry is as follows, including `messages`, `images`, and `solution` fields. The `solution` is used in the reward function, while `messages` and `images` serve as model input.
- Note: `{'role': 'assistant', 'content': '<answer> 3 </answer>'}` will be removed in GRPOTrainer and can be ignored. The 'solution' field will be passed directly into the ORM. When creating a custom dataset, the 'images' field should be organized as `["image_path1", "image_path2"]`.

```json
{
    "images": ["image_path1", "image_path2"],
    "messages": [
        {
            "role": "user",
            "content": "How many items are there in the image? Output the thinking process in <think> </think> and\n final answer (number) in <answer> </answer> tags."
        }
    ],
    "solution": "<answer> 3 </answer>"
}

```
```

**File:** deepanalyze/ms-swift/docs/source_en/BestPractices/Reranker.md (L67-83)
```markdown
### Common Original Data Format

```json lines
{"query": "query", "positive": ["relevant_doc1", "relevant_doc2", ...], "negative": ["irrelevant_doc1", "irrelevant_doc2", ...]}
```

> Reference: [MTEB/scidocs-reranking](https://www.modelscope.cn/datasets/MTEB/scidocs-reranking)

### Converted Data Format

```json lines
{"query": "query", "response": "relevant_doc1", "rejected_response": ["irrelevant_doc1", "irrelevant_doc2", ...]}
{"query": "query", "response": "relevant_doc2", "rejected_response": ["irrelevant_doc1", "irrelevant_doc2", ...]}
...
```

> The final converted data format is required, developers can build their own dataset or reuse [MTEBRerankPreprocessor](https://github.com/modelscope/ms-swift/blob/main/swift/llm/dataset/dataset/llm.py#L381) to convert data format.
```

**File:** deepanalyze/ms-swift/scripts/utils/run_dataset_info.py (L45-85)
```python
def run_dataset(key, template, cache_mapping):
    ms_id, hf_id, _ = key
    dataset_meta = DATASET_MAPPING[key]
    tags = ", ".join(tag for tag in dataset_meta.tags) or "-"
    dataset_id = ms_id or hf_id
    use_hf = ms_id is None
    if ms_id is not None:
        ms_id = f"[{ms_id}](https://modelscope.cn/datasets/{ms_id})"
    else:
        ms_id = "-"
    if hf_id is not None:
        hf_id = f"[{hf_id}](https://huggingface.co/datasets/{hf_id})"
    else:
        hf_id = "-"
    subsets = "<br>".join(subset.name for subset in dataset_meta.subsets)

    if dataset_meta.huge_dataset:
        dataset_size = "huge dataset"
        stat_str = "-"
    elif dataset_id in cache_mapping:
        dataset_size, stat_str = cache_mapping[dataset_id]
    else:
        num_proc = 4
        dataset, _ = load_dataset(
            f"{dataset_id}:all", strict=False, num_proc=num_proc, use_hf=use_hf
        )
        dataset_size = len(dataset)
        random_state = np.random.RandomState(42)
        idx_list = random_state.choice(
            dataset_size, size=min(dataset_size, 100000), replace=False
        )
        encoded_dataset = EncodePreprocessor(template)(
            dataset.select(idx_list), num_proc=num_proc
        )

        input_ids = encoded_dataset["input_ids"]
        token_len = [len(tokens) for tokens in input_ids]
        stat = stat_array(token_len)[0]
        stat_str = f"{stat['mean']:.1f}±{stat['std']:.1f}, min={stat['min']}, max={stat['max']}"

    return f"|{ms_id}|{subsets}|{dataset_size}|{stat_str}|{tags}|{hf_id}|"
```

# 我问
能否详细展开描述「推理轨迹合成」以及「交互轨迹合成」的整个过程

# deepwiki答


您询问的是**推理轨迹合成**和**交互轨迹合成**的过程<cite/>。根据代码库上下文,这两个概念主要在SkyRL框架中实现,分别对应不同的轨迹生成模式<cite/>。

## 推理轨迹合成(Inference Trajectory Generation)

推理轨迹合成是指通过模型推理生成单次或多次交互的完整轨迹 [1](#1-0) 。

### 核心流程

1. **轨迹初始化**:通过`agent_loop`方法启动单个轨迹的生成 [2](#1-1) 。创建环境实例,初始化对话历史,并获取初始提示 [3](#1-2) 。

2. **多轮推理循环**:在`while not done`循环中执行多轮推理 [4](#1-3) 。每轮包括:
   - 调用推理引擎生成模型输出 [5](#1-4) 
   - 环境执行动作并返回观察、奖励和完成状态 [6](#1-5) 
   - 更新对话历史或token序列 [7](#1-6) 

3. **批量生成**:通过`generate`方法并行生成多个轨迹 [8](#1-7) 。使用异步任务并发执行多个`agent_loop` [9](#1-8) 。

4. **输出处理**:收集所有轨迹的响应、奖励、停止原因等信息 [10](#1-9) 。

## 交互轨迹合成(Interactive Trajectory Generation)

交互轨迹合成是指通过Agent与环境交互生成轨迹,主要在SkyAgent框架中实现 [11](#1-10) 。

### 核心组件

1. **Trajectory类**:负责生成单个轨迹 [12](#1-11) 。包含三个关键方法:
   - `initialize_trajectory`:初始化运行时环境 [13](#1-12) 
   - `generate_trajectory`:执行Agent循环生成轨迹 [14](#1-13) 
   - `evaluate_trajectory`:评估轨迹结果 [15](#1-14) 

2. **Agent执行**:Agent通过`step`方法与环境交互 [16](#1-15) 。每步包括格式化消息、调用LLM、解析工具调用等 [17](#1-16) 。

3. **Dispatcher调度**:使用Dispatcher并发执行多个轨迹 [18](#1-17) 。Pipeline dispatcher按阶段(初始化、生成、评估)流水线执行 [19](#1-18) 。

4. **AgentRunner协调**:通过`run`方法协调整个流程 [20](#1-19) 。初始化轨迹、调用dispatcher、后处理结果 [21](#1-20) 。

### 多轮交互支持

MS-SWIFT框架也支持多轮交互轨迹生成 [22](#1-21) 。通过`async_infer`方法实现循环推理,每轮检查是否应该停止,并通过`multi_turn_scheduler`控制交互流程 [23](#1-22) 。

## Notes

两种轨迹合成方式的主要区别:
- **推理轨迹合成**侧重于高效的批量推理,适用于训练场景,通过`SkyRLGymGenerator`实现
- **交互轨迹合成**侧重于灵活的Agent-环境交互,适用于评估和复杂任务,通过`SkyAgent`框架实现

两者都支持多轮交互,但实现方式不同:前者在Generator层面管理多轮,后者通过Agent和Task抽象管理多轮<cite/>。配置参数如`max_turns`、`max_iterations`控制交互轮数 [24](#1-23) 。

### Citations

**File:** deepanalyze/SkyRL/skyrl-train/skyrl_train/generators/skyrl_gym_generator.py (L73-98)
```python
    async def agent_loop(
        self,
        prompt: ConversationType,
        env_class: str,
        env_extras: List[Dict[str, Any]],
        max_tokens: int,
        max_input_length: int,
        sampling_params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[int], float, str, List[int], List[int], Optional[List[float]]]:
        """
        Multi-turn generation loop that executes a single trajectory.

        Args:
            prompt: ConversationType
            env_extras: List[Dict[str, Any]]
            max_tokens: int
            max_input_length: int
            sampling_params: Optional[Dict[str, Any]]
        Returns:
            response_ids: List[int]
            reward: float
            stop_reason: str
            loss_mask: List[int]
            prompt_token_ids: List[int]
            rollout_logprobs: Optional[List[float]]
        """
```

**File:** deepanalyze/SkyRL/skyrl-train/skyrl_train/generators/skyrl_gym_generator.py (L99-112)
```python
        # Create a new environment instance
        env_extras["max_turns"] = self.max_turns  # TODO(shu): move this to config
        env_config = self.skyrl_gym_cfg.get(env_class, DictConfig({}))
        env = skyrl_gym.make(env_class, env_config=env_config, extras=env_extras)

        trajectory_id = uuid4().hex
        done = False

        # need copy here since the prompt is a list of messages and we are going to modify it
        chat_history = copy.deepcopy(prompt)
        chat_end_index = len(chat_history)

        # Init() returns the first prompt to be given to the model, and optional metadata dict
        chat_history, _ = env.init(chat_history)
```

**File:** deepanalyze/SkyRL/skyrl-train/skyrl_train/generators/skyrl_gym_generator.py (L127-180)
```python
        while not done:
            if self.use_conversation_multi_turn:
                engine_input = InferenceEngineInput(
                    prompts=[chat_history],
                    trajectory_ids=[trajectory_id],
                    sampling_params=sampling_params,
                )
            else:
                engine_input = InferenceEngineInput(
                    prompt_token_ids=[input_ids],
                    trajectory_ids=[trajectory_id],
                    sampling_params=sampling_params,
                )
            engine_output = await self.inference_engine_client.generate(engine_input)

            output = engine_output["responses"][0]
            stop_reason = engine_output["stop_reasons"][0]

            if self.env_executor is not None:
                loop = asyncio.get_running_loop()
                env_step_output: BaseTextEnvStepOutput = await loop.run_in_executor(
                    self.env_executor, env.step, output
                )
            else:
                env_step_output: BaseTextEnvStepOutput = env.step(output)
            new_obs = env_step_output["observations"]
            reward = env_step_output["reward"]
            done = env_step_output["done"]

            if env_step_output.get("postprocessed_action", None) is not None:
                output = env_step_output["postprocessed_action"]

            if self.use_conversation_multi_turn:
                chat_history, chat_end_index, loss_mask, input_ids = (
                    self._update_engine_input_chat_history(
                        chat_history,
                        chat_end_index,
                        loss_mask,
                        input_ids,
                        output,
                        new_obs,
                    )
                )
            else:
                loss_mask, input_ids, rollout_logprobs = (
                    self._update_engine_input_token_ids(
                        output, new_obs, loss_mask, input_ids, rollout_logprobs
                    )
                )

            if len(input_ids) > max_input_length:
                stop_reason = "length"
                break
            step += 1
```

**File:** deepanalyze/SkyRL/skyrl-train/skyrl_train/generators/skyrl_gym_generator.py (L321-365)
```python
    async def generate(self, input_batch: GeneratorInput) -> GeneratorOutput:
        """
        Generate trajectories for the input batch.

        Returns outputs in the same order as the input batch.
        Args:
            input_batch: GeneratorInput
        Returns:
            GeneratorOutput
        """
        prompts = input_batch["prompts"]
        env_classes = input_batch["env_classes"]
        env_extras = input_batch["env_extras"]
        sampling_params: Optional[dict] = input_batch.get("sampling_params", None)
        max_tokens = self.generator_cfg.sampling_params.max_generate_length
        max_input_length = self.generator_cfg.max_input_length

        if self.batched:
            return await self.generate_batched(
                prompts,
                env_classes,
                env_extras,
                max_tokens,
                max_input_length,
                sampling_params,
            )
        # Async agent loop to generate trajectories in parallel.
        tasks = []
        for i in range(len(prompts)):
            tasks.append(
                self.agent_loop(
                    prompts[i],
                    env_classes[i],
                    env_extras[i],
                    max_tokens,
                    max_input_length,
                    sampling_params=sampling_params,
                )
            )
        all_outputs = await tqdm.gather(
            *tasks,
            desc="Generating Trajectories",
            miniters=max(1, len(tasks) // 10),
            mininterval=5,
        )
```

**File:** deepanalyze/SkyRL/skyrl-train/skyrl_train/generators/skyrl_gym_generator.py (L367-407)
```python
        responses = [output[0] for output in all_outputs]
        rewards = [output[1] for output in all_outputs]
        print("all_rewards", rewards)
        stop_reasons = [output[2] for output in all_outputs]
        loss_masks = [output[3] for output in all_outputs]
        prompt_token_ids = [output[4] for output in all_outputs]

        if sampling_params is not None:
            # sampling params will be a dict in the format of the inference engine backend
            # TODO: this might have to change when we support logprobs for sglang
            get_logprobs = sampling_params.get("logprobs", None) is not None
        else:
            get_logprobs = self.generator_cfg.sampling_params.logprobs is not None

        if get_logprobs:
            rollout_logprobs = [output[5] for output in all_outputs]
        else:
            rollout_logprobs = None

        rollout_metrics = self._rollout_metrics(responses, rewards)

        if self.generator_cfg.zero_reward_on_non_stop:
            # set reward to 0 if the stop reason is not "stop"
            rewards = self._zero_reward_if_not_stop(rewards, stop_reasons)

        if self.generator_cfg.apply_overlong_filtering:
            loss_masks = apply_overlong_filtering(
                loss_masks, responses, self.tokenizer.eos_token_id
            )

        generator_output: GeneratorOutput = {
            "prompt_token_ids": prompt_token_ids,
            "response_ids": responses,
            "rewards": rewards,
            "loss_masks": loss_masks,
            "stop_reasons": stop_reasons,
            "rollout_metrics": rollout_metrics,
            "rollout_logprobs": rollout_logprobs,
        }

        return generator_output
```

**File:** deepanalyze/SkyRL/skyrl-train/docs/skyagent/agent-overview.rst (L44-62)
```text
Trajectory
----------

The trajectory class handles generating a single trajectory for the given instance from the batch. It has three methods:

1. ``initialize_trajectory``: Initialize the trajectory eg: setup any runtime environment needed for the agent to run.
2. ``generate_trajectory``: Generate the trajectory i.e. run the agent loop and get the final conversation and task results. 
3. ``evaluate_trajectory``: Evaluate the trajectory i.e. parse the final result and evaluate it for the given task.


The results of both ``generate_trajectory`` and ``evaluate_trajectory`` are stored in a ``.result`` attribute of the trajectory. Each trajectory instance will initialize an ``Agent`` instance to generate responses.

Here's a high-level diagram of the components involved in generating a trajectory:

.. figure:: images/generate_trajectory.png
   :alt: Generate Trajectory
   :align: center
   :width: 80%

```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/base.py (L84-116)
```python
class BaseTrajectory(ABC):

    def __init__(
        self,
        cfg: TrajectoryConfig,
        data: Dict[str, Any],
        infer_engine: AsyncInferBackend,
        tokenizer: AutoTokenizer,
        task: BaseTask,
    ) -> None:
        super().__init__()

        self.cfg = cfg
        self.data = data
        self.infer_engine = infer_engine
        self.tokenizer = tokenizer
        self.task = task
        self.agent_cls = _import_object(cfg.agent_cls)

        self.result: TrajectoryResult = None

    @abstractmethod
    async def initialize_trajectory(self):
        pass

    @abstractmethod
    async def generate_trajectory(self):
        pass

    @abstractmethod
    async def evaluate_trajectory(self):
        pass

```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/base.py (L448-503)
```python
    async def run(self, input_batch: Any, val_mode: bool = False) -> Any:
        """
        Generate trajectories for the given prompts using the configured agents.

        Args:
            prompts: A dictionary containing training instances.
            val_mode: Whether we're running validation.

        Returns:
            Results converted to the appropriate output format based on infer backend.
        """
        self.batch = build_generator_input(
            self.cfg.generator.infer_backend, input_batch
        ).input_batch

        if val_mode:
            num_trajectories = self.cfg.generator.val_config.num_trajectories
            sampling_params = self.cfg.generator.val_config.sampling_params
        else:
            sampling_params = self.cfg.generator.sampling_params
            num_trajectories = self.cfg.generator.num_trajectories

        # Initialize agents and other components
        self._initialize_trajectories(val_mode=val_mode)

        generator_dispatcher: DispatcherType | None = DISPATCHER_REGISTRY.get(
            self.cfg.dispatcher.type
        )
        if not generator_dispatcher:
            raise ValueError(f"Unknown generator type: {self.cfg.dispatcher.type}")
        else:
            logger.info(f"Using generator dispatcher: {self.cfg.dispatcher.type}")
            init_fn = "initialize_trajectory"
            run_fn = "generate_trajectory"
            eval_fn = "evaluate_trajectory"
            dispatcher_cfg = {
                "sampling_params": sampling_params,
                "max_parallel_agents": self.cfg.dispatcher.max_parallel_agents,
                "max_eval_parallel_agents": self.cfg.dispatcher.max_eval_parallel_agents,
                "num_instances": len(self.batch),
                "num_trajectories": num_trajectories,
            }
            await generator_dispatcher(
                dispatcher_cfg,
                self.trajectories,
                init_fn=init_fn,
                run_fn=run_fn,
                eval_fn=eval_fn,
            )

        output = self._post_process_results(val_mode=val_mode)

        # reset after run
        self.trajectories = {}

        return build_generator_output(self.cfg.generator.infer_backend, output).result
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/oh_codeact/codeact_runner.py (L120-171)
```python
    async def initialize_trajectory(self):
        """Initialize the runtime for a specific agent."""
        # only swebench task supported, redundant but makes linter happy
        assert isinstance(self.task, SWEBenchTask)

        batch_id = self.cfg.instance_id
        trajectory_id = self.cfg.trajectory_id

        # data = self._get_data(data)
        data = self.data
        instance_id = data['instance_id'] if data['instance_id'] else batch_id
        instance = pd.Series(data["instance"])
        data_source = data["data_source"]
        self.agent = OHCodeActAgent(traj_config=self.cfg, infer_engine=self.infer_engine, tokenizer=self.tokenizer)
        
        init_successful = False
        try:
            
            runtime = await self.task.initialize_runtime(instance, data_source, self.agent.config, self.cfg.max_iterations)

            app_config = self.task.get_config(instance, data_source, self.agent.config, self.cfg.max_iterations)
            
            # Store the runtime and instruction
            self.agent.runtime = runtime
            self.agent.instruction = self.task.get_instruction(instance, data_source)
            self.agent.app_config = app_config

            init_successful = True 
            logger.info(f"Successfully initialized runtime for instance {instance_id}")
        except Exception as e:
            logger.error(f"Failed to initialize runtime for instance {instance_id}: {str(e)}")
            self.agent.runtime = None
            
            return_val = {
                'instance_id': instance_id,
                'trajectory_id': trajectory_id,
                'messages': [],
                'state': None,
                'results': None,
                'error': str(e),
                'finish': False,
                'finish_reason': 'error_initialization',
            }

            self.result = return_val
        finally:
            if not init_successful: 
                logger.info(f"Init failed. Running cleanup for init agent task for instance {instance_id}, trajectory {trajectory_id}")
                if 'runtime' in locals() and runtime:
                    runtime.event_stream.close()
                    runtime.close() 

```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/oh_codeact/codeact_runner.py (L172-242)
```python
    async def generate_trajectory(self) -> None:
        # only swebench task supported, redundant but makes linter happy
        assert isinstance(self.task, SWEBenchTask)

        data = self.data
        instance_id = data['instance_id'] if data['instance_id'] else self.cfg.instance_id
        trajectory_id = self.cfg.trajectory_id
        instance = pd.Series(data["instance"])
        data_source = data["data_source"]
        agent = self.agent
        runtime = agent.runtime
        state = None

        try:
            if not runtime:
                raise Exception(f"Runtime not initialized for instance {instance_id}, trajectory {trajectory_id}")
            
            state = await run_controller(
                config=agent.app_config,
                initial_user_action=agent.instruction,
                runtime=runtime,
                agent=agent,
                fake_user_response_fn=codeact_user_response,
            )
            if state and is_fatal_evaluation_error(state.last_error):
                raise Exception('Fatal error: ' + state.last_error)

            final_messages = agent.get_final_messages(state)
            result = await call_sync_from_async(self.task.complete_runtime, runtime, instance, data_source)

            finish, finish_reason = agent._is_last_action_finish(state)
            if state and state.last_error:
                if "RuntimeError: Agent reached maximum iteration in headless mode" in state.last_error:
                    finish_reason = 'max_iterations_reached'
                elif "Agent got stuck in a loop" in state.last_error:
                    finish_reason = 'stuck_in_a_loop'
            
            if "finish_reason" in result:
                finish_reason = result["finish_reason"]

            return_val = TrajectoryResult({
                'instance_id': instance_id,
                'trajectory_id': trajectory_id,
                'messages': final_messages,
                'state': state,
                'results': result,
                'error': state.last_error if state and state.last_error else None,
                'finish': finish,
                'finish_reason': finish_reason,
            })
        except Exception as e:
            logger.error(f"Run error {instance_id}: {e}")
            logger.debug(f"Full Traceback: {traceback.format_exc()}")
            final_messages = agent.get_final_messages(state) if state else []
            if not final_messages or len(final_messages) == 0:
                logger.debug(f'Final messages are non-existent (or empty) for instance {instance_id}, trajectory {trajectory_id}')
            return_val = TrajectoryResult({
                'instance_id': instance_id,
                'trajectory_id': trajectory_id,
                'messages': final_messages,
                'state': state,
                'results': None,
                'error': str(e),
                'finish': False,
                'finish_reason': 'error_runtime',
            })
        finally:
            logger.info(f"Running cleanup for run agent task for instance {instance_id}, trajectory {trajectory_id}")
            self._cleanup_agent()

        self.result = return_val
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/react/react_runner.py (L47-66)
```python
    async def evaluate_trajectory(self) -> None:
        instance_id = self.cfg.instance_id
        trajectory_id = self.cfg.trajectory_id
        data = self.data
        instance_id = data['instance_id'] if data['instance_id'] else self.cfg.instance_id
        instance = pd.Series(data["instance"])
        result = self.result.get('results')

        try:
            eval_result = await self.task.evaluate_result(
                result,
                instance,
                data["data_source"],
                instance_id,
                trajectory_id,
            )
            self.result['reward'] = eval_result
        except Exception as e:
            self.result['reward'] = 0
            self.result['eval_error'] = str(e)
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/react/react_agent.py (L50-78)
```python
    async def step(self):
        done = False
        finish_reason = None
        
        self.step_count += 1
        # print(f"[Agent Step {self.step_count}] instance={self.instance_id} traj={self.trajectory_id}")

        formatted_messages = convert_fncall_messages_to_non_fncall_messages(
            self.messages, self.tool_params, add_in_context_learning_example=False
        )
        # print(f"[Agent Step {self.step_count}] Formatted messages: {formatted_messages}, messages: {self.messages}")

        input_ids = self.tokenizer.apply_chat_template(
            formatted_messages,
            add_generation_prompt=True,
            tokenize=True,
            enable_thinking=self.qwen3_enable_thinking,
        )

        if len(input_ids) >= self.max_prompt_length:
            # raise ValueError(
            #     f"Input length {len(input_ids)} exceeds max prompt length {self.max_prompt_length}. "
            #     "Please reduce the input size or increase the max prompt length."
            # )
            # For now, we will just stop the agent if the input length exceeds the max prompt length.
            print(f"[Agent Step] Input length {len(input_ids)} exceeds max prompt length {self.max_prompt_length}. Stopping agent.")
            done = True
            finish_reason = "CONTEXT_WINDOW_EXCEEDED"
            return done, finish_reason, None
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/dispatcher/dispatchers.py (L22-113)
```python
@register_dispatcher("async_pipeline")
async def async_pipeline_dispatcher(
    cfg,
    trajectories: Dict[str, Dict[str, Any]],
    init_fn: str,
    run_fn: str,
    eval_fn: str,
):
    async def pipeline():
        """Pipeline dispatcher for async processing of init, run, and eval functions."""
        # Initialize queues
        init_queue = asyncio.Queue()
        run_queue = asyncio.Queue()
        eval_queue = asyncio.Queue()

        # Get the generator instance from the init function
        max_parallel_agents = cfg["max_parallel_agents"]
        max_eval_parallel_agents = cfg.get(
            "max_eval_parallel_agents", max_parallel_agents
        )

        num_instances = cfg["num_instances"]
        num_trajectories = cfg["num_trajectories"]
        total_instances = num_instances

        max_eval_parallel_agents = min(
            total_instances * num_trajectories, max_eval_parallel_agents
        )
        max_parallel_agents = min(
            total_instances * num_trajectories, max_parallel_agents
        )

        logger.info(
            f"Using max_parallel_agents of {max_parallel_agents} for {total_instances} instances with {num_trajectories} trajectories each"
        )
        logger.info(
            f"Using max_eval_parallel_agents of {max_eval_parallel_agents} for {total_instances} instances with {num_trajectories} trajectories each"
        )

        # Fill the init queue with tasks
        for trajectory_id in range(num_trajectories):
            for instance_id in trajectories.keys():
                await init_queue.put((instance_id, trajectory_id))

        async def initialize_one():
            while True:
                instance_id, trajectory_id = await init_queue.get()
                await getattr(trajectories[instance_id][trajectory_id], init_fn)()
                await run_queue.put((instance_id, trajectory_id))
                init_queue.task_done()

        async def run_one():
            while True:
                instance_id, trajectory_id = await run_queue.get()
                await getattr(trajectories[instance_id][trajectory_id], run_fn)()
                await eval_queue.put((instance_id, trajectory_id))
                run_queue.task_done()

        async def eval_one():
            while True:
                instance_id, trajectory_id = await eval_queue.get()
                await getattr(trajectories[instance_id][trajectory_id], eval_fn)()
                eval_queue.task_done()

        # Create tasks for initialization, running and evaluation
        init_tasks = [
            asyncio.create_task(initialize_one()) for _ in range(max_parallel_agents)
        ]
        run_tasks = [asyncio.create_task(run_one()) for _ in range(max_parallel_agents)]
        eval_tasks = [
            asyncio.create_task(eval_one()) for _ in range(max_eval_parallel_agents)
        ]

        # Wait until all initialization tasks are done
        print("Waiting for initialization tasks to complete...")
        await init_queue.join()
        for task in init_tasks:
            task.cancel()

        print("Initialization tasks completed. Waiting for run tasks to complete...")
        # Wait until all running tasks are done
        await run_queue.join()
        for task in run_tasks:
            task.cancel()

        print("Run tasks completed. Waiting for evaluation tasks to complete...")
        # Wait until all evaluation tasks are done
        await eval_queue.join()
        for task in eval_tasks:
            task.cancel()

    await pipeline()
```

**File:** deepanalyze/ms-swift/swift/llm/infer/infer_engine/grpo_vllm_engine.py (L122-182)
```python
    async def async_infer(self,
                          infer_requests: List[Union[RolloutInferRequest, Dict[str, Any]]],
                          request_config: Optional[RequestConfig] = None,
                          metrics: Optional[List[Metric]] = None,
                          *,
                          use_tqdm: Optional[bool] = None,
                          **kwargs) -> List[ChatCompletionResponse]:
        if request_config is None:
            request_config = RequestConfig()
        # in GRPO n always equals 1
        assert request_config.n == 1

        # change here, multi turn loop
        async def _infer_async_single(infer_request: Union[RolloutInferRequest, Dict[str, Any]],
                                      request_config: Optional[RequestConfig] = None,
                                      **kwargs):
            if isinstance(infer_request, Dict):
                infer_request = RolloutInferRequest(**infer_request)
            current_request = infer_request
            current_turn = 1
            while True:
                messages = current_request.messages
                if current_turn == 1 or not messages[-1]['content']:
                    # If it's the first turn or the last message content is empty(dummy), remove the response
                    InferRequest.remove_response(messages)

                result: ChatCompletionResponse = await self.infer_async(current_request, request_config, **kwargs)
                result_choice: RolloutResponseChoice = result.choices[0]

                completion = result_choice.message.content
                if messages[-1]['role'] == 'assistant':
                    messages[-1]['content'] += completion
                else:
                    messages.append({'role': 'assistant', 'content': completion})

                if self.multi_turn_scheduler:
                    should_stop = self.multi_turn_scheduler.check_finished(current_request, result_choice, current_turn)
                else:
                    should_stop = True

                if self.max_turns:
                    should_stop = should_stop or (current_turn >= self.max_turns)

                if should_stop:
                    result_choice.messages = messages
                    return result

                current_request = self.multi_turn_scheduler.step(current_request, result_choice, current_turn)
                assert isinstance(current_request, RolloutInferRequest)
                if current_request.messages[-1]['role'] == 'assistant':
                    # NOTE: engine will discard last response during inference
                    # https://github.com/modelscope/ms-swift/blob/v3.5.1/swift/llm/template/base.py#L416-L419
                    # To allow the engine to continue generating content, add a dummy response here.
                    current_request.messages.append({'role': 'assistant', 'content': None})

                current_turn += 1

        tasks = [_infer_async_single(infer_request, request_config, **kwargs) for infer_request in infer_requests]
        if use_tqdm is None:
            use_tqdm = len(infer_requests) > 1
        return await self._batch_infer_stream(tasks, request_config.stream, use_tqdm, metrics)
```

**File:** deepanalyze/SkyRL/skyrl-train/docs/configuration/config.rst (L503-504)
```text
- ``generator.max_turns``: Maximum number of turns for generation with multi-turn RL.
- ``generator.use_conversation_multi_turn``: Whether to use conversation format for multi-turn generation. If set to ``true`` then observations are appended to the chat history as a new turn. If set to ``false`` then observations are appended as-is to the assistant response in token space and generation is continued  (after removing any EOS token in the response).  We've observed some cases where model can be sensitive to chat history format (ex: in SkyRL-SQL), and thus ``false`` can be used for full control over the exact tokens added after environment interaction.
```

# 我问
交互轨迹合成使用什么工具或这框架来记录轨迹，并且告诉我轨迹样本长什么样子

# deepwiki答


交互轨迹合成使用**SkyRL框架(https://github.com/NovaSky-AI/SkyRL)**来记录轨迹 [1](#2-0) 。轨迹记录主要通过以下工具和机制实现:

## 轨迹记录工具

### 1. TrajectoryResult数据结构

轨迹通过`TrajectoryResult`类型记录,包含以下字段 [2](#2-1) :
- `instance_id`: 实例标识符
- `trajectory_id`: 轨迹标识符  
- `messages`: OpenAI格式的消息列表
- `state`: 运行时状态对象
- `results`: 任务完成结果
- `error`: 错误信息(如有)
- `finish`: 是否完成标志
- `finish_reason`: 完成原因
- `reward`: 奖励值(评估后填充)
- `eval_error`: 评估错误(如有)

### 2. 文件系统持久化

轨迹会自动保存到文件系统 [3](#2-2) 。在`OHCodeActAgent`中,每个轨迹的消息历史会在特定步骤(第1步或每5步)保存为JSON文件,路径格式为`/mnt/shared_storage/trace/{run_name}/step{current_step}/{instance_id}/{trajectory_id}/trace_{timestamp}.json` [4](#2-3) 。

### 3. 可视化工具

代码库提供了`vis_trace.py`工具用于可视化轨迹 [5](#2-4) 。该工具使用Gradio构建Web界面,可以加载和展示保存的轨迹JSON文件 [6](#2-5) 。

## 轨迹样本示例

### CodeAct轨迹样本

对于SWEBench任务,`CodeActTrajectory`生成的轨迹样本包含 [7](#2-6) :

```python
{
    'instance_id': 'django__django-12345',
    'trajectory_id': 0,
    'messages': [...],  # OpenAI格式的完整对话历史
    'state': <State对象>,  # 包含事件流和历史
    'results': {...},  # 包含生成的补丁等
    'error': None,
    'finish': True,
    'finish_reason': 'FINISH_TOOL'
}
```

### ReAct轨迹样本

对于通用ReAct任务,轨迹样本更简洁 [8](#2-7) :

```python
{
    'instance_id': 'math_problem_123',
    'trajectory_id': 0,
    'messages': [
        {'role': 'system', 'content': '...'},
        {'role': 'user', 'content': '...'},
        {'role': 'assistant', 'content': '...'},
        {'role': 'tool', 'content': '...'}
    ],
    'results': '最终答案',
    'finish_reason': 'FINISH_TOOL'
}
```

### Messages格式

`messages`字段遵循OpenAI聊天格式,支持多种角色 [9](#2-8) :
- `user`: 用户输入
- `assistant`: 模型响应(包括思考过程)
- `tool_call`: 工具调用请求
- `tool_response`/`tool`: 工具执行结果

对于多模态任务,消息中可包含`<image>`、`<audio>`等标签,并配合额外的`images`、`audios`字段 [10](#2-9) 。

## Notes

轨迹记录机制在不同Agent类型中略有差异:
- `OHCodeActAgent`使用OpenHands的`State`对象记录完整事件流 [11](#2-10) 
- `ReActAgent`直接维护消息列表 [12](#2-11) 

轨迹数据既用于训练(通过`AgentRunner`的后处理转换为训练格式 [13](#2-12) ),也用于评估和调试分析<cite />。

### Citations

**File:** deepanalyze/SkyRL/skyrl-train/docs/skyagent/agent-overview.rst (L1-4)
```text
SkyAgent Overview
====================

SkyAgent is a generic agent layer for training and evaluating agents. It is a flexible frontend for building your own agents. 
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/base.py (L70-81)
```python
@dataclass
class TrajectoryResult(TypedDict):
    instance_id: str
    trajectory_id: str
    messages: List[Dict[str, str]]
    state: Any
    results: Optional[CompleterOutput]
    error: Optional[str]
    finish: bool
    finish_reason: str
    reward: Optional[bool]
    eval_error: Optional[str]
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/base.py (L498-503)
```python
        output = self._post_process_results(val_mode=val_mode)

        # reset after run
        self.trajectories = {}

        return build_generator_output(self.cfg.generator.infer_backend, output).result
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/oh_codeact/codeact_agent.py (L235-250)
```python
        import wandb
        current_step = wandb.run.step if wandb.run else 1
        run_name = wandb.run.name if wandb.run else "no_run"
        logger.info(f"Detected run name: {run_name}")
        if  (current_step == 1) or (current_step % 5 == 0) :
            instance_dir = Path(f"/mnt/shared_storage/trace/{run_name}/step{current_step}") / str(self.instance_id) / str(self.trajectory_id)
            instance_dir.mkdir(exist_ok=True, parents=True)

            # Generate a unique filename using a timestamp with microsecond resolution
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            trace_file = instance_dir / f"trace_{timestamp}.json"

            with open(trace_file, "w") as f:
                result_json = json.dumps(messages, default=lambda x: str(x))
                f.write(result_json)

```

**File:** deepanalyze/SkyRL/skyagent/vis_trace.py (L45-70)
```python
def build_interface(trace_dir: str = "./trace/14b", port: int = 9781):
    trace_root = Path(trace_dir)
    all_json_files = sorted([*trace_root.rglob("*.jsonl"), *trace_root.rglob("*.json")])

    if not all_json_files:
        raise FileNotFoundError(f"No .json or .jsonl files found in {trace_root}")

    file_options = [str(p.relative_to(trace_root)) for p in all_json_files]
    conversations_cache = {}

    with gr.Blocks() as demo:
        gr.Markdown("# 🧠 OpenAI Message Trace Viewer")
        gr.Markdown(
            "Select a trace file and conversation index to visualize the conversation."
        )

        with gr.Row():
            file_dropdown = gr.Dropdown(
                label="Select trace file", choices=file_options, value=file_options[0]
            )
            index_slider = gr.Number(
                label="Conversation index", value=0, precision=0, minimum=0
            )

        chatbot = gr.Chatbot(label="Chat Trace", height=600)
        status_text = gr.Textbox(label="Status", interactive=False)
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/oh_codeact/codeact_runner.py (L212-221)
```python
            return_val = TrajectoryResult({
                'instance_id': instance_id,
                'trajectory_id': trajectory_id,
                'messages': final_messages,
                'state': state,
                'results': result,
                'error': state.last_error if state and state.last_error else None,
                'finish': finish,
                'finish_reason': finish_reason,
            })
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/react/react_runner.py (L39-45)
```python
        self.result = {
            'instance_id': instance_id,
            'trajectory_id': self.cfg.trajectory_id,
            'messages': self.agent.get_messages(),
            'results': result,
            'finish_reason': finish_reason,
        }
```

**File:** deepanalyze/ms-swift/docs/source_en/Instruction/Agent-support.md (L7-10)
```markdown
```jsonl
{"tools": "[{\"type\": \"function\", \"function\": {\"name\": \"realtime_aqi\", \"description\": \"Weather forecast. Get real-time air quality, including current air quality, PM2.5, and PM10 information.\", \"parameters\": {\"type\": \"object\", \"properties\": {\"city\": {\"type\": \"string\", \"description\": \"City name, e.g., Shanghai\"}}, \"required\": [\"city\"]}}}]", "messages": [{"role": "user", "content": "What is the weather like in Beijing and Shanghai today?"}, {"role": "tool_call", "content": "{\"name\": \"realtime_aqi\", \"arguments\": {\"city\": \"Beijing\"}}"}, {"role": "tool_call", "content": "{\"name\": \"realtime_aqi\", \"arguments\": {\"city\": \"Shanghai\"}}"}, {"role": "tool_response", "content": "{\"city\": \"Beijing\", \"aqi\": \"10\", \"unit\": \"celsius\"}"}, {"ro ... (truncated)
{"tools": "[{\"type\": \"function\", \"function\": {\"name\": \"click\", \"description\": \"Click on a position on the screen\", \"parameters\": {\"type\": \"object\", \"properties\": {\"x\": {\"type\": \"integer\", \"description\": \"X-coordinate representing the horizontal position on the screen\"}, \"y\": {\"type\": \"integer\", \"description\": \"Y-coordinate representing the vertical position on the screen\"}}, \"required\": [\"x\", \"y\"]}}}]", "messages": [{"role": "user", "content": "<image>What time is it now?"}, {"role": "assistant", "content": "<think>\nI can check the current time by opening the calendar app.\n</think>\n"}, {"role": "tool_call", "content": "{\"name\": \"click\", \"arguments\": {\"x\": 105, \"y\": 132}}"}, {"role": "tool_response", "content": "{\"images\": \"<im ... (truncated)
```
```

**File:** deepanalyze/ms-swift/docs/source_en/Customization/Custom-dataset.md (L206-210)
```markdown
Here are example data samples for a text-only Agent and a multimodal Agent:
```jsonl
{"tools": "[{\"type\": \"function\", \"function\": {\"name\": \"realtime_aqi\", \"description\": \"Weather forecast. Get real-time air quality, including current air quality, PM2.5, and PM10 information.\", \"parameters\": {\"type\": \"object\", \"properties\": {\"city\": {\"type\": \"string\", \"description\": \"City name, e.g., Shanghai\"}}, \"required\": [\"city\"]}}}]", "messages": [{"role": "user", "content": "What is the weather like in Beijing and Shanghai today?"}, {"role": "tool_call", "content": "{\"name\": \"realtime_aqi\", \"arguments\": {\"city\": \"Beijing\"}}"}, {"role": "tool_call", "content": "{\"name\": \"realtime_aqi\", \"arguments\": {\"city\": \"Shanghai\"}}"}, {"role": "tool_response", "content": "{\"city\": \"Beijing\", \"aqi\": \"10\", \"unit\": \"celsius\"}"}, {"ro ... (truncated)
{"tools": "[{\"type\": \"function\", \"function\": {\"name\": \"click\", \"description\": \"Click on a position on the screen\", \"parameters\": {\"type\": \"object\", \"properties\": {\"x\": {\"type\": \"integer\", \"description\": \"X-coordinate representing the horizontal position on the screen\"}, \"y\": {\"type\": \"integer\", \"description\": \"Y-coordinate representing the vertical position on the screen\"}}, \"required\": [\"x\", \"y\"]}}}]", "messages": [{"role": "user", "content": "<image>What time is it now?"}, {"role": "assistant", "content": "<think>\nI can check the current time by opening the calendar app.\n</think>\n"}, {"role": "tool_call", "content": "{\"name\": \"click\", \"arguments\": {\"x\": 105, \"y\": 132}}"}, {"role": "tool_response", "content": "{\"images\": \"<im ... (truncated)
```
```

**File:** deepanalyze/SkyRL/skyagent/skyagent/agents/react/react_agent.py (L34-34)
```python
        self.messages: List[dict] = []
```
