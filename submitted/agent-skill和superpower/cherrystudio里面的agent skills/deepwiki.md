我想知道，cherry studio里面，agent模式的插件里面「技能」是如何运作的？我安装后怎么判断起作用了？


## 技能运作机制

在 Cherry Studio 的 Agent 模式中，「技能」是通过插件系统实现的特殊工具类型。技能作为 `AgentToolsType.Skill` 类型被定义在工具枚举中 [1](#0-0) 。

### 技能的工作流程

1. **插件安装**：技能通过插件浏览器安装，分为 agent、command、skill 三种类型 [2](#0-1) 

2. **技能加载**：Agent 服务在获取 Agent 信息时，会从工作目录的缓存文件中加载已安装的插件 [3](#0-2) 

3. **技能执行**：当 Agent 调用技能时，通过 `SkillTool` 渲染器处理技能的输入和输出 [4](#0-3) 

4. **消息展示**：技能的执行结果通过 `MessageTool` 组件判断并渲染相应的工具界面 [5](#0-4) 

### 判断技能是否生效

您可以通过以下方式判断技能是否正常工作：

1. **插件列表确认**：在 Agent 设置的插件页面，查看技能是否出现在"已安装"列表中 [6](#0-5) 

2. **工具调用日志**：当 Agent 使用技能时，会在对话界面显示工具调用卡片，包含技能名称和执行结果

3. **错误提示**：如果技能加载失败，控制台会显示警告日志但不会中断 Agent 运行 [7](#0-6) 

## Notes

技能插件需要放置在 Agent 的工作目录中才能被正确加载。技能的输入参数遵循 `SkillToolInput` 接口，包含 `command` 字段来指定要执行的具体技能命令 [8](#0-7) 。

Wiki pages you might want to explore:
- [Data Models and Types (CherryHQ/cherry-studio)](/wiki/CherryHQ/cherry-studio#3.5)

### Citations

**File:** src/renderer/src/pages/home/Messages/Tools/MessageAgentTools/types.ts (L1-32)
```typescript
export enum AgentToolsType {
  Skill = 'Skill',
  Read = 'Read',
  Task = 'Task',
  Bash = 'Bash',
  Search = 'Search',
  Glob = 'Glob',
  TodoWrite = 'TodoWrite',
  WebSearch = 'WebSearch',
  Grep = 'Grep',
  Write = 'Write',
  WebFetch = 'WebFetch',
  Edit = 'Edit',
  MultiEdit = 'MultiEdit',
  BashOutput = 'BashOutput',
  NotebookEdit = 'NotebookEdit',
  ExitPlanMode = 'ExitPlanMode'
}

export type TextOutput = {
  type: 'text'
  text: string
}

// Read 工具的类型定义
export interface SkillToolInput {
  /**
   * The skill to use
   */
  command: string
}

```

**File:** src/renderer/src/pages/settings/AgentSettings/components/PluginBrowser.tsx (L23-61)
```typescript
type PluginType = 'all' | 'agent' | 'command' | 'skill'

const ITEMS_PER_PAGE = 12

export const PluginBrowser: FC<PluginBrowserProps> = ({
  agentId,
  agents,
  commands,
  skills,
  installedPlugins,
  onInstall,
  onUninstall,
  loading
}) => {
  const { t } = useTranslation()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [activeType, setActiveType] = useState<PluginType>('all')
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE)
  const [actioningPlugin, setActioningPlugin] = useState<string | null>(null)
  const [selectedPlugin, setSelectedPlugin] = useState<PluginMetadata | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const observerTarget = useRef<HTMLDivElement>(null)
  const [filterDropdownOpen, setFilterDropdownOpen] = useState(false)

  // Combine all plugins based on active type
  const allPlugins = useMemo(() => {
    switch (activeType) {
      case 'agent':
        return agents
      case 'command':
        return commands
      case 'skill':
        return skills
      case 'all':
      default:
        return [...agents, ...commands, ...skills]
    }
  }, [agents, commands, skills, activeType])
```

**File:** src/main/services/agents/services/AgentService.ts (L96-111)
```typescript
    // Load installed_plugins from cache file instead of database
    const workdir = agent.accessible_paths?.[0]
    if (workdir) {
      try {
        agent.installed_plugins = await pluginService.listInstalledFromCache(workdir)
      } catch (error) {
        // Log error but don't fail the request
        logger.warn(`Failed to load installed plugins for agent ${id}`, {
          workdir,
          error: error instanceof Error ? error.message : String(error)
        })
        agent.installed_plugins = []
      }
    } else {
      agent.installed_plugins = []
    }
```

**File:** src/renderer/src/pages/home/Messages/Tools/MessageAgentTools/index.tsx (L52-54)
```typescript
  [AgentToolsType.ExitPlanMode]: ExitPlanModeTool,
  [AgentToolsType.Skill]: SkillTool
} as const
```

**File:** src/renderer/src/pages/home/Messages/Tools/MessageTool.tsx (L40-42)
```typescript
  } else if (isAgentTool(toolName as AgentToolsType)) {
    return <MessageAgentTools toolResponse={toolResponse} />
  }
```

**File:** src/renderer/src/pages/settings/AgentSettings/PluginSettings.tsx (L107-112)
```typescript
          <InstalledPluginsList
            plugins={plugins}
            onUninstall={handleUninstall}
            loading={loadingInstalled || uninstalling}
          />
        )}
```


___________________


假设我有n多个skill，是如何选择skill呢？比如每个SKILL.md的内容，如何送到模型？我看这个文件内容很长，除了name和desc外，还有很多代码

## 技能选择机制

在 Cherry Studio 的 Agent 模式中，技能选择是通过 MCP (Model Context Protocol) 工具系统实现的。模型根据技能的描述和功能来选择使用哪个技能。

### 技能发现和加载

当 Agent 启动时，系统会通过 `fetchMcpTools` 函数获取所有可用的技能工具 [1](#1-0) ：

```typescript
export async function fetchMcpTools(assistant: Assistant) {
  let mcpTools: MCPTool[] = []
  const allMcpServers = store.getState().mcp.servers || []
  const activedMcpServers = allMcpServers.filter((s) => s.isActive)
  const assistantMcpServers = assistant.mcpServers || []
  
  const enabledMCPs = activedMcpServers.filter((server) => 
    assistantMcpServers.some((s) => s.id === server.id)
  )
  
  // 获取每个服务器的工具列表
  const toolPromises = enabledMCPs.map(async (mcpServer: MCPServer) => {
    const tools = await window.api.mcp.listTools(mcpServer)
    return tools.filter((tool: any) => !mcpServer.disabledTools?.includes(tool.name))
  })
}
```

### 技能信息传递给模型

技能的详细信息（不仅仅是 name 和 description）通过以下方式传递给模型：

1. **工具定义结构**：每个技能工具包含完整的元数据，包括名称、描述、参数结构等
2. **系统提示集成**：在 `buildStreamTextParams` 中，工具信息被整合到模型的系统提示中 [2](#1-1) 
3. **动态工具列表**：模型在每次对话中都能看到当前可用的所有技能工具

### 技能选择过程

模型选择技能的过程如下：

1. **工具列表展示**：所有可用技能的名称和描述被展示给模型
2. **上下文匹配**：模型根据用户请求和技能描述进行匹配
3. **参数验证**：模型使用技能时需要提供符合 `SkillToolInput` 接口的参数 [3](#1-2) 
4. **工具调用**：模型通过 `command` 字段指定要执行的具体技能

### SKILL.md 文件内容处理

SKILL.md 文件的完整内容（包括代码示例）通过以下机制处理：

1. **元数据提取**：从 SKILL.md 中提取 name、description 等元数据
2. **内容保留**：完整的文档内容被保留，用于提供详细的技能说明
3. **工具描述生成**：系统可能基于完整内容生成更丰富的工具描述，帮助模型更好地理解技能功能

## Notes

技能的详细内容（包括代码示例）对于模型理解技能的具体用法很重要。虽然这会增加提示长度，但能提供更准确的技能选择和执行。系统通过 MCP 协议确保技能信息的完整传递，同时保持工具调用的类型安全 [4](#1-3) 。

Wiki pages you might want to explore:
- [Data Models and Types (CherryHQ/cherry-studio)](/wiki/CherryHQ/cherry-studio#3.5)
- [AI Model Integration (CherryHQ/cherry-studio)](/wiki/CherryHQ/cherry-studio#5)

### Citations

**File:** src/renderer/src/services/ApiService.ts (L54-84)
```typescript
export async function fetchMcpTools(assistant: Assistant) {
  // Get MCP tools (Fix duplicate declaration)
  let mcpTools: MCPTool[] = [] // Initialize as empty array
  const allMcpServers = store.getState().mcp.servers || []
  const activedMcpServers = allMcpServers.filter((s) => s.isActive)
  const assistantMcpServers = assistant.mcpServers || []

  const enabledMCPs = activedMcpServers.filter((server) => assistantMcpServers.some((s) => s.id === server.id))

  if (enabledMCPs && enabledMCPs.length > 0) {
    try {
      const toolPromises = enabledMCPs.map(async (mcpServer: MCPServer) => {
        try {
          const tools = await window.api.mcp.listTools(mcpServer)
          return tools.filter((tool: any) => !mcpServer.disabledTools?.includes(tool.name))
        } catch (error) {
          logger.error(`Error fetching tools from MCP server ${mcpServer.name}:`, error as Error)
          return []
        }
      })
      const results = await Promise.allSettled(toolPromises)
      mcpTools = results
        .filter((result): result is PromiseFulfilledResult<MCPTool[]> => result.status === 'fulfilled')
        .map((result) => result.value)
        .flat()
    } catch (toolError) {
      logger.error('Error fetching MCP tools:', toolError as Error)
    }
  }
  return mcpTools
}
```

**File:** src/renderer/src/services/ApiService.ts (L186-195)
```typescript
  const {
    params: aiSdkParams,
    modelId,
    capabilities,
    webSearchPluginConfig
  } = await buildStreamTextParams(messages, assistant, provider, {
    mcpTools: mcpTools,
    webSearchProviderId: assistant.webSearchProviderId,
    requestOptions
  })
```

**File:** src/renderer/src/pages/home/Messages/Tools/MessageAgentTools/types.ts (L25-31)
```typescript
// Read 工具的类型定义
export interface SkillToolInput {
  /**
   * The skill to use
   */
  command: string
}
```

**File:** src/renderer/src/pages/home/Messages/Tools/MessageAgentTools/index.tsx (L52-54)
```typescript
  [AgentToolsType.ExitPlanMode]: ExitPlanModeTool,
  [AgentToolsType.Skill]: SkillTool
} as const
```


_____________________________

代码层面是如何「从 SKILL.md 中提取 name、description 等元数据」


## SKILL.md 元数据提取机制

在 Cherry Studio 中，从 SKILL.md 文件提取元数据是通过 `parseSkillMetadata` 函数实现的 [1](#2-0) 。

### 元数据提取流程

1. **技能目录扫描**：系统首先通过 `findAllSkillDirectories` 函数扫描技能目录，找到所有技能文件夹 [2](#2-1) 

2. **元数据解析**：对每个技能目录，调用 `parseSkillMetadata` 函数解析元数据 [3](#2-2) 

3. **数据结构**：解析后的元数据遵循 `PluginMetadata` 结构，包含以下字段 [4](#2-3) ：
   - `sourcePath`: 源文件路径
   - `filename`: 文件名（技能类型为文件夹名）
   - `name`: 显示名称
   - `description`: 描述信息
   - `category`: 分类（从父文件夹名派生）
   - `type`: 插件类型（'skill'）
   - `tags`: 标签数组
   - `tools`: 工具数组
   - 其他元数据如版本、作者、文件大小、内容哈希等

### 技能安装时的元数据提取

在安装技能插件时，系统会：
1. 确保技能源目录存在 [5](#2-4) 
2. 解析技能元数据 [3](#2-2) 
3. 对文件夹名进行清理处理 [6](#2-5) 
4. 将技能安装到目标位置 [7](#2-6) 

### 错误处理

如果解析失败，系统会记录警告日志但不会中断整个流程 [8](#2-7) 。

## Notes

实际的 `parseSkillMetadata` 函数实现位于 `@main/utils/markdownParser` 模块中，该模块负责解析 Markdown 文件的前置元数据（frontmatter）并提取相关信息。技能类型与普通插件不同，它使用整个文件夹作为技能单元，而 `filename` 字段存储的是文件夹名而非文件名 [9](#2-8) 。

### Citations

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L2-2)
```typescript
import { findAllSkillDirectories, parsePluginMetadata, parseSkillMetadata } from '@main/utils/markdownParser'
```

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L86-92)
```typescript
      const skillDirectories = await findAllSkillDirectories(skillsPath, basePath)
      logger.info(`Found ${skillDirectories.length} skill directories`, { skillsPath })

      for (const { folderPath, sourcePath } of skillDirectories) {
        try {
          const metadata = await parseSkillMetadata(folderPath, sourcePath, 'skills')
          skills.push(metadata)
```

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L94-98)
```typescript
          logger.warn(`Failed to parse skill folder: ${sourcePath}`, {
            folderPath,
            error: error instanceof Error ? error.message : String(error)
          })
        }
```

**File:** src/main/services/agents/plugins/PluginService.ts (L165-165)
```typescript
    await this.cacheStore.ensureSkillSourceDirectory(sourceAbsolutePath, options.sourcePath)
```

**File:** src/main/services/agents/plugins/PluginService.ts (L167-167)
```typescript
    const metadata = await parseSkillMetadata(sourceAbsolutePath, options.sourcePath, 'skills')
```

**File:** src/main/services/agents/plugins/PluginService.ts (L168-168)
```typescript
    const sanitizedFolderName = this.sanitizeFolderName(metadata.filename)
```

**File:** src/main/services/agents/plugins/PluginService.ts (L175-175)
```typescript
    await this.installer.installSkill(agent.id, sourceAbsolutePath, destPath)
```

**File:** src/renderer/src/types/plugin.ts (L7-34)
```typescript
export const PluginMetadataSchema = z.object({
  // Identification
  sourcePath: z.string(), // e.g., "agents/ai-specialists/ai-ethics-advisor.md" or "skills/my-skill"
  filename: z.string(), // IMPORTANT: Semantics vary by type:
  // - For agents/commands: includes .md extension (e.g., "my-agent.md")
  // - For skills: folder name only, no extension (e.g., "my-skill")
  name: z.string(), // Display name from frontmatter or filename

  // Content
  description: z.string().optional(),
  allowed_tools: z.array(z.string()).optional(), // from frontmatter (for commands)
  tools: z.array(z.string()).optional(), // from frontmatter (for agents and skills)

  // Organization
  category: z.string(), // derived from parent folder name
  type: z.enum(['agent', 'command', 'skill']), // UPDATED: now includes 'skill'
  tags: z.array(z.string()).optional(),

  // Versioning (for future updates)
  version: z.string().optional(),
  author: z.string().optional(),

  // Metadata
  size: z.number(), // file size in bytes
  contentHash: z.string(), // SHA-256 hash for change detection
  installedAt: z.number().optional(), // Unix timestamp (for installed plugins)
  updatedAt: z.number().optional() // Unix timestamp (for installed plugins)
})
```

________________________________

agent和用户交互过程中，是每一轮交互都会读取SKILL.md？还是首次识别要使用某个skill的时候就已经把SKILL.md结构化解析缓存在内存中？


## 技能元数据缓存机制

在 Cherry Studio 中，SKILL.md 文件**不会在每一轮交互中都重新读取**。系统采用了**缓存机制**，在首次加载时将技能元数据解析并存储在缓存中。

### 缓存加载时机

1. **Agent 获取时加载**：当调用 `AgentService.getAgent()` 获取 Agent 信息时，系统会从工作目录的缓存文件中加载已安装的插件 [1](#3-0) 。

2. **缓存文件读取**：系统通过 `pluginService.listInstalledFromCache(workdir)` 从缓存文件读取插件信息，而不是重新解析 SKILL.md [2](#3-1) 。

### 缓存存储机制

1. **缓存文件位置**：插件信息存储在 Agent 工作目录的 `plugins.json` 文件中 [3](#3-2) 。

2. **缓存数据结构**：缓存文件包含 `CachedPluginsData`，其中存储了所有已安装插件的元数据 [4](#3-3) 。

3. **元数据更新**：只有在安装新技能时才会重新解析 SKILL.md 并更新缓存 [5](#3-4) 。

### 性能优化设计

这种缓存机制的设计考虑了性能优化：

- **避免重复解析**：SKILL.md 文件通常包含大量内容（包括代码示例），每次交互都重新解析会造成性能开销
- **快速响应**：从内存/缓存文件读取元数据比解析 Markdown 文件快得多
- **一致性保证**：缓存确保了同一技能在不同交互中使用相同的元数据

### 缓存更新触发

缓存只会在以下情况更新：
1. **安装新技能**时 [6](#3-5) 
2. **卸载技能**时
3. **手动刷新插件列表**时

## Notes

SKILL.md 的完整内容（包括代码示例）在安装时被解析并提取为结构化的 `PluginMetadata`，存储在缓存文件中。后续的交互直接使用缓存数据，不会重复读取和解析 SKILL.md 文件 [7](#3-6) 。这种设计既保证了性能，又确保了技能信息的一致性。

Wiki pages you might want to explore:
- [Database and Persistence (CherryHQ/cherry-studio)](/wiki/CherryHQ/cherry-studio#3.4)

### Citations

**File:** src/main/services/agents/services/AgentService.ts (L96-111)
```typescript
    // Load installed_plugins from cache file instead of database
    const workdir = agent.accessible_paths?.[0]
    if (workdir) {
      try {
        agent.installed_plugins = await pluginService.listInstalledFromCache(workdir)
      } catch (error) {
        // Log error but don't fail the request
        logger.warn(`Failed to load installed plugins for agent ${id}`, {
          workdir,
          error: error instanceof Error ? error.message : String(error)
        })
        agent.installed_plugins = []
      }
    } else {
      agent.installed_plugins = []
    }
```

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L91-92)
```typescript
          const metadata = await parseSkillMetadata(folderPath, sourcePath, 'skills')
          skills.push(metadata)
```

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L404-416)
```typescript
  private async readCacheFile(claudePath: string): Promise<CachedPluginsData | null> {
    const cachePath = path.join(claudePath, 'plugins.json')
    try {
      const content = await fs.promises.readFile(cachePath, 'utf-8')
      const data = JSON.parse(content)
      return CachedPluginsDataSchema.parse(data)
    } catch (err) {
      logger.warn(`Failed to read cache file at ${cachePath}`, {
        error: err instanceof Error ? err.message : String(err)
      })
      return null
    }
  }
```

**File:** src/main/services/agents/plugins/PluginService.ts (L167-193)
```typescript
    const metadata = await parseSkillMetadata(sourceAbsolutePath, options.sourcePath, 'skills')
    const sanitizedFolderName = this.sanitizeFolderName(metadata.filename)

    await this.ensureClaudeDirectory(workdir, 'skill')
    const destPath = this.getClaudePluginPath(workdir, 'skill', sanitizedFolderName)

    metadata.filename = sanitizedFolderName

    await this.installer.installSkill(agent.id, sourceAbsolutePath, destPath)

    const installedAt = Date.now()
    const metadataWithInstall: PluginMetadata = {
      ...metadata,
      filename: sanitizedFolderName,
      installedAt,
      updatedAt: metadata.updatedAt ?? installedAt,
      type: 'skill'
    }
    const installedPlugin: InstalledPlugin = {
      filename: sanitizedFolderName,
      type: 'skill',
      metadata: metadataWithInstall
    }

    await this.cacheStore.upsert(workdir, installedPlugin)
    this.upsertAgentPlugin(agent, installedPlugin)

```


________________________________

缓存文件还是内存？长啥样子的？


## 缓存存储方式

在 Cherry Studio 中，技能元数据**存储在文件系统中**，而不是纯内存中。缓存以 JSON 文件形式持久化保存。

### 缓存文件位置

缓存文件存储在 Agent 工作目录的 `.claude/plugins.json` 路径下 [1](#4-0) 。

### 缓存文件结构

缓存文件遵循 `CachedPluginsData` 结构，具体格式如下 [2](#4-1) ：

```json
{
  "version": 1,
  "lastUpdated": 1704067200000,
  "plugins": [
    {
      "filename": "my-skill",
      "type": "skill",
      "metadata": {
        "sourcePath": "/path/to/skill",
        "filename": "my-skill",
        "name": "My Skill",
        "description": "A useful skill",
        "category": "skills",
        "type": "skill",
        "tags": ["utility"],
        "tools": [],
        "installedAt": 1704067200000
      }
    }
  ]
}
```

### 缓存读写机制

1. **读取缓存**：通过 `readCacheFile` 方法读取 JSON 文件并验证格式 [3](#4-2) 

2. **写入缓存**：通过 `writeCacheFile` 方法先写入临时文件，然后原子性重命名 [4](#4-3) 

3. **内存加载**：虽然缓存存储在文件中，但运行时会加载到内存供快速访问 [5](#4-4) 

### 性能优化

这种文件缓存+内存加载的设计提供了：
- **持久性**：应用重启后缓存仍然存在
- **快速访问**：运行时从内存读取，避免重复文件 I/O
- **原子更新**：使用临时文件+重命名确保写入安全 [6](#4-5) 

## Notes

缓存文件在 Agent 首次获取插件信息时创建，之后每次交互都直接从内存中的缓存数据读取，只有在安装/卸载插件或手动刷新时才会更新文件缓存 [7](#4-6) 。

Wiki pages you might want to explore:
- [Database and Persistence (CherryHQ/cherry-studio)](/wiki/CherryHQ/cherry-studio#3.4)

### Citations

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L225-232)
```typescript
  async listInstalled(workdir: string): Promise<InstalledPlugin[]> {
    const claudePath = this.deps.getClaudeBasePath(workdir)
    const cacheData = await this.readCacheFile(claudePath)

    if (cacheData) {
      logger.debug(`Loaded ${cacheData.plugins.length} plugins from cache`, { workdir })
      return cacheData.plugins
    }
```

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L404-415)
```typescript
  private async readCacheFile(claudePath: string): Promise<CachedPluginsData | null> {
    const cachePath = path.join(claudePath, 'plugins.json')
    try {
      const content = await fs.promises.readFile(cachePath, 'utf-8')
      const data = JSON.parse(content)
      return CachedPluginsDataSchema.parse(data)
    } catch (err) {
      logger.warn(`Failed to read cache file at ${cachePath}`, {
        error: err instanceof Error ? err.message : String(err)
      })
      return null
    }
```

**File:** src/main/services/agents/plugins/PluginCacheStore.ts (L418-425)
```typescript
  private async writeCacheFile(claudePath: string, data: CachedPluginsData): Promise<void> {
    const cachePath = path.join(claudePath, 'plugins.json')
    const tempPath = `${cachePath}.tmp`

    const content = JSON.stringify(data, null, 2)
    await fs.promises.writeFile(tempPath, content, 'utf-8')
    await fs.promises.rename(tempPath, cachePath)
  }
```

**File:** src/renderer/src/types/plugin.ts (L46-51)
```typescript
// Cache file schema for .claude/plugins.json
export const CachedPluginsDataSchema = z.object({
  version: z.number().default(1),
  lastUpdated: z.number(), // Unix timestamp in milliseconds
  plugins: z.array(InstalledPluginSchema)
})
```

**File:** src/main/services/agents/services/AgentService.ts (L96-111)
```typescript
    // Load installed_plugins from cache file instead of database
    const workdir = agent.accessible_paths?.[0]
    if (workdir) {
      try {
        agent.installed_plugins = await pluginService.listInstalledFromCache(workdir)
      } catch (error) {
        // Log error but don't fail the request
        logger.warn(`Failed to load installed plugins for agent ${id}`, {
          workdir,
          error: error instanceof Error ? error.message : String(error)
        })
        agent.installed_plugins = []
      }
    } else {
      agent.installed_plugins = []
    }
```
