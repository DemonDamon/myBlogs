# 我问
这个项目是基于 MCP 的 rag框架吗？如何在代码层面体现？涉及到哪些工具、提示词以及mcp资源？

# deepwiki答
是的,UltraRAG v2 是一个基于 MCP (Model Context Protocol) 架构的 RAG 框架 [1](#0-0) 。<cite />

## MCP 架构在代码层面的体现

### 1. Server 封装

核心组件被封装为独立的 MCP Server,每个 Server 继承自 `UltraRAG_MCP_Server` 类 [2](#0-1) :<cite />

- **Custom Server**: 数据转换工具 [3](#0-2) 
- **Prompt Server**: 模板渲染 [4](#0-3) 
- **Router Server**: 条件分支逻辑 [5](#0-4) 
- **Generation Server**: LLM 推理 [6](#0-5) 
- **Retriever Server**: 检索功能 [7](#0-6) 
- **Benchmark Server**: 数据加载 [8](#0-7) 
- **Evaluation Server**: 评估指标 [9](#0-8) 

### 2. Tool 注册机制

通过 `@app.tool` 装饰器注册函数级工具,使用 `output` 参数定义 I/O 映射 [10](#0-9) :<cite />

```python
@app.tool(output="ans_ls->extract_query_list")
def search_r1_query_extract(ans_ls: List[str]) -> Dict[str, List[str]]:
    # 实现逻辑
``` [11](#0-10) 

### 3. Client-Server 通信

Client 通过 stdio 协议与 Server 进程通信 [12](#0-11) :<cite />

- Python Server: `{"command": "python", "args": [path]}` [13](#0-12) 
- 远程 Server: 通过 `npx mcp-remote` 调用 [14](#0-13) 

### 4. Build 系统

每个 Server 自动注册 `build()` 工具 [15](#0-14) ,生成 `server.yaml` 元数据文件 [16](#0-15) :<cite />

```yaml
tools:
  tool_name:
    input: {param1: var1, param2: $config_param}
    output: [output_var]
```

## 涉及的工具

### Prompt 工具

- `qa_boxed`: 基础问答提示 [17](#0-16) 
- `qa_rag_boxed`: RAG 问答提示 [18](#0-17) 
- `webnote_gen_plan`: WebNote 计划生成 [19](#0-18) 
- `webnote_init_page`: 页面初始化 [20](#0-19) 
- `webnote_gen_subq`: 子问题生成 [21](#0-20) 

### Router 工具

- `ircot_check_end`: 检查 IRCoT 是否完成 [22](#0-21) 
- `webnote_check_page`: 检查页面完整性(返回 `incomplete`/`complete` 状态)<cite />

### Custom 工具

- `search_r1_query_extract`: 提取搜索查询 [23](#0-22) 
- `output_extract_from_boxed`: 从 LaTeX `\boxed{}` 格式提取答案<cite />

## 涉及的提示词模板

提示词使用 Jinja2 模板,存储在 `prompt/` 目录:<cite />

- `prompt/webnote_gen_plan.jinja`: 生成结构化大纲<cite />
- `prompt/webnote_init_page.jinja`: 创建带占位符的页面框架<cite />
- `prompt/webnote_gen_subq.jinja`: 为不完整章节生成检索查询<cite />
- `prompt/webnote_fill_page.jinja`: 用检索内容填充章节<cite />
- `prompt/search_o1_reasoning.jinja`: Search-O1 推理指令<cite />

## MCP 资源

### 依赖包

- `mcp==1.12.4`: MCP 协议核心库 [24](#0-23) 
- `fastmcp`: FastMCP 框架(版本在 CLI 中显示) [25](#0-24) 
- `jinja2==3.1.6`: 模板引擎 [26](#0-25) 

### 配置文件

- `parameter.yaml`: 存储配置参数(如模板路径、top_k 等)<cite />
- `server.yaml`: Build 系统生成的工具元数据<cite />
- Pipeline YAML: 定义执行流程(如 `examples/webnote.yaml`)<cite />

## Notes

UltraRAG v2 的核心创新在于将 MCP 的 Client-Server 架构与原生流程控制(串行、循环、条件分支)深度融合 [27](#0-26) 。<cite />开发者只需编写 YAML 文件即可构建复杂的多阶段推理系统,无需编写大量胶水代码 [28](#0-27) 。<cite />每个 Server 的功能通过函数级 Tool 接口暴露,支持热插拔式扩展 [29](#0-28) 。<cite />

Wiki pages you might want to explore:
- [MCP Server Framework (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#2.4)
- [Hierarchical Methods (WebNote) (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#4.6)

### Citations

**File:** README.md (L48-48)
```markdown
为了解决这一痛点，清华大学 [THUNLP](https://nlp.csai.tsinghua.edu.cn/) 实验室、东北大学 [NEUIR](https://neuir.github.io) 实验室、[OpenBMB](https://www.openbmb.cn/home) 与 [AI9stars](https://github.com/AI9Stars) 联合推出 UltraRAG v2 —— 首个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) 架构设计的 RAG 框架。这一设计让科研人员只需编写 YAML 文件，就可以直接声明串行、循环、条件分支等复杂逻辑，从而以极低的代码量快速实现多阶段推理系统。
```

**File:** README.md (L59-60)
```markdown
- 🚀 **低代码构建复杂 Pipeline**  
  - 原生支持 **串行、循环、条件分支** 等推理控制结构。开发者只需编写 YAML 文件，即可实现几十行代码构建的 **迭代式 RAG 流程**。  
```

**File:** README.md (L69-70)
```markdown
  - 每个 Server 的功能以函数级 **Tool** 注册，新增功能仅需添加一个函数即可接入完整流程；  
  - 同时支持调用 **外部 MCP Server**，轻松扩展 Pipeline 能力与应用场景。 
```

**File:** README.md (L98-98)
```markdown
复杂 RAG 推理框架的开发具有显著挑战，而 UltraRAG v2 之所以能够在**低代码**条件下支持复杂系统的构建，核心在于其底层对多结构 **Pipeline 流程控制**的原生支持。无论是串行、循环还是条件分支，所有控制逻辑均可在 YAML 层完成定义与调度，覆盖复杂推理任务所需的多种流程表达方式。在实际运行中，推理流程的调度由内置 **Client** 执行，其逻辑完全由用户编写的外部 **Pipeline YAML 脚本** 脚本描述，从而实现与底层实现的解耦。开发者可以像使用编程语言关键字一样调用 loop、step 等指令，以声明的方式快速构建多阶段推理流程。
```

**File:** src/ultrarag/server.py (L32-32)
```python
class UltraRAG_MCP_Server(FastMCP):
```

**File:** src/ultrarag/server.py (L105-105)
```python
        self.tool(self.build, name="build")
```

**File:** src/ultrarag/server.py (L111-145)
```python
    def tool(
        self,
        name_or_fn: str | AnyFunction | None = None,
        *,
        output: str | None = None,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: set[str] | None = None,
        output_schema: dict[str, Any] | None | NotSetT = NotSet,
        annotations: ToolAnnotations | dict[str, Any] | None = None,
        exclude_args: list[str] | None = None,
        meta: dict[str, Any] | None = None,
        enabled: bool | None = None,
    ):
        if output is not None:
            if annotations is None:
                annotations = {"output": output}
            elif isinstance(annotations, dict):
                annotations = annotations | {"output": output}
            else:
                annotations.output = output

        return super().tool(
            name_or_fn,
            name=name,
            title=title,
            output_schema=output_schema,
            description=description,
            tags=tags,
            annotations=annotations,
            exclude_args=exclude_args,
            meta=meta,
            enabled=enabled,
        )
```

**File:** src/ultrarag/server.py (L308-334)
```python
    def build(self, parameter_file: str):
        cfg_path = Path(parameter_file)
        base_dir = cfg_path.parent
        srv_name = base_dir.name
        self.param_cfg = self.load_config(str(cfg_path)) if cfg_path.exists() else {}
        out_path = base_dir / "server.yaml"
        build_yaml = {
            "path": self.param_cfg.get(
                "path", str(base_dir / "src" / f"{srv_name}.py")
            ),
            "parameter": parameter_file,
            "tools": {
                name: self._build_entry(self.fn_meta[name], self.param_cfg)
                for name in self.fn_meta
            },
            "prompts": {
                name: self._build_entry(self.prompt_meta[name], self.param_cfg)
                for name in self.prompt_meta
            },
        }

        if not Path(build_yaml["path"]).exists():
            raise FileNotFoundError(f"Server code not found: {build_yaml['path']}")

        yaml.safe_dump(
            build_yaml, out_path.open("w"), allow_unicode=True, sort_keys=False
        )
```

**File:** servers/custom/src/custom.py (L6-6)
```python
app = UltraRAG_MCP_Server("custom")
```

**File:** servers/custom/src/custom.py (L9-28)
```python
@app.tool(output="ans_ls->extract_query_list")
def search_r1_query_extract(ans_ls: List[str]) -> Dict[str, List[str]]:

    def get_query(text):
        import re

        pattern = re.compile(r"<search>([^<]*)", re.DOTALL)
        matches = pattern.findall(text)

        if matches:
            query = matches[-1].strip()
            if not query.endswith("?"):
                query += "?"
            return query
        else:
            return "There is no query."

    query = [get_query(answer) for answer in ans_ls]

    return {"extract_query_list": query}
```

**File:** servers/prompt/src/prompt.py (L12-12)
```python
app = UltraRAG_MCP_Server("prompt")
```

**File:** servers/prompt/src/prompt.py (L24-31)
```python
@app.prompt(output="q_ls,template->prompt_ls")
def qa_boxed(q_ls: List[str], template: str | Path) -> List[PromptMessage]:
    template: Template = load_prompt_template(template)
    ret = []
    for q in q_ls:
        p = template.render(question=q)
        ret.append(p)
    return ret
```

**File:** servers/prompt/src/prompt.py (L66-81)
```python
@app.prompt(output="q_ls,choices_ls,ret_psg,template->prompt_ls")
def qa_rag_boxed_multiple_choice(
    q_ls: List[str],
    choices_ls: List[List[str]],
    ret_psg: List[List[str]],
    template: str | Path,
) -> List[PromptMessage]:
    template: Template = load_prompt_template(template)
    ret = []
    CHOICES: List[str] = list(string.ascii_uppercase)  # A, B, ..., Z
    for q, psg, choices in zip(q_ls, ret_psg, choices_ls):
        passage_text = "\n".join(psg)
        choices_text = "\n".join(f"{CHOICES[i]}: {c}" for i, c in enumerate(choices))
        p = template.render(question=q, documents=passage_text, choices=choices_text)
        ret.append(p)
    return ret
```

**File:** servers/prompt/src/prompt.py (L162-173)
```python
@app.prompt(output="q_ls,plan_ls,webnote_init_page_template->prompt_ls")
def webnote_init_page(
    q_ls: List[str],
    plan_ls: List[str],
    template: str | Path,
) -> List[PromptMessage]:
    template: Template = load_prompt_template(template)
    all_prompts = []
    for q, plan in zip(q_ls, plan_ls):
        p = template.render(question=q, plan=plan)
        all_prompts.append(p)
    return all_prompts
```

**File:** servers/prompt/src/prompt.py (L176-186)
```python
@app.prompt(output="q_ls,webnote_gen_plan_template->prompt_ls")
def webnote_gen_plan(
    q_ls: List[str],
    template: str | Path,
) -> List[PromptMessage]:
    template: Template = load_prompt_template(template)
    all_prompts = []
    for q in q_ls:
        p = template.render(question=q)
        all_prompts.append(p)
    return all_prompts
```

**File:** servers/prompt/src/prompt.py (L189-201)
```python
@app.prompt(output="q_ls,plan_ls,page_ls,webnote_gen_subq_template->prompt_ls")
def webnote_gen_subq(
    q_ls: List[str],
    plan_ls: List[str],
    page_ls: List[str],
    template: str | Path,
) -> List[PromptMessage]:
    template: Template = load_prompt_template(template)
    all_prompts = []
    for q, plan, page in zip(q_ls, plan_ls, page_ls):
        p = template.render(question=q, plan=plan, page=page)
        all_prompts.append(p)
    return all_prompts
```

**File:** servers/router/src/router.py (L6-6)
```python
app = UltraRAG_MCP_Server("router")
```

**File:** servers/router/src/router.py (L24-33)
```python
@app.tool(output="ans_ls->ans_ls")
def ircot_check_end(ans_ls: List[str]) -> Dict[str, List[Dict[str, str]]]:
    ans_ls = [
        {
            "data": ans,
            "state": "complete" if "so the answer is" in ans.lower() else "incomplete",
        }
        for ans in ans_ls
    ]
    return {"ans_ls": ans_ls}
```

**File:** servers/generation/src/generation.py (L15-15)
```python
app = UltraRAG_MCP_Server("generation")
```

**File:** servers/retriever/src/retriever.py (L17-17)
```python
app = UltraRAG_MCP_Server("retriever")
```

**File:** servers/benchmark/src/benchmark.py (L11-11)
```python
app = UltraRAG_MCP_Server("benchmark")
```

**File:** servers/evaluation/src/evaluation.py (L15-15)
```python
app = UltraRAG_MCP_Server("evaluation")
```

**File:** src/ultrarag/client.py (L646-690)
```python
    mcp_servers: Dict[str, Any] = {}
    for name, conf in server_cfgs.items():
        path = conf.get("path", "")
        if path.endswith(".py"):
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"[UltraRAG Error] Cannot find the server file of {name}: {path}"
                )
            mcp_servers[name] = {
                "command": "python",
                "args": [path],
                "env": os.environ.copy(),
            }
        elif path.startswith(("http://", "https://")):
            if not node_status:
                try:
                    check_node_version(20)
                    node_status = True
                except NodeNotInstalledError as e:
                    logger.error(
                        "[UltraRAG Error] Node.js is not installed or not found in PATH. Please install Node.js >= 20."
                    )
                    logger.error(str(e))
                    sys.exit(1)
                except NodeVersionTooLowError as e:
                    logger.error(
                        "[UltraRAG Error] Node.js version is too low. Please upgrade to Node.js >= 20."
                    )
                    logger.error(str(e))
                    sys.exit(1)
            mcp_servers[name] = (
                {
                    "command": "npx",
                    "args": [
                        "-y",
                        "mcp-remote",
                        path,
                    ],
                    "env": os.environ.copy(),
                },
            )
        else:
            raise ValueError(
                f"[UltraRAG Error] Unsupported server type for {name}: {path}"
            )
```

**File:** environment.yml (L181-181)
```yaml
  - jinja2==3.1.6
```

**File:** environment.yml (L203-203)
```yaml
  - mcp==1.12.4
```

**File:** src/ultrarag/cli.py (L40-42)
```python
    info_table.add_row(
        "🏎️", "FastMCP version:", Text(get_version_safe("fastmcp"), style="dim white")
    )
```


# 我问
那我想在cursor上创建这个ultrarag的mcp server，具体怎么做呢？给出详细的配置方式

# deepwiki答

您想在 Cursor 中配置 UltraRAG 的 MCP Server。<cite/> 根据代码库,UltraRAG 的 MCP Server 是通过 stdio 协议与客户端通信的 Python 进程。 [1](#1-0)  以下是详细的配置步骤:

## 配置方式

### 1. Cursor MCP 配置文件位置

Cursor 的 MCP 配置文件通常位于:<cite/>
- **macOS/Linux**: `~/.cursor/mcp.json` 或 `~/.config/cursor/mcp.json`
- **Windows**: `%APPDATA%\Cursor\mcp.json`

### 2. 基本配置结构

在 `mcp.json` 中添加 UltraRAG 的 Server 配置:<cite/>

```json
{
  "mcpServers": {
    "ultrarag-custom": {
      "command": "python",
      "args": ["/path/to/UltraRAG/servers/custom/src/custom.py"],
      "env": {}
    },
    "ultrarag-prompt": {
      "command": "python",
      "args": ["/path/to/UltraRAG/servers/prompt/src/prompt.py"],
      "env": {}
    },
    "ultrarag-router": {
      "command": "python",
      "args": ["/path/to/UltraRAG/servers/router/src/router.py"],
      "env": {}
    },
    "ultrarag-generation": {
      "command": "python",
      "args": ["/path/to/UltraRAG/servers/generation/src/generation.py"],
      "env": {}
    },
    "ultrarag-retriever": {
      "command": "python",
      "args": ["/path/to/UltraRAG/servers/retriever/src/retriever.py"],
      "env": {}
    }
  }
}
```

这个配置格式与 UltraRAG 内部使用的格式完全一致。 [2](#1-1) 

### 3. 环境变量配置

如果需要特定的环境变量(如 API keys),可以在 `env` 字段中添加:<cite/>

```json
{
  "mcpServers": {
    "ultrarag-generation": {
      "command": "python",
      "args": ["/path/to/UltraRAG/servers/generation/src/generation.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "log_level": "info"
      }
    }
  }
}
```

### 4. 确保 Python 环境

确保 `python` 命令指向安装了 UltraRAG 依赖的环境:<cite/>

```json
{
  "mcpServers": {
    "ultrarag-custom": {
      "command": "/path/to/conda/envs/ultrarag/bin/python",
      "args": ["/path/to/UltraRAG/servers/custom/src/custom.py"],
      "env": {}
    }
  }
}
```

### 5. 验证配置

每个 Server 都会自动注册一个 `build` 工具。 [3](#1-2)  配置完成后,在 Cursor 中应该能看到以下工具:

**Custom Server 工具**:<cite/>
- `search_r1_query_extract`: 提取搜索查询 [4](#1-3) 
- `output_extract_from_boxed`: 提取 LaTeX 格式答案 [5](#1-4) 

**Prompt Server 工具**:<cite/>
- `qa_boxed`: 基础问答提示 [6](#1-5) 
- `qa_rag_boxed`: RAG 问答提示 [7](#1-6) 

**Router Server 工具**:<cite/>
- `ircot_check_end`: 检查推理完成状态 [8](#1-7) 

## 完整示例配置

```json
{
  "mcpServers": {
    "ultrarag-custom": {
      "command": "/Users/username/miniconda3/envs/ultrarag/bin/python",
      "args": ["/Users/username/projects/UltraRAG/servers/custom/src/custom.py"],
      "env": {
        "log_level": "info"
      }
    },
    "ultrarag-prompt": {
      "command": "/Users/username/miniconda3/envs/ultrarag/bin/python",
      "args": ["/Users/username/projects/UltraRAG/servers/prompt/src/prompt.py"],
      "env": {
        "log_level": "info"
      }
    },
    "ultrarag-router": {
      "command": "/Users/username/miniconda3/envs/ultrarag/bin/python",
      "args": ["/Users/username/projects/UltraRAG/servers/router/src/router.py"],
      "env": {
        "log_level": "info"
      }
    }
  }
}
```

## Notes

UltraRAG 的每个 Server 都是独立的 Python 进程,通过 stdio 协议与 MCP Client 通信。 [9](#1-8)  配置时需要注意:

1. **路径必须是绝对路径**,不支持相对路径或 `~` 符号 <cite/>
2. **Python 环境必须包含所有依赖**,包括 `fastmcp`、`mcp`、`jinja2` 等 <cite/>
3. **每个 Server 独立运行**,可以根据需要选择性配置 <cite/>
4. 如果需要使用 Generation 或 Retriever Server,还需要配置相应的 API keys 或模型路径 <cite/>

配置完成后重启 Cursor,即可在 MCP 工具列表中看到 UltraRAG 的各个工具。<cite/>

Wiki pages you might want to explore:
- [MCP Server Framework (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#2.4)
- [Hierarchical Methods (WebNote) (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#4.6)

### Citations

**File:** src/ultrarag/client.py (L654-658)
```python
            mcp_servers[name] = {
                "command": "python",
                "args": [path],
                "env": os.environ.copy(),
            }
```

**File:** src/ultrarag/client.py (L888-892)
```python
            mcp_cfg["mcpServers"][name] = {
                "command": "python",
                "args": [path],
                "env": os.environ.copy(),
            }
```

**File:** src/ultrarag/server.py (L105-105)
```python
        self.tool(self.build, name="build")
```

**File:** src/ultrarag/server.py (L336-347)
```python
    def run(
        self,
        transport: Transport | None = None,
        show_banner: bool = False,
        **transport_kwargs: Any,
    ) -> None:
        super().run(
            transport=transport,
            show_banner=show_banner,
            **transport_kwargs,
        )

```

**File:** servers/custom/src/custom.py (L9-10)
```python
@app.tool(output="ans_ls->extract_query_list")
def search_r1_query_extract(ans_ls: List[str]) -> Dict[str, List[str]]:
```

**File:** servers/custom/src/custom.py (L65-92)
```python
@app.tool(output="ans_ls->pred_ls")
def output_extract_from_boxed(ans_ls: List[str]) -> Dict[str, List[str]]:
    def extract(ans: str) -> str:
        start = ans.rfind(r"\boxed{")
        if start == -1:
            content = ans.strip()
        else:
            i = start + len(r"\boxed{")
            brace_level = 1
            end = i
            while end < len(ans) and brace_level > 0:
                if ans[end] == "{":
                    brace_level += 1
                elif ans[end] == "}":
                    brace_level -= 1
                end += 1
            content = ans[i : end - 1].strip()
            content = re.sub(r"^\$+|\$+$", "", content).strip()
            content = re.sub(r"^\\\(|\\\)$", "", content).strip()
            if content.startswith(r"\text{") and content.endswith("}"):
                content = content[len(r"\text{") : -1].strip()
            content = content.strip("()").strip()

        content = content.replace("\\", " ")
        content = content.replace("  ", " ")
        return content

    return {"pred_ls": [extract(ans) for ans in ans_ls]}
```

**File:** servers/prompt/src/prompt.py (L24-25)
```python
@app.prompt(output="q_ls,template->prompt_ls")
def qa_boxed(q_ls: List[str], template: str | Path) -> List[PromptMessage]:
```

**File:** servers/prompt/src/prompt.py (L51-62)
```python
# prompt for QA RAG boxed
@app.prompt(output="q_ls,ret_psg,template->prompt_ls")
def qa_rag_boxed(
    q_ls: List[str], ret_psg: List[str | Any], template: str | Path
) -> list[PromptMessage]:
    template: Template = load_prompt_template(template)
    ret = []
    for q, psg in zip(q_ls, ret_psg):
        passage_text = "\n".join(psg)
        p = template.render(question=q, documents=passage_text)
        ret.append(p)
    return ret
```

**File:** servers/router/src/router.py (L24-25)
```python
@app.tool(output="ans_ls->ans_ls")
def ircot_check_end(ans_ls: List[str]) -> Dict[str, List[Dict[str, str]]]:
```


# 我问
ultrarag是如何实现 用 YAML 文件 来构建复杂rag？请罗列出核心的模块有哪些？可复用或可独立部署的组件有哪些？以及所支持的核心功能点有哪些？

# deepwiki答
UltraRAG 通过 **YAML 配置文件** + **MCP Client-Server 架构** 实现复杂 RAG 系统的低代码构建。 [1](#2-0) 核心思路是将流程控制逻辑(串行、循环、分支)声明在 YAML 中,由 Client 解析执行,调用独立的 MCP Server 完成具体任务。 [2](#2-1) 

## YAML 构建复杂 RAG 的实现机制

### 1. 配置文件体系

UltraRAG 使用三类 YAML 文件协同工作:<cite />

- **Pipeline YAML** (`examples/*.yaml`): 定义工作流步骤、循环、分支逻辑 [3](#2-2) 
- **Server YAML** (`servers/*/server.yaml`): 工具的输入输出映射(由 `build` 命令自动生成) [4](#2-3) 
- **Parameter YAML** (`parameter.yaml`): 运行时配置参数(模型路径、API keys 等) [5](#2-4) 

### 2. 流程控制结构

Pipeline YAML 支持三种原生控制结构:<cite />

**串行执行**:
```yaml
pipeline:
  - server.tool1
  - server.tool2
``` [6](#2-5) 

**循环执行**:
```yaml
loop:
  times: 3
  steps:
    - server.tool
``` [7](#2-6) 

**条件分支**:
```yaml
branch:
  router:
    - router.check_state
  branches:
    state1: [server.tool1]
    state2: [server.tool2]
``` [8](#2-7) 

### 3. 执行流程

**Build 阶段**: `ultrarag build pipeline.yaml` 收集所有 Server 的工具元数据,生成 `server.yaml` 和聚合的 `parameter.yaml`。 [9](#2-8) 每个 Server 的 `build()` 工具会提取函数签名和参数配置。 [10](#2-9) 

**Run 阶段**: `ultrarag run pipeline.yaml` 按 YAML 定义的顺序执行步骤。 [11](#2-10) `UltraData` 类管理全局变量和状态,支持 `$variable` 语法引用参数。 [12](#2-11) 

## 核心模块

### 1. 编排层 (Orchestration Layer)

- **`Client` (fastmcp)**: MCP 客户端,管理与 Server 的连接和工具调用 [13](#2-12) 
- **`Configuration`**: 加载和解析 YAML 配置文件 [14](#2-13) 
- **`UltraData`**: 状态管理器,跟踪变量、分支状态和执行历史 [15](#2-14) 

### 2. Server 层 (MCP Server Layer)

所有 Server 继承自 `UltraRAG_MCP_Server` 基类:<cite />

**核心 RAG 组件**:
- **Retriever Server** (`servers/retriever`): 检索功能,支持 dense/sparse/web 搜索 [16](#2-15) 
- **Generation Server** (`servers/generation`): LLM 推理,支持 vLLM/OpenAI/HuggingFace [17](#2-16) 
- **Prompt Server** (`servers/prompt`): Jinja2 模板渲染<cite />
- **Evaluation Server** (`servers/evaluation`): 评估指标计算<cite />

**辅助组件**:
- **Router Server** (`servers/router`): 条件分支逻辑<cite />
- **Custom Server** (`servers/custom`): 数据处理工具<cite />
- **Benchmark Server** (`servers/benchmark`): 数据集加载<cite />
- **Corpus Server** (`servers/corpus`): 语料库构建与分块<cite />

### 3. 工具注册机制

Server 通过 `@app.tool` 装饰器注册函数级工具,`output` 参数定义输出变量映射: [18](#2-17) 

```python
@app.tool(output="results->retrieved_docs")
def retriever_search(query_list, top_k):
    # 实现逻辑
```

## 可复用/可独立部署的组件

### 1. 独立 MCP Server

每个 Server 都是独立的 Python 进程,可单独部署:<cite />

- **本地部署**: 通过 stdio 协议启动 [19](#2-18) 
- **远程部署**: 通过 HTTP 协议访问 [20](#2-19) 
- **Node.js 集成**: 通过 `npx mcp-remote` 调用 [21](#2-20) 

### 2. 可复用的检索后端

Retriever Server 支持多种可切换的后端:<cite />
- **Embedding**: infinity / sentence_transformers / openai [16](#2-15) 
- **Index**: FAISS / Milvus [22](#2-21) 
- **Sparse**: BM25 [23](#2-22) 

### 3. 可复用的生成后端

Generation Server 支持多种推理引擎:<cite />
- **vLLM**: 高性能推理 [24](#2-23) 
- **OpenAI API**: 兼容 OpenAI 格式的服务 [25](#2-24) 
- **HuggingFace**: 原生 Transformers [26](#2-25) 

## 核心功能点

### 1. 多阶段推理

- **迭代检索**: 支持循环调用检索和生成(如 IRCoT、IterRetGen)<cite />
- **条件分支**: 根据 Router 状态执行不同分支(如 WebNote 的完整性检查)<cite />
- **状态追踪**: `UltraData` 记录每步执行后的状态快照 [27](#2-26) 

### 2. 多模态支持

- **多模态检索**: 支持文本、图片、表格的联合检索 [28](#2-27) 
- **多模态生成**: 支持视觉语言模型(如 MiniCPM4)<cite />
- **多模态评估**: 支持 VQA 任务评估<cite />

### 3. 知识库构建

- **多格式解析**: PDF/Markdown/HTML/TXT<cite />
- **结构化抽取**: 集成 MinerU 进行表格、图片提取<cite />
- **自动分块**: 支持多种 chunking 策略<cite />

### 4. 统一评估

- **17+ Benchmark**: NQ、HotpotQA、ASQA、MP-DocVQA 等<cite />
- **标准化指标**: EM、F1、ROUGE、BERTScore<cite />
- **可视化调试**: 输出执行历史到 JSON [29](#2-28) 

### 5. 外部集成

- **Web 搜索**: Tavily、Exa API<cite />
- **外部 MCP Server**: 支持调用任意符合 MCP 协议的 Server<cite />

## Notes

UltraRAG 的核心创新在于将 **声明式 YAML** 与 **MCP 架构** 结合,实现了"配置即代码"的 RAG 开发范式。<cite />开发者无需编写 Python 胶水代码,只需在 YAML 中声明流程逻辑,即可构建包含循环、分支的复杂推理系统。<cite />所有 Server 都是独立进程,支持热插拔和分布式部署,极大降低了 RAG 系统的开发和维护成本。<cite />

Wiki pages you might want to explore:
- [System Architecture (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#1.1)

### Citations

**File:** README.md (L48-48)
```markdown
为了解决这一痛点，清华大学 [THUNLP](https://nlp.csai.tsinghua.edu.cn/) 实验室、东北大学 [NEUIR](https://neuir.github.io) 实验室、[OpenBMB](https://www.openbmb.cn/home) 与 [AI9stars](https://github.com/AI9Stars) 联合推出 UltraRAG v2 —— 首个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) 架构设计的 RAG 框架。这一设计让科研人员只需编写 YAML 文件，就可以直接声明串行、循环、条件分支等复杂逻辑，从而以极低的代码量快速实现多阶段推理系统。
```

**File:** README.md (L98-98)
```markdown
复杂 RAG 推理框架的开发具有显著挑战，而 UltraRAG v2 之所以能够在**低代码**条件下支持复杂系统的构建，核心在于其底层对多结构 **Pipeline 流程控制**的原生支持。无论是串行、循环还是条件分支，所有控制逻辑均可在 YAML 层完成定义与调度，覆盖复杂推理任务所需的多种流程表达方式。在实际运行中，推理流程的调度由内置 **Client** 执行，其逻辑完全由用户编写的外部 **Pipeline YAML 脚本** 脚本描述，从而实现与底层实现的解耦。开发者可以像使用编程语言关键字一样调用 loop、step 等指令，以声明的方式快速构建多阶段推理流程。
```

**File:** src/ultrarag/client.py (L55-66)
```python
class Configuration:
    def __init__(self) -> None:
        self.load_env()

    @staticmethod
    def load_env() -> None:
        load_dotenv()

    @staticmethod
    def load_config(file_path: str):
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
```

**File:** src/ultrarag/client.py (L100-138)
```python
class UltraData:
    def __init__(
        self,
        pipeline_yaml_path: str,
        server_configs: Dict[str, Dict] = None,
        parameter_file: str | Path | None = None,
    ):
        self.pipeline_yaml_path = pipeline_yaml_path
        cfg = Configuration()
        pipeline = cfg.load_config(pipeline_yaml_path)
        servers = pipeline.get("servers", {})
        server_paths = servers

        if server_configs:
            self.servers = server_configs
        else:
            self.servers = {
                name: cfg.load_config(os.path.join(path, "server.yaml"))
                for name, path in server_paths.items()
            }

        self.local_vals = {
            name: cfg.load_parameter_config(os.path.join(path, "parameter.yaml"))
            for name, path in server_paths.items()
        }
        cfg_path = Path(pipeline_yaml_path)
        if parameter_file is not None:
            param_file = Path(parameter_file)
        else:
            param_file = (
                cfg_path.parent / "parameter" / f"{cfg_path.stem}_parameter.yaml"
            )
        all_local_vals = cfg.load_parameter_config(param_file)
        self.local_vals.update(all_local_vals)
        self.io = {}
        self.global_vars = {}
        self._extract_io(pipeline.get("pipeline", []))
        # store history of memory states after each step
        self.snapshots: List[Dict[str, Any]] = []
```

**File:** src/ultrarag/client.py (L591-607)
```python
    def write_memory_output(self, pipeline_name: str, timestamp: str):
        benchmark_cfg = self.local_vals.get("benchmark", {})
        if isinstance(benchmark_cfg, dict):
            if "benchmark" in benchmark_cfg and "name" in benchmark_cfg["benchmark"]:
                benchmark_name = benchmark_cfg["benchmark"]["name"]
            else:
                benchmark_name = ""

        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = (
            output_dir / f"memory_{benchmark_name}_{pipeline_name}_{timestamp}.json"
        )

        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(self.snapshots, fp, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Memory output saved to {file_path}")
```

**File:** src/ultrarag/client.py (L614-621)
```python
async def build(config_path: str):
    logger.info(f"Building configuration {config_path}")
    cfg_path = Path(config_path)
    pipline_name = cfg_path.stem
    loader = Configuration()
    init_cfg = loader.load_config(config_path)
    servers = init_cfg.get("servers", {})
    server_paths = servers
```

**File:** src/ultrarag/client.py (L654-658)
```python
            mcp_servers[name] = {
                "command": "python",
                "args": [path],
                "env": os.environ.copy(),
            }
```

**File:** src/ultrarag/client.py (L659-686)
```python
        elif path.startswith(("http://", "https://")):
            if not node_status:
                try:
                    check_node_version(20)
                    node_status = True
                except NodeNotInstalledError as e:
                    logger.error(
                        "[UltraRAG Error] Node.js is not installed or not found in PATH. Please install Node.js >= 20."
                    )
                    logger.error(str(e))
                    sys.exit(1)
                except NodeVersionTooLowError as e:
                    logger.error(
                        "[UltraRAG Error] Node.js version is too low. Please upgrade to Node.js >= 20."
                    )
                    logger.error(str(e))
                    sys.exit(1)
            mcp_servers[name] = (
                {
                    "command": "npx",
                    "args": [
                        "-y",
                        "mcp-remote",
                        path,
                    ],
                    "env": os.environ.copy(),
                },
            )
```

**File:** src/ultrarag/client.py (L695-695)
```python
    client = Client(mcp_cfg)
```

**File:** src/ultrarag/client.py (L842-849)
```python
async def run(config_path: str, param_path: str | Path | None = None):
    cfg_path = Path(config_path)
    log_server_banner(cfg_path.stem)
    logger.info(f"Executing pipeline with configuration {config_path}")
    cfg = Configuration()
    init_cfg = cfg.load_config(config_path)
    servers = init_cfg.get("servers", {})
    pipeline_cfg: List[PipelineStep] = init_cfg.get("pipeline", [])
```

**File:** src/ultrarag/client.py (L866-891)
```python
        if provided_path.is_absolute():
            candidate_paths.append(provided_path)
        else:
            candidate_paths.append(Path.cwd() / provided_path)
            candidate_paths.append(root_path / provided_path)

        param_config_path = next((p for p in candidate_paths if p.exists()), None)
        if param_config_path is None:
            raise FileNotFoundError(
                f"[UltraRAG Error] Parameter file '{provided_path}' does not exist"
            )
        param_config_path = param_config_path.resolve()
    else:
        param_config_path = root_path / "parameter" / f"{cfg_name}_parameter.yaml"
    param_cfg = cfg.load_parameter_config(param_config_path)
    for srv_name in server_cfg.keys():
        server_cfg[srv_name]["parameter"] = param_cfg.get(srv_name, {})

    mcp_cfg = {"mcpServers": {}}
    for name, sc in server_cfg.items():
        path = sc.get("path", "")
        if path.endswith(".py"):
            mcp_cfg["mcpServers"][name] = {
                "command": "python",
                "args": [path],
                "env": os.environ.copy(),
```

**File:** src/ultrarag/client.py (L893-989)
```python
        elif path.startswith(("http://", "https://")):
            if not node_status:
                try:
                    check_node_version(20)
                    node_status = True
                except NodeNotInstalledError as e:
                    logger.error(
                        "[UltraRAG Error] Node.js is not installed or not found in PATH. Please install Node.js >= 20."
                    )
                    logger.error(str(e))
                    sys.exit(1)
                except NodeVersionTooLowError as e:
                    logger.error(
                        "[UltraRAG Error] Node.js version is too low. Please upgrade to Node.js >= 20."
                    )
                    logger.error(str(e))
                    sys.exit(1)
            mcp_cfg["mcpServers"][name] = (
                {
                    "command": "npx",
                    "args": [
                        "-y",
                        "mcp-remote",
                        path,
                    ],
                    "env": os.environ.copy(),
                },
            )
        else:
            raise ValueError(f"Unsupported server type for {name}: {path}")

    logger.info("Initializing servers...")
    client = Client(mcp_cfg)
    Data: UltraData = UltraData(
        config_path, server_configs=server_cfg, parameter_file=param_config_path
    )

    async def execute_steps(
        steps: List[PipelineStep],
        depth: int = 0,
        state: str = ROOT,
    ):
        indent = "  " * depth
        result = None
        for step in steps:
            logger.info(f"{indent}Executing step: {step}")
            if isinstance(step, dict) and "loop" in step:
                LoopTerminal.append(True)
                loop_cfg = step["loop"]
                times = loop_cfg.get("times")
                inner_steps = loop_cfg.get("steps", [])
                if times is None or not isinstance(inner_steps, list):
                    raise ValueError(f"Invalid loop config: {loop_cfg}")
                for st in range(times):
                    LoopTerminal[-1] = True
                    await execute_steps(inner_steps, depth + 1, state)
                    logger.debug(
                        f"{indent}Loop iteration {st + 1}/{times} completed {LoopTerminal}"
                    )
                    if LoopTerminal[-1]:
                        LoopTerminal.pop()
                        logger.debug(
                            f"{indent}Loop terminal in iteration {st + 1}/{times}"
                        )
                        break
            elif isinstance(step, dict) and any(k.startswith("branch") for k in step):
                branch_step = step["branch"]
                router = branch_step.get("router", None)
                if not router:
                    raise ValueError(
                        f"Router not found in branch config: {branch_step}"
                    )
                await execute_steps(
                    router[:-1],
                    depth,
                    state,
                )
                if isinstance(router[-1], str):
                    server_name, tool_name = router[-1].split(".")
                    concated, args_input, _ = Data.get_data(
                        server_name, tool_name, state
                    )
                    result = await client.call_tool(concated, args_input)
                    output_text = Data.save_data(
                        server_name, tool_name, result, f"{state}{SEP}router"
                    )
                else:
                    server_name, tool_name = list(router[-1].keys())[0].split(".")
                    tool_value = router[-1][list(router[-1].keys())[0]]
                    concated, args_input, _ = Data.get_data(
                        server_name, tool_name, state, tool_value.get("input", {})
                    )
                    result = await client.call_tool(concated, args_input)
                    output_text = Data.save_data(
                        server_name,
                        tool_name,
                        result,
```

**File:** src/ultrarag/client.py (L991-1104)
```python
                        tool_value.get("output", {}),
                    )

                logger.debug(f"{indent}Result: {output_text}")

                branch_depth = parse_path(state)[-1][0] + 1 if parse_path(state) else 1
                branches = Data.get_branch()
                for branch_name in branches:
                    # for branch_name, branch_steps in branch_step["branches"].items():

                    logger.debug(f"{indent}Processing branch: {branch_name}")
                    # branch_steps = branch_step["branches"][branch_name]``
                    await execute_steps(
                        branch_step["branches"][branch_name],
                        depth,
                        f"{state}{SEP}branch{branch_depth}_{branch_name}",
                    )
            elif isinstance(step, dict) and "." in list(step.keys())[0]:
                server_name, tool_name = list(step.keys())[0].split(".")
                tool_value = step[list(step.keys())[0]]
                concated, args_input, signal = Data.get_data(
                    server_name, tool_name, state, tool_value.get("input", {})
                )
                if depth > 0:
                    LoopTerminal[depth - 1] &= signal
                if not signal:
                    if server_name == "prompt":
                        result = await client.get_prompt(concated, args_input)
                    else:
                        result = await client.call_tool(concated, args_input)
                    output_text = Data.save_data(
                        server_name,
                        tool_name,
                        result,
                        state,
                        tool_value.get("output", {}),
                    )
                    logger.debug(f"{indent}Result: {output_text}")

                    logger.debug(f"{indent}Updated var pool")
            elif isinstance(step, str):
                server_name, tool_name = step.split(".")

                concated, args_input, signal = Data.get_data(
                    server_name, tool_name, state
                )
                if depth > 0:
                    LoopTerminal[depth - 1] = signal
                if not signal:
                    if server_name == "prompt":
                        result = await client.get_prompt(concated, args_input)
                    else:
                        result = await client.call_tool(concated, args_input)
                    output_text = Data.save_data(server_name, tool_name, result, state)
                    logger.debug(f"{indent}Result: {output_text}")
                    logger.debug(f"{indent}Updated var pool")
            else:
                raise ValueError(f"Unrecognized pipeline step: {step}")

        return result

    async with client:
        tools = await client.list_tools()
        tool_name_lst = [
            tool.name
            for tool in tools
            if not tool.name.endswith("_build" if "_" in tool.name else "build")
        ]
        logger.info(f"Available tools: {tool_name_lst}")

        cleanup_tools = [
            tool.name for tool in tools if tool.name.endswith("vllm_shutdown")
        ]

        result = None
        try:
            result = await execute_steps(pipeline_cfg)
            logger.info("Pipeline execution completed.")
        finally:
            for tool_name in cleanup_tools:
                try:
                    logger.info(f"Invoking cleanup tool: {tool_name}")
                    await client.call_tool(tool_name, {})
                except Exception as exc:
                    logger.warning(
                        f"Cleanup tool {tool_name} raised {exc.__class__.__name__}: {exc}"
                    )

        # save memory snapshots
        Data.write_memory_output(cfg_name, datetime.now().strftime("%Y%m%d_%H%M%S"))
        if result is None:
            return None
        return result.data


logging.getLogger("mcp").setLevel(logging.WARNING)


def main():
    parser = argparse.ArgumentParser(prog="ultrarag", description="UltraRAG CLI")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    p_val = subparsers.add_parser("build", help="Build the configuration")
    p_val.add_argument("config")

    p_run = subparsers.add_parser(
        "run", help="Run the pipeline with the given configuration"
    )
    p_run.add_argument("config")
    p_run.add_argument(
        "--param",
        type=str,
        help="Custom parameter file path",
    )
```

**File:** src/ultrarag/server.py (L111-145)
```python
    def tool(
        self,
        name_or_fn: str | AnyFunction | None = None,
        *,
        output: str | None = None,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: set[str] | None = None,
        output_schema: dict[str, Any] | None | NotSetT = NotSet,
        annotations: ToolAnnotations | dict[str, Any] | None = None,
        exclude_args: list[str] | None = None,
        meta: dict[str, Any] | None = None,
        enabled: bool | None = None,
    ):
        if output is not None:
            if annotations is None:
                annotations = {"output": output}
            elif isinstance(annotations, dict):
                annotations = annotations | {"output": output}
            else:
                annotations.output = output

        return super().tool(
            name_or_fn,
            name=name,
            title=title,
            output_schema=output_schema,
            description=description,
            tags=tags,
            annotations=annotations,
            exclude_args=exclude_args,
            meta=meta,
            enabled=enabled,
        )
```

**File:** src/ultrarag/server.py (L308-327)
```python
    def build(self, parameter_file: str):
        cfg_path = Path(parameter_file)
        base_dir = cfg_path.parent
        srv_name = base_dir.name
        self.param_cfg = self.load_config(str(cfg_path)) if cfg_path.exists() else {}
        out_path = base_dir / "server.yaml"
        build_yaml = {
            "path": self.param_cfg.get(
                "path", str(base_dir / "src" / f"{srv_name}.py")
            ),
            "parameter": parameter_file,
            "tools": {
                name: self._build_entry(self.fn_meta[name], self.param_cfg)
                for name in self.fn_meta
            },
            "prompts": {
                name: self._build_entry(self.prompt_meta[name], self.param_cfg)
                for name in self.prompt_meta
            },
        }
```

**File:** servers/retriever/parameter.yaml (L7-31)
```yaml
backend: sentence_transformers # options: infinity, sentence_transformers, openai, bm25
backend_configs:
  infinity:
    bettertransformer: false
    pooling_method: auto
    device: cuda
    model_warmup: false
    trust_remote_code: true
  sentence_transformers:
    device: cuda
    trust_remote_code: true
    sentence_transformers_encode:
      normalize_embeddings: false
      encode_chunk_size: 10000
      q_prompt_name: query
      psg_prompt_name: document
      psg_task: null
      q_task: null
  openai:
    model_name: text-embedding-3-small
    base_url: "https://api.openai.com/v1"
    api_key: ""
  bm25:
    lang: en
    save_path: index/bm25
```

**File:** servers/retriever/parameter.yaml (L33-52)
```yaml
index_backend: faiss # options: faiss, milvus
index_backend_configs:
  faiss:
    index_use_gpu: True
    index_chunk_size: 50000
    index_path: index/index.index
  milvus:
    uri: index/milvus_demo.db # Milvus Lite local file (or http://localhost:19530 for server)
    token: null
    collection_name: ultrarag_embeddings
    id_field_name: id
    vector_field_name: vector
    metric_type: IP
    index_params:
      index_type: AUTOINDEX
      metric_type: IP
    search_params:
      metric_type: IP
      params: {}
    index_chunk_size: 50000
```

**File:** servers/retriever/parameter.yaml (L58-58)
```yaml
is_multimodal: false
```

**File:** servers/generation/parameter.yaml (L3-22)
```yaml
backend: vllm # options: vllm, openai
backend_configs:
  vllm:
    model_name_or_path: openbmb/MiniCPM4-8B
    gpu_ids: "2,3"
    gpu_memory_utilization: 0.9
    dtype: auto
    trust_remote_code: true
  openai:
    model_name: MiniCPM4-8B
    base_url: http://localhost:8000/v1
    api_key: ""
    concurrency: 8
    retries: 3
    base_delay: 1.0
  hf:
    model_name_or_path: openbmb/MiniCPM4-8B
    gpu_ids: '2,3'
    trust_remote_code: true
    batch_size: 8
```

# 我问
看到论文这么说：UltraRAG implements
two alignment strategies: supervised fine-tuning
(SFT) and direct preference optimization (DPO)

代码层面怎么实现的？

# deepwiki答
我需要澄清一下:您提到的论文中关于 UltraRAG 实现 SFT(supervised fine-tuning)和 DPO(direct preference optimization)这两种对齐策略,在当前提供的代码库上下文中**并未找到相关实现**<cite/>。

根据我看到的代码,UltraRAG v2 是一个基于 MCP(Model Context Protocol)架构的 RAG 框架,主要专注于: [1](#0-0) 

- 通过 YAML 配置文件实现低代码的 RAG pipeline 构建
- 将检索、生成、评估等功能封装为独立的 MCP Server
- 支持串行、循环、条件分支等流程控制

核心架构包括: [2](#0-1) 
- `Configuration` 类:负责加载 YAML 配置
- `Client` 类:协调 MCP servers 的调用
- `UltraData` 类:管理 pipeline 执行状态

## Notes

您提到的 SFT 和 DPO 对齐策略可能来自 UltraRAG 的相关论文,但这些训练/对齐功能**不在当前 v2 框架的代码实现范围内**<cite/>。当前代码库主要是一个 RAG 系统的编排框架,而非模型训练框架<cite/>。

如果您需要了解 SFT/DPO 的具体实现,可能需要:
1. 查看 UltraRAG 论文中是否有单独的训练代码仓库链接
2. 或者这些功能可能在 v1 版本中(README 提到可以查看 [v1 分支](https://github.com/OpenBMB/UltraRAG/tree/v1)) [3](#0-2) 

Wiki pages you might want to explore:
- [System Architecture (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#1.1)

### Citations

**File:** README.md (L38-38)
```markdown
- [2025.01.23] 发布 UltraRAG！让大模型读懂善用知识库！我们保留了UltraRAG 1.0的代码，可以点击 [v1](https://github.com/OpenBMB/UltraRAG/tree/v1) 查看。
```

**File:** README.md (L44-55)
```markdown
## UltraRAG v2：面向科研的“RAG实验”加速器 

检索增强生成系统（RAG）正从早期“检索+生成”的简单拼接，走向融合 **自适应知识组织**、**多轮推理**、**动态检索** 的复杂知识系统。但这种复杂度的提升，使科研人员在 **方法复现**、**快速迭代新想法** 时，面临着高昂的工程实现成本。

为了解决这一痛点，清华大学 [THUNLP](https://nlp.csai.tsinghua.edu.cn/) 实验室、东北大学 [NEUIR](https://neuir.github.io) 实验室、[OpenBMB](https://www.openbmb.cn/home) 与 [AI9stars](https://github.com/AI9Stars) 联合推出 UltraRAG v2 —— 首个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) 架构设计的 RAG 框架。这一设计让科研人员只需编写 YAML 文件，就可以直接声明串行、循环、条件分支等复杂逻辑，从而以极低的代码量快速实现多阶段推理系统。

其核心思路是：
- 组件化封装：将RAG 的核心组件封装为**标准化的独立 MCP Server**；
- 灵活调用与扩展：提供 **函数级 Tool** 接口，支持功能的灵活调用与扩展；
- 轻量流程编排：借助 **MCP Client**，建立自上而下的简洁化链路搭建；

与传统框架相比，UltraRAG v2 显著降低了复杂 RAG 系统的 **技术门槛与学习成本**，让研究者能够将更多精力投入到 **实验设计与算法创新** 上，而不是陷入冗长的工程实现。
```

**File:** src/ultrarag/client.py (L55-76)
```python
class Configuration:
    def __init__(self) -> None:
        self.load_env()

    @staticmethod
    def load_env() -> None:
        load_dotenv()

    @staticmethod
    def load_config(file_path: str):
        with open(file_path, "r") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_parameter_config(
        file_path: Union[str, Path | str],
    ) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.is_file():
            return {}
        return yaml.safe_load(path.read_text())

```

# 我问
论文里说「支持嵌入模型和生成模型的微调」具体用了什么第三方微调库吗？支持哪些模型微调？数据怎么自动化构建的？具体地，sft和dpo数据的生成流程是如何（给出mermaid图）？评估的流程又是怎么样的？

# deepwiki答
根据代码库上下文,我需要澄清:**UltraRAG v2 框架本身并不直接支持模型微调功能**<cite/>。

## 当前支持的功能

UltraRAG v2 是一个基于 MCP 架构的 RAG 框架,主要专注于以下能力 [1](#0-0) :

1. **检索(Retrieval)**: 支持多种嵌入模型后端用于检索 [2](#0-1) 
2. **生成(Generation)**: 支持多种 LLM 推理后端 [3](#0-2) 
3. **评估(Evaluation)**: 内置标准化评测流程 [4](#0-3) 

### 支持的模型后端

**检索模型后端**:
- `sentence_transformers`: 本地推理
- `infinity`: 高性能嵌入服务器
- `openai`: OpenAI 兼容 API
- `bm25`: 稀疏检索<cite/>

**生成模型后端**:
- `vllm`: 高吞吐量推理
- `openai`: OpenAI 兼容 API  
- `hf`: HuggingFace Transformers [5](#0-4) 

## 数据构建流程

UltraRAG 支持自动化语料库构建,但**不涉及 SFT/DPO 训练数据生成**<cite/>:

```mermaid
graph TB
    A[原始文档<br/>PDF/MD/HTML/TXT] --> B[Corpus Server]
    B --> C{解析方式}
    C -->|标准解析| D[文本提取]
    C -->|MinerU| E[结构化提取<br/>文本/表格/图片]
    D --> F[分块处理<br/>token/sentence/recursive]
    E --> F
    F --> G[JSONL 语料库]
    G --> H[Retriever Server]
    H --> I[嵌入生成]
    I --> J[向量索引<br/>FAISS/Milvus]
``` [6](#0-5) 

## 评估流程

```mermaid
graph LR
    A[Benchmark Server] -->|加载数据| B[q_ls, gt_ls]
    B --> C[Prompt Server]
    C -->|生成提示| D[prompt_ls]
    D --> E[Generation Server]
    E -->|生成答案| F[ans_ls]
    F --> G[Custom Server]
    G -->|提取答案| H[pred_ls]
    H --> I[Evaluation Server]
    B --> I
    I -->|计算指标| J[F1/EM/ROUGE<br/>MAP/MRR/NDCG]
``` [4](#0-3) 

评估支持的指标包括:
- **QA 指标**: Accuracy, F1, EM, ROUGE-L [7](#0-6) 
- **IR 指标**: MAP, MRR, NDCG@K, Recall@K [8](#0-7) 

## Notes

从代码库来看,UltraRAG v2 是一个 RAG **推理和评估框架**,而非模型训练框架<cite/>。如果论文中提到微调支持,可能指的是:
1. 框架可以使用已微调的模型进行推理
2. 或者这是未来计划的功能,但当前代码库中未实现

框架依赖的第三方库(如 `peft==0.17.1` [9](#0-8) )可能用于加载 LoRA 等微调后的模型,但没有训练相关的代码<cite/>。

Wiki pages you might want to explore:
- [MCP Server Reference (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#3)

### Citations

**File:** README.md (L44-56)
```markdown
## UltraRAG v2：面向科研的“RAG实验”加速器 

检索增强生成系统（RAG）正从早期“检索+生成”的简单拼接，走向融合 **自适应知识组织**、**多轮推理**、**动态检索** 的复杂知识系统。但这种复杂度的提升，使科研人员在 **方法复现**、**快速迭代新想法** 时，面临着高昂的工程实现成本。

为了解决这一痛点，清华大学 [THUNLP](https://nlp.csai.tsinghua.edu.cn/) 实验室、东北大学 [NEUIR](https://neuir.github.io) 实验室、[OpenBMB](https://www.openbmb.cn/home) 与 [AI9stars](https://github.com/AI9Stars) 联合推出 UltraRAG v2 —— 首个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) 架构设计的 RAG 框架。这一设计让科研人员只需编写 YAML 文件，就可以直接声明串行、循环、条件分支等复杂逻辑，从而以极低的代码量快速实现多阶段推理系统。

其核心思路是：
- 组件化封装：将RAG 的核心组件封装为**标准化的独立 MCP Server**；
- 灵活调用与扩展：提供 **函数级 Tool** 接口，支持功能的灵活调用与扩展；
- 轻量流程编排：借助 **MCP Client**，建立自上而下的简洁化链路搭建；

与传统框架相比，UltraRAG v2 显著降低了复杂 RAG 系统的 **技术门槛与学习成本**，让研究者能够将更多精力投入到 **实验设计与算法创新** 上，而不是陷入冗长的工程实现。

```

**File:** README.md (L72-75)
```markdown
- 📚 **知识接入与语料构建自动化**
	- 支持 PDF、Markdown、HTML、TXT 等多格式文档解析与分块建库；
	- 与 MinerU 无缝集成，自动完成结构化抽取、多模态切块（文本/表格/图片）；
	- 一键构建个人化与企业级知识库，适用于科研、企业文档、私有知识管理等场景。
```

**File:** servers/retriever/src/retriever.py (L66-93)
```python
    def retriever_init(
        self,
        model_name_or_path: str,
        backend_configs: Dict[str, Any],
        batch_size: int,
        corpus_path: str,
        gpu_ids: Optional[object] = None,
        is_multimodal: bool = False,
        backend: str = "sentence_transformers",
        index_backend: str = "faiss",
        index_backend_configs: Optional[Dict[str, Any]] = None,
    ):

        self.backend = backend.lower()
        self.index_backend_name = index_backend.lower()
        self.index_backend_configs = index_backend_configs or {}
        self.index_backend: Optional[BaseIndexBackend] = None

        self.batch_size = batch_size
        self.backend_configs = backend_configs

        cfg = self.backend_configs.get(self.backend, {})
        self.cfg = cfg

        gpu_ids = str(gpu_ids)
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_ids

        self.device_num = len(gpu_ids.split(","))
```

**File:** servers/generation/src/generation.py (L161-204)
```python
        elif self.backend == "hf":
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
            except ImportError:
                err_msg = "transformers is not installed. Please install it with `pip install transformers`."
                app.logger.error(err_msg)
                raise ImportError(err_msg)

            gpu_ids = str(cfg.get("gpu_ids"))
            os.environ["CUDA_VISIBLE_DEVICES"] = gpu_ids

            model_name_or_path = cfg.get("model_name_or_path")
            hf_pass_cfg = self._drop_keys(
                cfg,
                banned=["gpu_ids", "model_name_or_path", "batch_size"],
            )
            hf_sampling_params = self._drop_keys(
                sampling_params, banned=["chat_template_kwargs"]
            )
            self.chat_template_kwargs = sampling_params.get("chat_template_kwargs", {})
            self.sampling_params = hf_sampling_params
            self.batch_size = int(cfg.get("batch_size", 1))

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                device_map="auto",
                **hf_pass_cfg,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name_or_path,
                padding_side="left",
            )
            added_tokens = 0
            if self.tokenizer.pad_token is None:
                if self.tokenizer.eos_token is not None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                else:
                    added_tokens = self.tokenizer.add_special_tokens(
                        {"pad_token": "[PAD]"}
                    )

            if added_tokens > 0 and hasattr(self.model, "resize_token_embeddings"):
                self.model.resize_token_embeddings(len(self.tokenizer))
        else:
```

**File:** servers/evaluation/src/evaluation.py (L122-152)
```python
# ROUGE-1 Score
def rouge1_score(gt: List[str], pred: str) -> float:
    pred_norm = normalize_text(pred)
    gt_norm_ls = [normalize_text(g) for g in gt]
    scores = []
    for g in gt_norm_ls:
        score = _rouge_scorer.score(g, pred_norm)["rouge1"].fmeasure
        scores.append(score)
    return max(scores) if scores else 0.0


# ROUGE-2 Score
def rouge2_score(gt: List[str], pred: str) -> float:
    pred_norm = normalize_text(pred)
    gt_norm_ls = [normalize_text(g) for g in gt]
    scores = []
    for g in gt_norm_ls:
        score = _rouge_scorer.score(g, pred_norm)["rouge2"].fmeasure
        scores.append(score)
    return max(scores) if scores else 0.0


# ROUGE-L Score
def rougel_score(gt: List[str], pred: str) -> float:
    pred_norm = normalize_text(pred)
    gt_norm_ls = [normalize_text(g) for g in gt]
    scores = []
    for g in gt_norm_ls:
        score = _rouge_scorer.score(g, pred_norm)["rougeL"].fmeasure
        scores.append(score)
    return max(scores) if scores else 0.0
```

**File:** servers/evaluation/src/evaluation.py (L246-285)
```python
def eval_with_pytrec(
    qrels_path: str,
    run_path: str,
    metrics: List[str] | None,
    ks: Optional[List[int]] = None,
) -> Dict[str, Any]:
    try:
        import pytrec_eval
    except ImportError:
        err_msg = "pytrec_eval is not installed. Please install it with `pip install pytrec_eval`"
        app.logger.error(err_msg)
        raise ImportError(err_msg)

    qrel = _load_qrels(qrels_path)
    run = _load_run(run_path)

    measures: set[str] = set()
    if "mrr" in metrics:
        measures.add("recip_rank")
    if "map" in metrics:
        measures.add("map")
    for k in ks:
        if "ndcg" in metrics:
            measures.add(f"ndcg_cut.{k}")
        if "precision" in metrics:
            measures.add(f"P.{k}")
        if "recall" in metrics:
            measures.add(f"recall.{k}")

    evaluator = pytrec_eval.RelevanceEvaluator(qrel, measures)
    per_query = evaluator.evaluate(run)  # {qid: {metric: value}}

    agg: Dict[str, float] = {}
    if per_query:
        pytrec_metrics = sorted(next(iter(per_query.values())).keys())
        n_q = len(per_query)
        for m in pytrec_metrics:
            agg[m] = sum(qres.get(m, 0.0) for qres in per_query.values()) / n_q

    return {"per_query": per_query, "aggregate": agg}
```

**File:** servers/evaluation/src/evaluation.py (L325-333)
```python
@app.tool(output="pred_ls,gt_ls,metrics,save_path->eval_res")
def evaluate(
    pred_ls: List[str],
    gt_ls: List[List[str]],
    metrics: List[str] | None,
    save_path: str,
) -> Dict[str, Any]:
    results = compute_metrics(gt_ls, pred_ls, metrics)
    return save_evaluation_results(results, markdown=True, save_path=save_path)
```

**File:** servers/generation/parameter.yaml (L3-23)
```yaml
backend: vllm # options: vllm, openai
backend_configs:
  vllm:
    model_name_or_path: openbmb/MiniCPM4-8B
    gpu_ids: "2,3"
    gpu_memory_utilization: 0.9
    dtype: auto
    trust_remote_code: true
  openai:
    model_name: MiniCPM4-8B
    base_url: http://localhost:8000/v1
    api_key: ""
    concurrency: 8
    retries: 3
    base_delay: 1.0
  hf:
    model_name_or_path: openbmb/MiniCPM4-8B
    gpu_ids: '2,3'
    trust_remote_code: true
    batch_size: 8

```

**File:** environment.yml (L255-255)
```yaml
  - peft==0.17.1
```

# 我问
当前最新版本的ultrarag如何对多模态文档进行解析和构建索引？

# deepwiki答
您询问的是 UltraRAG v2 如何对多模态文档进行解析和构建索引。<cite/>根据代码库,UltraRAG v2 在 2.1 版本中新增了完整的多模态文档处理能力 [1](#1-0) ,主要通过 **Corpus Server** 和 **Retriever Server** 协同实现。<cite/>

## 多模态文档解析流程

UltraRAG v2 提供两种多模态文档解析方式:

### 1. 基础图像提取 (`build_image_corpus`)

直接从 PDF 中提取图像并构建语料库 [2](#1-1) :

```mermaid
graph TB
    A[PDF文档] --> B[pymupdf解析]
    B --> C[逐页提取图像]
    C --> D[图像验证<br/>PIL.Image.open]
    D --> E[保存到image目录]
    E --> F[生成JSONL语料库<br/>image_path + contents]
``` [3](#1-2) 

### 2. MinerU 结构化解析 (`mineru_parse` + `build_mineru_corpus`)

使用 MinerU 进行深度结构化提取 [4](#1-3) :

```mermaid
graph TB
    A[PDF文档] --> B[mineru命令行解析]
    B --> C[生成auto目录]
    C --> D[提取Markdown文本<br/>stem.md]
    C --> E[提取images目录<br/>结构化图像]
    D --> F[文本语料库JSONL<br/>id + title + contents]
    E --> G[图像语料库JSONL<br/>image_id + image_path]
    F --> H[统一输出]
    G --> H
``` [5](#1-4) 

MinerU 解析会调用外部 `mineru` 命令行工具 [6](#1-5) ,生成的结果包含:
- **文本内容**: 从 `{stem}.md` 文件读取 [7](#1-6) 
- **图像文件**: 从 `images/` 目录收集,支持 `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tiff` 格式 [8](#1-7) 

构建的图像语料库格式为 [9](#1-8) :
```jsonl
{"id": 0, "image_id": "doc1/page1.png", "image_path": "images/doc1/page1.png"}
```

## 多模态索引构建流程

### 嵌入生成 (`retriever_embed`)

Retriever Server 在加载语料库时会根据 `is_multimodal` 参数区分处理方式 [10](#1-9) :

**文本模式**: 读取 `contents` 字段 [11](#1-10) 

**多模态模式**: 读取 `image_path` 字段并解析为绝对路径 [12](#1-11) 

生成嵌入时,不同后端的处理:

**Infinity 后端** [13](#1-12) :
- 多模态: 使用 `PIL.Image.open()` 加载图像,调用 `model.image_embed(images=chunk)`
- 文本: 调用 `model.embed(sentences=chunk)`

**OpenAI 后端**: 不支持图像嵌入 [14](#1-13) 

### 向量索引构建 (`retriever_index`)

嵌入生成后,通过 `retriever_index` 工具构建向量索引 [15](#1-14) :

1. 加载 `.npy` 格式的嵌入文件 [16](#1-15) 
2. 调用索引后端的 `build_index()` 方法 [17](#1-16) 

**FAISS 后端**示例 [18](#1-17) :
- 使用 `IndexFlatIP` (内积相似度) + `IndexIDMap2` (ID映射)
- 分批添加向量,默认每批 50000 个 [19](#1-18) 
- 保存为 `.index` 文件 [20](#1-19) 

## 完整工作流示例

```mermaid
graph LR
    A[PDF文档] --> B[corpus.mineru_parse]
    B --> C[corpus.build_mineru_corpus]
    C --> D[文本JSONL + 图像JSONL]
    D --> E[retriever.retriever_init<br/>is_multimodal=true]
    E --> F[retriever.retriever_embed<br/>infinity/sentence_transformers]
    F --> G[embedding.npy]
    G --> H[retriever.retriever_index<br/>faiss/milvus]
    H --> I[向量索引<br/>.index文件]
    I --> J[retriever.retriever_search<br/>多模态检索]
```

<cite/>

## Notes

- 多模态支持需要安装 `mineru[core]` 和 `pymupdf` 依赖 [21](#1-20) 
- 目前仅 `infinity` 和 `sentence_transformers` 后端支持图像嵌入,OpenAI 后端不支持<cite/>
- MinerU 需要单独安装命令行工具,通过 `shutil.which("mineru")` 检测可用性 [22](#1-21) 
- 图像路径在 JSONL 中存储为相对路径,检索时会解析为绝对路径 [23](#1-22) 

Wiki pages you might want to explore:
- [MCP Server Reference (OpenBMB/UltraRAG)](/wiki/OpenBMB/UltraRAG#3)

### Citations

**File:** README.md (L29-29)
```markdown
- [2025.11.11] 🎉 UltraRAG 2.1 更新：强化知识接入与多模态支持，完善统一评估体系！
```

**File:** README.md (L73-75)
```markdown
	- 支持 PDF、Markdown、HTML、TXT 等多格式文档解析与分块建库；
	- 与 MinerU 无缝集成，自动完成结构化抽取、多模态切块（文本/表格/图片）；
	- 一键构建个人化与企业级知识库，适用于科研、企业文档、私有知识管理等场景。
```

**File:** README.md (L174-182)
```markdown
# Corpus Server依赖：
# chonkie
uv pip install chonkie
# pymupdf
uv pip install pymupdf
# mineru
uv pip install "mineru[core]"
# 一键安装：
uv pip install -e ".[corpus]"
```

**File:** servers/corpus/src/corpus.py (L129-165)
```python
@app.tool(output="parse_file_path,image_corpus_save_path->None")
async def build_image_corpus(
    parse_file_path: str,
    image_corpus_save_path: str,
) -> None:
    try:
        import pymupdf
    except ImportError:
        err_msg = "pymupdf not installed. Please `pip install pymupdf`."
        app.logger.error(err_msg)
        raise ToolError(err_msg)

    in_path = os.path.abspath(parse_file_path)
    if not os.path.exists(in_path):
        err_msg = f"Input path not found: {in_path}"
        app.logger.error(err_msg)
        raise ToolError(err_msg)

    corpus_jsonl = os.path.abspath(image_corpus_save_path)
    out_root = os.path.dirname(corpus_jsonl) or os.getcwd()
    base_img_dir = os.path.join(out_root, "image")
    os.makedirs(base_img_dir, exist_ok=True)

    pdf_list: List[str] = []
    if os.path.isfile(in_path):
        if not in_path.lower().endswith(".pdf"):
            err_msg = f"Only PDF is supported here. Got: {os.path.splitext(in_path)[1]}"
            app.logger.error(err_msg)
            raise ToolError(err_msg)
        pdf_list = [in_path]
    else:
        for dp, _, fns in os.walk(in_path):
            for fn in sorted(fns):
                if fn.lower().endswith(".pdf"):
                    pdf_list.append(os.path.join(dp, fn))
        pdf_list.sort()

```

**File:** servers/corpus/src/corpus.py (L240-246)
```python
    _save_jsonl(valid_rows, corpus_jsonl)
    info_msg = (
        f"Built image corpus: {corpus_jsonl} (valid images={len(valid_rows)}), "
        f"images root: {base_img_dir}, "
        f"pdf_count={len(pdf_list)}"
    )
    app.logger.info(info_msg)
```

**File:** servers/corpus/src/corpus.py (L249-314)
```python
@app.tool(output="parse_file_path,mineru_dir,mineru_extra_params->None")
async def mineru_parse(
    parse_file_path: str,
    mineru_dir: str,
    mineru_extra_params: Optional[Dict[str, Any]] = None,
) -> None:

    if shutil.which("mineru") is None:
        err_msg = "`mineru` executable not found. Please install it or add it to PATH."
        app.logger.error(err_msg)
        raise ToolError(err_msg)

    if not parse_file_path:
        err_msg = "`parse_file_path` cannot be empty."
        app.logger.error(err_msg)
        raise ToolError(err_msg)

    in_path = os.path.abspath(parse_file_path)
    if not os.path.exists(in_path):
        err_msg = f"Input path not found: {in_path}"
        app.logger.error(err_msg)
        raise ToolError(err_msg)

    if os.path.isfile(in_path) and not in_path.lower().endswith(".pdf"):
        err_msg = f"Only .pdf files or directories are supported: {in_path}"
        app.logger.error(err_msg)
        raise ToolError(err_msg)

    out_root = os.path.abspath(mineru_dir)
    os.makedirs(out_root, exist_ok=True)

    extra_args: List[str] = []
    if mineru_extra_params:
        for k in sorted(mineru_extra_params.keys()):
            v = mineru_extra_params[k]
            extra_args.append(f"--{k}")
            if v is not None and v != "":
                extra_args.append(str(v))

    cmd = ["mineru", "-p", in_path, "-o", out_root] + extra_args
    info_msg = f"Starting mineru command: {' '.join(cmd)}"
    app.logger.info(info_msg)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert proc.stdout is not None
        async for line in proc.stdout:
            app.logger.info(line.decode("utf-8", errors="replace").rstrip())

        returncode = await proc.wait()
        if returncode != 0:
            err_msg = f"mineru exited with non-zero code: {returncode}"
            app.logger.error(err_msg)
            raise ToolError(err_msg)
    except Exception as e:
        err_msg = f"Unexpected error while running mineru: {e}"
        app.logger.error(err_msg)
        raise ToolError(err_msg)

    info_msg = f"mineru finished processing {in_path} into {out_root}"
    app.logger.info(info_msg)

```

**File:** servers/corpus/src/corpus.py (L316-327)
```python
def _list_images(images_dir: str) -> List[str]:
    if not os.path.isdir(images_dir):
        return []
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    rels = []
    for dp, _, fns in os.walk(images_dir):
        for fn in sorted(fns):
            if os.path.splitext(fn)[1].lower() in exts:
                rel = os.path.relpath(os.path.join(dp, fn), start=images_dir)
                rels.append(Path(rel).as_posix())
    rels.sort()
    return rels
```

**File:** servers/corpus/src/corpus.py (L395-402)
```python
        md_path = os.path.join(auto_dir, f"{stem}.md")
        if not os.path.isfile(md_path):
            warn_msg = f"Markdown not found for '{stem}': {md_path} (skip text)"
            app.logger.warning(warn_msg)
        else:
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read().strip()
            text_rows.append({"id": stem, "title": stem, "contents": md_text})
```

**File:** servers/corpus/src/corpus.py (L424-431)
```python
            shutil.copy2(src, dst)
            image_rows.append(
                {
                    "id": len(image_rows),
                    "image_id": Path(os.path.join(stem, rel)).as_posix(),
                    "image_path": Path(os.path.join("images", stem, rel)).as_posix(),
                }
            )
```

**File:** servers/retriever/src/retriever.py (L251-270)
```python
                    if not is_multimodal or self.backend == "bm25":
                        if "contents" not in item:
                            error_msg = (
                                f"Line {i}: missing key 'contents'. full item={item}"
                            )
                            app.logger.error(error_msg)
                            raise ValueError(error_msg)

                        self.contents.append(item["contents"])
                    else:
                        if "image_path" not in item:
                            error_msg = (
                                f"Line {i}: missing key 'image_path'. full item={item}"
                            )
                            app.logger.error(error_msg)
                            raise ValueError(error_msg)

                        rel = str(item["image_path"])
                        abs_path = str((corpus_dir / rel).resolve())
                        self.contents.append(abs_path)
```

**File:** servers/retriever/src/retriever.py (L344-374)
```python
        if self.backend == "infinity":
            async with self.model:
                if is_multimodal:
                    data = []
                    for i, p in enumerate(self.contents):
                        try:
                            with Image.open(p) as im:
                                data.append(im.convert("RGB").copy())
                        except Exception as e:
                            err_msg = f"Failed to load image at index {i}: {p} ({e})"
                            app.logger.error(err_msg)
                            raise RuntimeError(err_msg)
                    call = self.model.image_embed
                else:
                    data = self.contents
                    call = self.model.embed

                eff_bs = self.batch_size * self.device_num
                n = len(data)
                pbar = tqdm(total=n, desc="[infinity] Embedding:")
                embeddings = []
                for i in range(0, n, eff_bs):
                    chunk = data[i : i + eff_bs]
                    vecs, _ = (
                        await call(images=chunk)
                        if is_multimodal
                        else await call(sentences=chunk)
                    )
                    embeddings.extend(vecs)
                    pbar.update(len(chunk))
                pbar.close()
```

**File:** servers/retriever/src/retriever.py (L431-436)
```python
            if is_multimodal:
                err_msg = (
                    "openai backend does not support image embeddings in this path."
                )
                app.logger.error(err_msg)
                raise ValueError(err_msg)
```

**File:** servers/retriever/src/retriever.py (L466-505)
```python
    def retriever_index(
        self,
        embedding_path: str,
        overwrite: bool = False,
    ):
        if self.backend == "bm25":
            err_msg = "BM25 backend does not support vector index building via retriever_index."
            app.logger.error(err_msg)
            raise ValueError(err_msg)

        if self.index_backend is None:
            err_msg = (
                "Vector index backend is not initialized. "
                "Ensure retriever_init completed successfully."
            )
            app.logger.error(err_msg)
            raise RuntimeError(err_msg)

        if not os.path.exists(embedding_path):
            app.logger.error(f"Embedding file not found: {embedding_path}")
            raise NotFoundError(f"Embedding file not found: {embedding_path}")

        embedding = np.load(embedding_path)
        vec_ids = np.arange(embedding.shape[0]).astype(np.int64)
        
        try:
            self.index_backend.build_index(
                embeddings=embedding,
                ids=vec_ids,
                overwrite=overwrite,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        finally:
            del embedding
            gc.collect()

        
        info_msg = f"[{self.index_backend_name}] Indexing success."
        app.logger.info(info_msg)
```

**File:** servers/retriever/src/index_backends/faiss_backend.py (L92-149)
```python
    def build_index(
        self,
        *,
        embeddings: np.ndarray,
        ids: np.ndarray,
        overwrite: bool = False,
    ) -> None:

        if not self.index_path.endswith(".index"):
            err_msg = (
                f"Parameter 'index_path' must end with '.index', got '{self.index_path}'"
            )
            raise ValidationError(err_msg)

        if not overwrite and os.path.exists(self.index_path):
            info_msg = (
                f"Index file already exists: {self.index_path}. "
                "Set overwrite=True to overwrite."
            )
            self.logger.info(info_msg)
            return

        dir_path = os.path.dirname(self.index_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        embeddings = np.asarray(embeddings, dtype=np.float32, order="C")
        ids = np.asarray(ids, dtype=np.int64)
        if embeddings.ndim != 2:
            raise ValueError("[faiss] embeddings must be 2-D array.")
        if ids.ndim != 1 or ids.shape[0] != embeddings.shape[0]:
            raise ValueError("[faiss] ids must be 1-D array aligned with embeddings.")

        dim = embeddings.shape[1]
        cpu_flat = faiss.IndexFlatIP(dim)
        cpu_index = faiss.IndexIDMap2(cpu_flat)

        total = embeddings.shape[0]
        info_msg = f"Start building FAISS index, total vectors: {total}"
        self.logger.info(info_msg)
        
        
        index_chunk_size = int(self.config.get("index_chunk_size"))
        with tqdm(
            total=total,
            desc="[faiss] Indexing: ",
            unit="vec",
        ) as pbar:
            for start in range(0, total, index_chunk_size):
                end = min(start + index_chunk_size, total)
                cpu_index.add_with_ids(embeddings[start:end], ids[start:end])
                pbar.update(end - start)

        faiss.write_index(cpu_index, self.index_path)
        self.logger.info("[faiss] Index written to '%s'.", self.index_path)
        
        self.index = self._maybe_to_gpu(cpu_index)
        
```
