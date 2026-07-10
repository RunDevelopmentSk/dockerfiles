---
type: always_apply
trigger: always_on
---

# Instructions for AI agents

This file is a **shared source of truth** for all AI agents in the project
(Auggie, Claude Code, Antigravity, Codex). Auggie, Antigravity
and Codex read it natively; Claude Code reads it via the symlink `CLAUDE.md → AGENTS.md`.

Configuration details of individual agents and the unified structure are in
[`docs/ai-agents.md`](docs/ai-agents.md).

Before working, check:

- `.agents/rules/*.md` – modular workspace rules

## Always applicable cross-cutting rules

- @.agents/rules/run.language-policy.md
- @.agents/rules/run.secret-safety.md

# General Project Description

The current project contains Dockerfile files of various Docker images that we use in other projects as:

- basis for .devcontainer in the VS Code environment. These are the files/images whose names start with `dev-` or `fanj`.
- basis for production containers. These are the files/images whose names start with `prod-`.

These images are published and shared on https://hub.docker.com/u/developmentrunsk. Individual Dockerfile files are independent, although sometimes quite similar, as they only update the Docker image for a newer version of the given technology. The naming convention is `Dockerfile.<image-label>_<image-tag>`, for example:

- `Dockerfile.dev-odoo_17.0-20240812`
- `Dockerfile.fajnlamp_7.3`
- `Dockerfile.prod-odoo_19.0-20251222`
