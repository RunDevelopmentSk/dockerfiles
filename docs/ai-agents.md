# Programming AI Agents

The following programming AI agents are available in the devcontainer:

- **Augment Code** (VS Code extension) and/or `auggie` (Auggie CLI)
- **Claude Code** (VS Code extension) and/or `claude` (Claude Code CLI)
- `agy` (**Antigravity** CLI)
- **Codex** (VS Code extension) and/or `codex` (Codex CLI)

Usage details for each AI agent are described below.

## Unified Configuration (`.agents/` + `AGENTS.md`)

For all agents, **one source of truth** is used for project instructions, workspace rules and skills across all agents:

- [`AGENTS.md`](../AGENTS.md) in the root directory – main project instructions in the standard [agents.md](https://agents.md/) format.
- [`.agents/rules/`](../.agents/rules/) – modular workspace rules.
- [`.agents/skills/`](../.agents/skills/) – cross-tool skills in the standard [agentskills.io](https://agentskills.io/) format.
- [`.agents/commands/`](../.agents/commands/) – custom slash commands shared across agents; each `<name>.md` file creates a `/name` command.
- [`.agents/agents/`](../.agents/agents/) – subagents shared across agents; `.md` for Claude Code and Auggie, `.toml` for Codex (each agent takes the format it knows).

Where an agent does not natively support the `.agents/` + `AGENTS.md` standard, it is resolved by **symbolic links committed to the repo**:

| Symlink                                   | Reason                                                                                            |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `CLAUDE.md → AGENTS.md`                   | Claude Code reads `CLAUDE.md`.                                                                    |
| `.claude/skills → ../.agents/skills`      | Claude Code reads skills from `.claude/skills/`.                                                  |
| `.augment/rules → ../.agents/rules`       | Augment Code reads workspace rules from `.augment/rules/`.                                            |
| `.mcp.json → .agents/mcp_config.json`     | Claude Code reads the MCP configuration from `.mcp.json` in the root; Antigravity from `.agents/mcp_config.json`. |
| `.augment/commands → ../.agents/commands` | Augment Code reads slash commands from `.augment/commands/`.                                          |
| `.claude/commands → ../.agents/commands`  | Claude Code reads slash commands from `.claude/commands/`.                                            |
| `.agents/workflows → commands`            | Antigravity reads slash commands from `.agents/workflows/`.                                           |
| `.claude/agents → ../.agents/agents`      | Claude Code reads subagents from `.claude/agents/` (`.md` files with YAML frontmatter).              |
| `.augment/agents → ../.agents/agents`     | Auggie reads subagents from `.augment/agents/` (`.md` files).                                       |
| `.codex/agents → ../.agents/agents`       | Codex reads subagents from `.codex/agents/` (`.toml` files).                                        |

Antigravity and Codex do not require any symlinks for `AGENTS.md` or `.agents/skills/` – they read them natively. Codex does not support its own slash commands (deprecated in version 0.117.0 in favor of skills).

Commands to create the links are (the path to the linked folder or file is always given relative to the link's location):

```sh
ln -s AGENTS.md CLAUDE.md
ln -s ../.agents/skills .claude/skills
ln -s ../.agents/rules .augment/rules
ln -s .agents/mcp_config.json .mcp.json
ln -s ../.agents/commands .augment/commands
ln -s ../.agents/commands .claude/commands
ln -s commands .agents/workflows
ln -s ../.agents/agents .claude/agents
ln -s ../.agents/agents .augment/agents
ln -s ../.agents/agents .codex/agents
```

### Rules

Workspace rules are in `.agents/rules/*.md` (Markdown with optional YAML frontmatter). Discovery by agent:

| Agent        | Discovery                                                                             |
| ------------ | ------------------------------------------------------------------------------------- |
| Antigravity  | natively reads `.agents/rules/*.md`                                                   |
| Augment Code | via symlink `.augment/rules → ../.agents/rules`                                       |
| Claude Code  | has no rule folder; imports from `AGENTS.md` via `@.agents/rules/<file>.md` as needed  |
| Codex        | has no rules folder; references `.agents/rules/<file>.md` from `AGENTS.md` as needed   |

Augment Code and Antigravity use **different frontmatter keys**, but each ignores unknown keys – so files work in both from a single location. Augment Code distinguishes `type: always_apply|agent_requested|manual`; Antigravity `trigger: always_on|glob (+ globs:)|model_decision|manual`. For `agent_requested` / `model_decision`, the agent decides on activation based on `description:`. Both frontmatter blocks can be combined in a single file.

An example of a compatible file:

```markdown
---
description: Odoo ORM and Python conventions for extra-addons
type: agent_requested
trigger: model_decision
---

# Odoo ORM conventions

- Add fields of extended models via `_inherit`, not via override.
- …
```

### Subagents

Shared subagents are defined in `.agents/agents/`. Since Claude Code and Auggie use **Markdown** (`.md`) and Codex uses **TOML** (`.toml`), the directory contains both formats for each subagent. Each agent takes the file format it knows during discovery and ignores the others.

| Subagent        | Files                                    | Description                                                     |
| --------------- | ---------------------------------------- | --------------------------------------------------------------- |
| `code-reviewer` | `code-reviewer.md` + `code-reviewer.toml` | Code review focused on Odoo conventions, security, and style     |

**Formats:**

- **`.md` (Claude Code, Auggie):** YAML frontmatter with fields `name` (Claude), `description` (both), `color` (Auggie), optionally `tools` and `model` (Claude). The file body is the system prompt.
- **`.toml` (Codex):** Fields `name`, `description`, `developer_instructions` (system prompt), optionally `model`, `sandbox_mode`.

**Antigravity** currently does not support file-defined subagents (only dynamic creation via the `define_subagent` tool at runtime). If Google officially introduces this, we will add it.

**Augment Code VS Code extension** has subagent support in Beta – it works through the same `.augment/agents/` directory as Auggie.

### What remains agent-specific

The following files and folders cannot be unified into `.agents/` or symlinked (different formats, naming or discovery mechanisms). Details for each item are in the [Augment Code](#augment-code), [Claude Code](#claude-code), [Antigravity](#antigravity) and [Codex](#codex) sections below.

| Agent            | Specific artifacts (not covered by the unified structure)                                                                                                                                             |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Augment Code** | `.augment/settings.json` (+ `.local`), `.augmentignore`; **MCP via UI**                                                                                                                               |
| **Claude Code**  | `CLAUDE.local.md` (private, gitignored), `.claude/settings.json` (+ `.local`; permissions/env/hooks)                                                                                                  |
| **Antigravity**  | `GEMINI.md` (alternative workspace context), `.agents/hooks.json` (lifecycle hooks)                                                                                                                  |
| **Codex**        | `AGENTS.override.md` (per-dir override), `.codex/config.toml` (model/sandbox/MCP/hooks), `.codex/hooks.json`, `.codex/rules/*.rules` (sandbox allow/block), `.agents/plugins/` + `plugins/` (plugins) |

**MCP**: shared JSON configuration is in `.agents/mcp_config.json` (both Claude Code and Antigravity via the `.mcp.json` symlink above). Augment Code configures MCP via the UI. Codex uses TOML – `[mcp_servers]` in `.codex/config.toml` – sharing via symlink is not possible.

**Hooks** (lifecycle interceptors – `PreToolUse`, `PostToolUse`, `Stop`, etc.):

| Agent           | File (project-level)                                                 | Format                                                              |
| --------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Antigravity** | `.agents/hooks.json`                                                 | `{ "hooks": { "PreToolUse": [{ "matcher": "…", "hooks": […] }] } }` |
| **Claude Code** | `.claude/settings.json` (or `.claude/settings.local.json`)           | `{ "hooks": { "PreToolUse": [{ "matcher": "…", "hooks": […] }] } }` |
| **Codex**       | `.codex/hooks.json` **or** inline `[hooks]` in `.codex/config.toml`  | JSON (same schema) / TOML: `[[hooks.PreToolUse]]`                   |
| **Auggie**      | `.augment/settings.json` (or `.augment/settings.local.json`)         | `{ "hooks": { "PreToolUse": [{ "matcher": "…", "hooks": […] }] } }` |

The JSON schema of hooks is almost identical between Antigravity, Claude Code, and Auggie – only the file location differs. Codex also offers an equivalent TOML notation; if both `hooks.json` and inline `[hooks]` exist in the same layer, Codex loads both and warns – one per layer is recommended.

### Notes

- **Windows**: symlinks in git work reliably on Linux/macOS. Devcontainer runs on Linux, so the issue is eliminated. With a native Windows clone, it is necessary to have `git config core.symlinks=true` and the user must have `SeCreateSymbolicLinkPrivilege` permission:
  - Set `git config --global core.symlinks true` - this only needs to be done once globally, at the beginning.
  - Turn on "Settings" (`Win + I`) > "System" > "Advanced" > "For developers" - this only needs to be done once globally, at the beginning.
- **Local overrides**: `*.local.md`, `*.local.json`, `*.local.toml` files are in `.gitignore` – use them for your own notes/settings that do not belong in the repo.
- **Skill format**: each skill is a directory `.agents/skills/<name>/SKILL.md` with YAML frontmatter `name` and `description` (a common requirement of Augment, Codex, and Antigravity).

The sections below describe the installation, login, and also all configuration options of individual agents.

## Augment Code

### Installation

The VS Code extension is installed **automatically** in the devcontainer using `.devcontainer/devcontainer.json` > `"customizations"` > `"vscode"` > `"extensions"` > `"augment.vscode-augment"`.

The CLI (`auggie`) is installed **automatically** in the devcontainer using `.devcontainer/post-create.sh` > `# install Auggie CLI (Augment Code)`.

### Login

On [app.augmentcode.com](https://app.augmentcode.com/) it is necessary to create a personal account. In case of private use, pay for one of the plans. **In case of work use**, request adding your personal user to [company users](https://app.augmentcode.com/account/team).

When logging in to `auggie`, use the personal account created on [app.augmentcode.com](https://app.augmentcode.com/).

On the company account, it is possible to track [credits consumed by individual users](https://app.augmentcode.com/account/analytics).

### Configuration

Augment Code can be configured as follows:

| File / folder                     | What it is used for                                      | Note                                                                                                                                                                                                               |
| --------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `.augment/rules/*.md`             | Project rules                                            | Rules in `.augment/rules` are Markdown files; in VS Code they can be **always_apply**, **manual**, or **agent_requested**. Workspace rules are intended for committing to the repository. ([docs.augmentcode.com][augment-1]) |
| `AGENTS.md`                       | Hierarchical rules                                       | Can be in the root as well as subdirectories; Augment looks for it in the current and parent directories when working with a file. ([docs.augmentcode.com][augment-2], [agents.md](https://agents.md/))                          |
| `CLAUDE.md`                       | Hierarchical rules compatible with Claude Code           | Works similarly to `AGENTS.md`; only `AGENTS.md` and `CLAUDE.md` appear hierarchically, not `.augment/rules` in subdirectories. ([docs.augmentcode.com][augment-2])                                                     |
| `.augment/skills/<name>/SKILL.md` | Skills                                                   | Each skill is its own directory with `SKILL.md`; it must have YAML frontmatter `name` and `description`. ([docs.augmentcode.com][augment-3])                                                                                    |
| `.claude/skills/<name>/SKILL.md`  | Skills compatible with Claude Code                       | Augment can discover them as workspace skills. ([docs.augmentcode.com][augment-3])                                                                                                                                      |
| `.agents/skills/<name>/SKILL.md`  | Standard agentskills.io format                           | Also supported as workspace skills. ([docs.augmentcode.com][augment-3])                                                                                                                                             |
| `.augment/commands/*.md`          | Custom slash commands                                    | They appear in the `/` autocomplete menu in chat; e.g., `.augment/commands/security-review.md` → `/security-review`. ([docs.augmentcode.com][augment-4])                                                                     |
| `.augment/commands/foo/bar.md`    | Namespaced commands                                      | E.g., `.augment/commands/frontend/component.md` → `/frontend:component`. ([docs.augmentcode.com][augment-4])                                                                                                           |
| `.claude/commands/*.md`           | Claude-compatible commands                               | Augment can use them as compatible commands. ([docs.augmentcode.com][augment-4])                                                                                                                                  |
| `.cursor/commands/*.md`           | Cursor-compatible commands                               | Supported in VS Code custom commands locations. ([docs.augmentcode.com][augment-4])                                                                                                                                  |
| `.augmentignore`                  | What should not be indexed                               | Works similarly to `.gitignore`; Augment indexes workspace except files from `.gitignore` and `.augmentignore`. You can also use `!` to include gitignored files. ([docs.augmentcode.com][augment-5])                  |

[augment-1]: https://docs.augmentcode.com/setup-augment/guidelines "Rules & Guidelines for Agent and Chat - Augment"
[augment-2]: https://docs.augmentcode.com/cli/rules "Rules & Guidelines - Augment"
[augment-3]: https://docs.augmentcode.com/using-augment/skills "Skills - Augment"
[augment-4]: https://docs.augmentcode.com/using-augment/custom-commands "Custom Commands - Augment"
[augment-5]: https://docs.augmentcode.com/setup-augment/workspace-indexing "Index your workspace - Augment"

In the directory structure, it looks like this:

```
repo/
  .augmentignore
  AGENTS.md
  CLAUDE.md

  .augment/
    rules/
      general.md
      frontend/react.md
    skills/
      deploy-guide/
        SKILL.md
    commands/
      security-review.md
      frontend/
        component.md
    settings.json          # rather Auggie/CLI and advanced shared settings
    settings.local.json    # local, do not commit
    agents/                # subagents, mainly Auggie/CLI
      code-review.md

  .claude/
    skills/
      some-skill/
        SKILL.md
    commands/
      some-command.md

  .agents/
    skills/
      some-standard-skill/
        SKILL.md

  .cursor/
    commands/
      some-cursor-compatible-command.md
```

## Claude Code

### Installation

The VS Code extension is installed **automatically** in the devcontainer using `.devcontainer/devcontainer.json` > `"customizations"` > `"vscode"` > `"extensions"` > `"anthropic.claude-code"`.

The CLI (`claude`) is installed **automatically** in the devcontainer using `.devcontainer/post-create.sh` > `# install Claude Code CLI`.

### Login

On [platform.claude.com](https://platform.claude.com/) it is necessary to create a personal account. In case of private use, pay for one of the plans. **In case of work use**, request adding your personal user to [company users](https://platform.claude.com/settings/members) (with role `Claude Code` or `Developer`).

When logging in to `claude` > `/login`, choose `2. Anthropic Console account · API usage billing` and use the personal account created on [platform.claude.com](https://platform.claude.com/).

On the company account, it is possible to track [credits consumed by individual users](https://platform.claude.com/cost?group_by=key_id).

### Configuration

Claude Code can be configured as follows:

| File / folder                     | What it is used for                                                                            | Note                                                                                                                                                       |
| --------------------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE.md`                       | Main project instructions: architecture, build/test commands, coding conventions, workflow.    | Project `CLAUDE.md` can be in the root or as `.claude/CLAUDE.md`; Claude loads it as persistent instructions. ([Claude API Docs][claude-1])                 |
| `.claude/CLAUDE.md`               | Alternative location for project instructions.                                                 | Same purpose as root `CLAUDE.md`, just stored in `.claude/`. ([Claude API Docs][claude-1])                                                                 |
| `CLAUDE.local.md`                 | Your private project notes/preferences.                                                        | Claude loads it along with `CLAUDE.md`; it should be in `.gitignore`. ([Claude API Docs][claude-1])                                                        |
| `.claude/rules/*.md`              | Modular rules, e.g., coding style, testing, security, API rules.                               | Rules can be split into subdirectories and can be path-scoped. ([Claude API Docs][claude-1])                                                               |
| `.claude/settings.json`           | Shared project settings: permissions, env, hooks, plugins, exclusion of sensitive files.       | Shared project settings stored in the repository. ([Claude API Docs][claude-2])                                                                            |
| `.claude/settings.local.json`     | Local overrides for a specific project.                                                       | Local settings, Claude Code sets them as gitignored upon creation. ([Claude API Docs][claude-2])                                                           |
| `.claude/skills/<skill>/SKILL.md` | Skills: repeatable procedures, checklists, workflows and specialized knowledge.                  | Skills can be called via `/skill-name`; both `.claude/commands/*.md` and `.claude/skills/<name>/SKILL.md` create a slash command. ([Claude API Docs][claude-3]) |
| `.claude/commands/*.md`           | Legacy custom slash commands.                                                                  | They still work, but custom commands were merged with skills; it is better to put new things into skills. ([Claude API Docs][claude-3])                    |
| `.claude/agents/*.md`             | Custom subagents with an independent prompt, tool access and permissions.                       | Project subagents live in `.claude/agents/`; they are used for specialized tasks and isolated context. ([Claude API Docs][claude-4])                       |
| `.mcp.json`                       | Project MCP servers shared with the team.                                                       | Project-scoped MCP configuration is saved in `.mcp.json` in the project root. ([Claude API Docs][claude-5])                                                   |
| `.gitignore`                      | Protection against committing local Claude files and sensitive data.                             | Use `permissions.deny` in `.claude/settings.json` as well to block Claude Code access to sensitive files. ([Claude API Docs][claude-2])                     |

[claude-1]: https://docs.anthropic.com/en/docs/claude-code/memory "How Claude remembers your project - Claude Code Docs"
[claude-2]: https://docs.anthropic.com/en/docs/claude-code/settings "Claude Code settings - Claude Code Docs"
[claude-3]: https://docs.anthropic.com/en/docs/claude-code/skills "Extend Claude with skills - Claude Code Docs"
[claude-4]: https://docs.anthropic.com/en/docs/claude-code/sub-agents "Create custom subagents - Claude Code Docs"
[claude-5]: https://docs.anthropic.com/en/docs/claude-code/mcp "Connect Claude Code to tools via MCP - Claude Code Docs"

In the directory structure, it looks like this:

```
repo/
  CLAUDE.md
  CLAUDE.local.md          # local, do not commit
  .mcp.json                # shared MCP servers

  .claude/
    CLAUDE.md              # alternative to root CLAUDE.md
    settings.json          # shared project settings
    settings.local.json    # local project settings, do not commit

    rules/
      general.md
      frontend/react.md
      backend/api.md

    skills/
      deploy-staging/
        SKILL.md
        scripts/
        examples.md

    commands/              # legacy; still works
      review.md
      fix-issue.md

    agents/
      code-reviewer.md
      debugger.md
      security-auditor.md
```

## Antigravity

### Installation

The VS Code extension is not installed (does not exist).

The CLI (`agy`) is installed **automatically** in the devcontainer using `.devcontainer/post-create.sh` > `# install Antigravity CLI`.

### Login

On [accounts.google.com](https://accounts.google.com) it is necessary to create a google account - i.e., having a regular personal google account is sufficient. **Antigravity can also be used for free** via your personal google account, but you have to expect limits, availability based on capacity, or pay for one of the [plans](https://antigravity.google/pricing). **In case of work use**, request adding your personal user to [company users](https://console.cloud.google.com/iam-admin/iam).

When logging in to `agy`, choose `2. Use a Google Cloud project`, use the personal account created on [accounts.google.com](https://accounts.google.com) and enter `project-605967c9-39ce-4929-b5b` as the project ID.

On the company account, it is possible to track the [current price (consumption) for services used](https://console.cloud.google.com/billing/reports).

#### Initial setup of a company account

For the google account you decide to use as a company account, in the [Google Cloud Console](https://console.cloud.google.com/) you need to:

- [Create a project](https://console.cloud.google.com/projectcreate), e.g., `Run AI`.
- [Add a billing account to it](https://console.cloud.google.com/billing), e.g., `Run billing`.
- Enable `Agent platform API`: [console](https://console.cloud.google.com/apis/dashboard?cloudshell=true) (icon `|>_|` at top right) > `gcloud services enable aiplatform.googleapis.com`

### Configuration

Antigravity can be configured as follows:

| File / folder                     | What it is used for                                                                       | Note                                                                                                                                                                                                                                |
| --------------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GEMINI.md`                       | Workspace context / general project instructions for Gemini/Antigravity CLI.               | Antigravity CLI supports workspace context files `GEMINI.md` and `AGENTS.md`. ([Google Antigravity][agy-1])                                                                                                                         |
| `AGENTS.md`                       | Tool-agnostic project instructions for coding agents.                                     | Antigravity CLI reads `AGENTS.md` from the active workspace; AGENTS.md is a general open format for agent instructions. ([Google Antigravity][agy-1], [agents.md](https://agents.md/))                                               |
| `.agents/agents.md`               | Definition of team/personas, e.g., PM, engineer, QA, DevOps.                              | Google codelab uses `.agents/agents.md` for centralized definition of specialized agent personas. ([Google Codelabs][agy-2])                                                                                                |
| `.agents/rules/*.md`              | Workspace rules: project rules for code style, architecture, testing, security.           | Workspace rules live in `.agents/rules/`; global rules are in `~/.gemini/GEMINI.md`. ([Google Antigravity][agy-3])                                                                                                                   |
| `.agents/skills/<skill>/SKILL.md` | Project skills: repeatable abilities/workflows packaged as a directory with `SKILL.md`.   | Antigravity currently defaults to `.agents/skills`; a skill is a folder containing `SKILL.md`. ([Google Antigravity][agy-4], [medium][agy-5])                                                                                           |
| `.agents/workflows/*.md`          | Workspace workflows / custom slash commands.                                              | Workflows are stored Markdown files and run via `/workflow-name`; workspace workflows live in `.agents/workflows/`. ([Google Antigravity][agy-3])                                                                             |
| `.agents/hooks.json`              | Hooks: local shell scripts executed at specified points of the agent execution cycle.      | Hooks are configured in `hooks.json` in the customization directory, e.g., `.agents/` in the workspace. ([Google Antigravity][agy-6])                                                                                                         |
| `.agents/mcp_config.json`         | Project MCP configuration, mainly for Antigravity CLI / workspace setup.                  | Antigravity uses a standalone `mcp_config.json`; IDE documentation mentions global `~/.gemini/antigravity/mcp_config.json`, while CLI/workspace guides also mention project-level MCP under `.agents/`. ([Google Antigravity][agy-7]) |

[agy-1]: https://antigravity.google/docs/gcli-migration "Migrating from Gemini CLI"
[agy-2]: https://codelabs.developers.google.com/autonomous-ai-developer-pipelines-antigravity "Build Autonomous Developer Pipelines using agents.md and skills.md in Antigravity  |  Google Codelabs"
[agy-3]: https://antigravity.google/docs/rules-workflows "Google Antigravity - Rules"
[agy-4]: https://antigravity.google/docs/skills "Agent Skills"
[agy-5]: https://medium.com/google-cloud/tutorial-getting-started-with-antigravity-skills-864041811e0d "Tutorial : Getting Started with Google Antigravity Skills"
[agy-6]: https://antigravity.google/docs/hooks "Hooks"
[agy-7]: https://antigravity.google/docs/mcp "Antigravity Editor: MCP Integration"

In the directory structure, it looks like this:

```
repo/
  GEMINI.md
  AGENTS.md

  .agents/
    agents.md

    rules/
      code-style.md
      testing.md
      security.md

    skills/
      deploy-staging/
        SKILL.md
        scripts/
        resources/
        examples/

    workflows/
      review.md
      fix-issue.md
      startcycle.md

    hooks.json
    mcp_config.json          # mainly Antigravity CLI / project MCP; IDE MCP is often global
```

## Codex

### Installation

The VS Code extension is installed **automatically** in the devcontainer using `.devcontainer/devcontainer.json` > `"customizations"` > `"vscode"` > `"extensions"` > `"openai.chatgpt"`.

The CLI (`codex`) is installed **automatically** in the devcontainer using `.devcontainer/post-create.sh` > `# install Codex CLI`.

### Login

On [chatgpt.com](https://chatgpt.com/) it is necessary to create a personal account. **Codex can also be used for free** via your personal GPT account, but you have to expect limits, availability based on capacity, or pay for one of the [plans](https://chatgpt.com/#pricing). **In case of work use**, request adding your personal user to [company users](https://chatgpt.com/admin/members).

When logging in to `codex`, choose `1. Sign in with ChatGPT` (or `2. Sign in with Device Code` if the first option does not work), use the personal account created on [chatgpt.com](https://chatgpt.com/) and when logging in in the browser select `Run Development's Workspace`.

On the company account, it is possible to track [credits consumed by individual users](https://chatgpt.com/admin/usage).

### Configuration

| File / folder                               | What it is used for                                                                                                       | Note                                                                                                                                                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `AGENTS.md`                                 | Main project instructions for Codex: build/test commands, architecture, conventions, what “done” means.                   | Codex reads `AGENTS.md` before working; looks for it from root to the current directory in the project and composes instructions hierarchically. ([OpenAI Developers][codex-1])                       |
| `AGENTS.override.md`                        | Optional override for instructions in the given directory.                                                                | Takes precedence over `AGENTS.md` during discovery; Codex takes at most one instruction file per directory. ([OpenAI Developers][codex-1])                                                             |
| `*/AGENTS.md`                               | Instructions for a specific subdirectory, module or service.                                                              | Files closer to the current workspace are added later, so they can override more general rules from the root. ([OpenAI Developers][codex-1])                                                             |
| `.codex/config.toml`                        | Project settings of Codex: model, approvals, sandbox, MCP servers, hooks inline, skill overrides, subagent settings.      | Codex uses `~/.codex/config.toml` for user config and `.codex/config.toml` for project overrides; loads project `.codex/` layers only in trusted projects. ([OpenAI Developers][codex-2])              |
| `.codex/hooks.json`                         | Lifecycle hooks for the project, e.g., prompt validation, logging, checks after a tool call or upon ending a turn.        | Codex looks for hooks next to active config layers as `hooks.json` or inline `[hooks]` in `config.toml`; project hooks are loaded only in trusted projects. ([OpenAI Developers][codex-3])              |
| `.codex/rules/*.rules`                      | Rules for allowing/prompting/blocking commands outside the sandbox.                                                       | `.rules` are experimental command rules; Codex scans `rules/` next to the active config layer, including `<repo>/.codex/rules/`. ([OpenAI Developers][codex-4])                                          |
| `.codex/agents/*.toml`                      | Project custom subagents / custom agents with their own model, sandbox, MCP, skills and developer instructions.           | Project custom agents are standalone TOML files in `.codex/agents/`; required fields are `name`, `description`, `developer_instructions`. ([OpenAI Developers][codex-5])                                |
| `.agents/skills/<skill>/SKILL.md`           | Repo skills: repeatable workflows, runbooks, checklists and specialized procedures.                                       | Codex reads repo skills from `.agents/skills` from the current directory to the repository root; a skill is a directory with `SKILL.md` and optional `scripts/`, `references/`, `assets/`. ([OpenAI Developers][codex-6]) |
| `.agents/plugins/marketplace.json`          | Repo marketplace plugin catalog for team/project.                                                                         | Repo-scoped marketplace can be saved to `$REPO_ROOT/.agents/plugins/marketplace.json`; items point to plugin folders, often under `./plugins/`. ([OpenAI Developers][codex-7])                         |
| `plugins/<plugin>/.codex-plugin/plugin.json` | Codex plugin manifest.                                                                                                    | A plugin has a required manifest `.codex-plugin/plugin.json`; it can package skills, MCP servers, hooks, app integrations and assets. ([OpenAI Developers][codex-7])                                   |
| `plugins/<plugin>/skills/<skill>/SKILL.md`  | Skills packaged in a plugin.                                                                                              | The plugin manifest can point to the `skills` folder and thereby distribute one or more skills. ([OpenAI Developers][codex-7])                                                                         |
| `plugins/<plugin>/hooks/hooks.json`         | Hooks packaged in a plugin.                                                                                               | A plugin can contain lifecycle hooks; before execution, the user must review and trust them. ([OpenAI Developers][codex-7])                                                                            |
| `plugins/<plugin>/.mcp.json`                | MCP servers packaged in a plugin.                                                                                         | In a normal project, MCP is configured via `.codex/config.toml`; a plugin can have its own `.mcp.json` pointed to by the manifest. ([OpenAI Developers][codex-8])                                      |
| `plugins/<plugin>/.app.json`                | App / connector mappings for a plugin.                                                                                    | The plugin structure can contain `.app.json` for app or connector integrations. ([OpenAI Developers][codex-7])                                                                                         |

[codex-1]: https://developers.openai.com/codex/guides/agents-md "Custom instructions with AGENTS.md – Codex | OpenAI Developers"
[codex-2]: https://developers.openai.com/codex/config-basic "Config basics – Codex | OpenAI Developers"
[codex-3]: https://developers.openai.com/codex/hooks "Hooks – Codex | OpenAI Developers"
[codex-4]: https://developers.openai.com/codex/rules "Rules – Codex | OpenAI Developers"
[codex-5]: https://developers.openai.com/codex/subagents "Subagents – Codex | OpenAI Developers"
[codex-6]: https://developers.openai.com/codex/skills "Agent Skills – Codex | OpenAI Developers"
[codex-7]: https://developers.openai.com/codex/plugins/build "Build plugins – Codex | OpenAI Developers"
[codex-8]: https://developers.openai.com/codex/mcp "Model Context Protocol – Codex | OpenAI Developers"

In the directory structure, it looks like this:

```
repo/
  AGENTS.md
  AGENTS.override.md          # optional, temporary override
  services/
    api/
      AGENTS.md               # optional, specific to the subdirectory

  .codex/
    config.toml               # project Codex config; only trusted projects
    hooks.json
    rules/
      default.rules
    agents/
      code-reviewer.toml
      explorer.toml

  .agents/
    skills/
      deploy-staging/
        SKILL.md
        scripts/
        references/
        assets/
      review-changes/
        SKILL.md
    plugins/
      marketplace.json

  plugins/
    my-plugin/
      .codex-plugin/
        plugin.json
      skills/
        my-skill/
          SKILL.md
      hooks/
        hooks.json
      .mcp.json
      .app.json
      assets/
```
