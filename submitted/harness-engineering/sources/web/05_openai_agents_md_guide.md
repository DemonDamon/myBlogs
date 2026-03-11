# Custom instructions with AGENTS.md - OpenAI Codex

**URL**: https://developers.openai.com/codex/guides/agents-md/

---

Codex reads `AGENTS.md` files before doing any work. By layering global guidance with project-specific overrides, you can start each task with consistent expectations, no matter which repository you open.

## How Codex discovers guidance

Codex builds an instruction chain when it starts. Discovery follows this precedence order:

### Merge order

Codex concatenates files from the root down, joining them with blank lines. **Files closer to your current directory override earlier guidance** because they appear later in the combined prompt.

### Discovery Path

1. **Project scope**: Starting at the project root (typically the Git root), Codex walks down to your current working directory.
   - In each directory: checks for `AGENTS.override.md` → `AGENTS.md` → fallback names
   - Includes at most one file per directory

2. **Global scope**: In your Codex home directory (`~/.codex`)
   - Reads `AGENTS.override.md` if exists, otherwise `AGENTS.md`
   - Uses only the first non-empty file at this level

### Size Limits

Codex skips empty files and stops adding files once the combined size reaches `project_doc_max_bytes` (**32 KiB by default**).

## Create global guidance

Create persistent defaults in your Codex home directory so every repository inherits your working agreements.

```bash
mkdir -p ~/.codex
```

Example `~/.codex/AGENTS.md`:

```md
# ~/.codex/AGENTS.md

## Working agreements

- Always run `npm test` after modifying JavaScript files.
- Prefer `pnpm` when installing dependencies.
- Ask for confirmation before adding new production dependencies.
```

## Layer project instructions

Repository-level files keep Codex aware of project norms while still inheriting your global defaults.

Example repository root `AGENTS.md`:

```md
# AGENTS.md

## Repository expectations

- Run `npm run lint` before opening a pull request.
- Document public utilities in `docs/` when you change behavior.
```

Example nested override `services/payments/AGENTS.override.md`:

```md
# services/payments/AGENTS.override.md

## Payments service rules

- Use `make test-payments` instead of `npm test`.
- Never rotate API keys without notifying the security channel.
```

## Customize fallback filenames

If your repository already uses a different filename, add it to the fallback list:

```toml
# ~/.codex/config.toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536
```

## Best Practices

1. **保持精简**：32 KiB 限制确保 Agent 不会过载
2. **分层覆盖**：全局 → 项目 → 子目录，每层专注特定范围
3. **覆盖文件用于临时变更**：`AGENTS.override.md` 便于测试不破坏基础配置
4. **验证加载**：使用 `codex --ask-for-approval never "Summarize the current instructions."` 确认生效

---
**Source**: https://developers.openai.com/codex/guides/agents-md/
