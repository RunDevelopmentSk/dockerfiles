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

## General description

The current project contains Dockerfile files of various Docker images that we use in other projects as:

- basis for .devcontainer in the VS Code environment. These are the files/images whose names start with `dev-` or `fanj`.
- basis for production containers. These are the files/images whose names start with `prod-`.

These images are published and shared on https://hub.docker.com/u/developmentrunsk. All build sources (the `Dockerfile.*` files and the `.sh` scripts) live in the `images/` directory, keeping the repository root reserved for documentation and tooling configuration. Individual Dockerfile files are independent, although sometimes quite similar, as they only update the Docker image for a newer version of the given technology. The naming convention is `images/Dockerfile.<image-label>_<image-tag>`, for example:

- `images/Dockerfile.dev-odoo_17.0-20240812`
- `images/Dockerfile.fajnlamp_7.3`
- `images/Dockerfile.prod-odoo_19.0-20251222`
