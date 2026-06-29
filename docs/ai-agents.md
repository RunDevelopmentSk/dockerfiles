# Programovací AI agenti

V devcontaineri sú dostupní nasledovní programovací AI agenti:

- **Augment Code** (VS Code rozšírenie) a/alebo `auggie` (Auggie CLI)
- **Claude Code** (VS Code rozšírenie) a/alebo `claude` (Claude Code CLI)
- `agy` (**Antigravity** CLI)
- **Codex** (VS Code rozšírenie) a/alebo `codex` (Codex CLI)

Detaily použitia jednotlivých AI agentov sú popísané tu nižšie.

## Unifikovaná konfigurácia (`.agents/` + `AGENTS.md`)

Pre všetkých agentov sa používa **jeden zdroj pravdy** pre projektové inštrukcie, workspace rules a skills naprieč všetkými agentmi:

- [`AGENTS.md`](../AGENTS.md) v koreňovom adresári – hlavné projektové inštrukcie v štandardnom [agents.md](https://agents.md/) formáte.
- [`.agents/rules/`](../.agents/rules/) – modulárne workspace pravidlá.
- [`.agents/skills/`](../.agents/skills/) – cross-tool skills v štandardnom [agentskills.io](https://agentskills.io/) formáte.
- [`.agents/commands/`](../.agents/commands/) – custom slash commands zdieľané naprieč agentmi; každý súbor `<name>.md` vytvára `/name` command.
- [`.agents/agents/`](../.agents/agents/) – subagenti zdieľaní naprieč agentmi; `.md` pre Claude Code a Auggie, `.toml` pre Codex (každý agent si zoberie formát, ktorý pozná).

Tam, kde agent štandard `.agents/` + `AGENTS.md` nepodporuje natívne, je to vyriešené **symbolickými linkmi commitnutými do repa**:

| Symlink                                   | Dôvod                                                                                             |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `CLAUDE.md → AGENTS.md`                   | Claude Code číta `CLAUDE.md`.                                                                     |
| `.claude/skills → ../.agents/skills`      | Claude Code číta skills z `.claude/skills/`.                                                      |
| `.augment/rules → ../.agents/rules`       | Augment Code číta workspace rules z `.augment/rules/`.                                            |
| `.mcp.json → .agents/mcp_config.json`     | Claude Code číta MCP konfiguráciu z `.mcp.json` v roote; Antigravity z `.agents/mcp_config.json`. |
| `.augment/commands → ../.agents/commands` | Augment Code číta slash commands z `.augment/commands/`.                                          |
| `.claude/commands → ../.agents/commands`  | Claude Code číta slash commands z `.claude/commands/`.                                            |
| `.agents/workflows → commands`            | Antigravity číta slash commands z `.agents/workflows/`.                                           |
| `.claude/agents → ../.agents/agents`      | Claude Code číta subagentov z `.claude/agents/` (`.md` súbory s YAML frontmatterom).              |
| `.augment/agents → ../.agents/agents`     | Auggie číta subagentov z `.augment/agents/` (`.md` súbory).                                       |
| `.codex/agents → ../.agents/agents`       | Codex číta subagentov z `.codex/agents/` (`.toml` súbory).                                        |

Antigravity a Codex nevyžadujú žiadne symlinky pre `AGENTS.md` ani `.agents/skills/` – čítajú ich natívne. Codex vlastné slash commands nepodporuje (zrušené vo verzii 0.117.0 v prospech skills).

Príkazy na vytvorenie linkov sú (cesta k linovanému priečinku alebo súboru je vždy uvedená relátivne voči polohe linku):

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

Workspace rules sú v `.agents/rules/*.md` (Markdown s voliteľným YAML frontmatterom). Discovery podľa agenta:

| Agent        | Discovery                                                                             |
| ------------ | ------------------------------------------------------------------------------------- |
| Antigravity  | natívne číta `.agents/rules/*.md`                                                     |
| Augment Code | cez symlink `.augment/rules → ../.agents/rules`                                       |
| Claude Code  | nemá rule priečinok; podľa potreby `@.agents/rules/<file>.md` import z `AGENTS.md`    |
| Codex        | nemá rules priečinok; podľa potreby `.agents/rules/<file>.md` odvolanie z `AGENTS.md` |

Augment Code a Antigravity používajú **rôzne frontmatter kľúče**, ale každý ignoruje neznáme kľúče – súbory teda fungujú v oboch z jedného umiestnenia. Augment Code rozlišuje `type: always_apply|agent_requested|manual`; Antigravity `trigger: always_on|glob (+ globs:)|model_decision|manual`. Pre `agent_requested` / `model_decision` rozhoduje agent o aktivácii podľa `description:`. Oba frontmatter bloky sa dajú kombinovať v jednom súbore.

Príklad kompatibilného súboru:

```markdown
---
description: Odoo ORM a Python konvencie pre extra-addons
type: agent_requested
trigger: model_decision
---

# Odoo ORM konvencie

- Polia rozširovaných modelov pridávaj cez `_inherit`, nie cez override.
- …
```

### Subagenti

Zdieľaní subagentti sú definovamí v `.agents/agents/`. Keďže Claude Code a Auggie používajú **Markdown** (`.md`) a Codex **TOML** (`.toml`), adresár obsahuje oba formáty pre každého subagenta. Každý agent si pri discovery zoberie súbory formátu, ktorý pozná; iné ignoruje.

| Subagent        | Súbory                                    | Popis                                                     |
| --------------- | ----------------------------------------- | --------------------------------------------------------- |
| `code-reviewer` | `code-reviewer.md` + `code-reviewer.toml` | Code review zameraný na Odoo konvencie, bezpečnosť a štýl |

**Formáty:**

- **`.md` (Claude Code, Auggie):** YAML frontmatter s poliami `name` (Claude), `description` (obaja), `color` (Auggie), voliteľne `tools` a `model` (Claude). Telo súboru je systémový prompt.
- **`.toml` (Codex):** Polia `name`, `description`, `developer_instructions` (systémový prompt), voliteľne `model`, `sandbox_mode`.

**Antigravity** v súčasnosti nepodporuje súborovo definovaných subagentov (len dynamické vytváranie cez `define_subagent` tool za behu). Ak to Google officiálne zavedie, doplníme.

**Augment Code VS Code extension** má podporu subagentov v Beta – funguje cez rovnaký `.augment/agents/` adresár ako Auggie.

### Čo zostane agent-špecifické

Nasledujúce súbory a priečinky sa nedajú zjednotiť do `.agents/` ani symlinkovať (rôzne formáty, naming alebo discovery mechanizmy). Detaily ku každej položke sú v sekciách [Augment Code](#augment-code), [Claude Code](#claude-code), [Antigravity](#antigravity) a [Codex](#codex) nižšie.

| Agent            | Špecifické artefakty (nepokryté unifikovanou štruktúrou)                                                                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Augment Code** | `.augment/settings.json` (+ `.local`), `.augmentignore`; **MCP cez UI**                                                                                                                               |
| **Claude Code**  | `CLAUDE.local.md` (privátne, gitignored), `.claude/settings.json` (+ `.local`; permissions/env/hooks)                                                                                                 |
| **Antigravity**  | `GEMINI.md` (alternatívny workspace context), `.agents/hooks.json` (lifecycle hooks)                                                                                                                  |
| **Codex**        | `AGENTS.override.md` (per-dir override), `.codex/config.toml` (model/sandbox/MCP/hooks), `.codex/hooks.json`, `.codex/rules/*.rules` (sandbox allow/block), `.agents/plugins/` + `plugins/` (pluginy) |

**MCP**: zdieľaná JSON konfigurácia je v `.agents/mcp_config.json` (Claude Code aj Antigravity cez symlink `.mcp.json` vyššie). Augment Code MCP konfiguruje cez UI. Codex používa TOML – `[mcp_servers]` v `.codex/config.toml` – zdieľanie cez symlink nie je možné.

**Hooks** (lifecycle interceptory – `PreToolUse`, `PostToolUse`, `Stop` atď.):

| Agent           | Súbor (projekt-level)                                                 | Formát                                                              |
| --------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Antigravity** | `.agents/hooks.json`                                                  | `{ "hooks": { "PreToolUse": [{ "matcher": "…", "hooks": […] }] } }` |
| **Claude Code** | `.claude/settings.json` (alebo `.claude/settings.local.json`)         | `{ "hooks": { "PreToolUse": [{ "matcher": "…", "hooks": […] }] } }` |
| **Codex**       | `.codex/hooks.json` **alebo** inline `[hooks]` v `.codex/config.toml` | JSON (rovnaká schéma) / TOML: `[[hooks.PreToolUse]]`                |
| **Auggie**      | `.augment/settings.json` (alebo `.augment/settings.local.json`)       | `{ "hooks": { "PreToolUse": [{ "matcher": "…", "hooks": […] }] } }` |

JSON schéma hooks je takmer identická medzi Antigravity, Claude Code a Auggie – líši sa iba umiestnenie súboru. Codex navyše ponúka ekvivalentný TOML zápis; ak existuje `hooks.json` aj inline `[hooks]` v tej istej vrstve, Codex načíta oboje a upozorní – odporúča sa jedno na vrstvu.

### Poznámky

- **Windows**: symlinky v gite fungujú spoľahlivo na Linuxe/macOS. Devcontainer beží na Linuxe, takže problém odpadá. Pri natívnom Windows klone je potrebné mať `git config core.symlinks=true` a používateľ právo `SeCreateSymbolicLinkPrivilege`:
  - Nastaviť `git config --global core.symlinks true` - toto stačí urobiť raz globálne, na začiatku.
  - Zapnúť "Settings" (`Win + I`) > "System" > "Advanced" > "For developers" - toto stačí urobiť raz globálne, na začiatku.
- **Lokálne overrides**: súbory `*.local.md`, `*.local.json`, `*.local.toml` sú v `.gitignore` – použi ich na vlastné poznámky/nastavenia, ktoré nepatria do repa.
- **Skill formát**: každý skill je adresár `.agents/skills/<name>/SKILL.md` s YAML frontmatterom `name` a `description` (spoločná požiadavka Augmentu, Codexu aj Antigravity).

Sekcie nižšie popisujú inštaláciu, prihlásenie a tiež všetky konfiguračné možnosti jednotlivých agentov.

## Augment Code

### Inštalácia

VS Code rozšírenie je v devcontaineri nainštalované **automaticky** pomocou `.devcontainer/devcontainer.json` > `"customizations"` > `"vscode"` > `"extensions"` > `"augment.vscode-augment"`.

CLI (`auggie`) je v devcontaineri nainštalované **automaticky** pomocou `.devcontainer/post-create.sh` > `# install Auggie CLI (Augment Code)`.

### Prihlásenie

Na [app.augmentcode.com](https://app.augmentcode.com/) je potrebné vytvoriť si osobný účet. V prípade súkromného použitia si zaplatiť niektorý z plánov. **V prípade pracovného použitia** požiadať o pridanie svojho osobného užívateľa medzi [firemných úžívateľov](https://app.augmentcode.com/account/team).

Pri prihlásení v `auggie` použiť osobný účet vytvorený na [app.augmentcode.com](https://app.augmentcode.com/).

Na firemnom účte je možné sledovať [kredity spotrebované jednotlivými užívateľmi](https://app.augmentcode.com/account/analytics).

### Konfigurácia

Augment Code je možné konfigurovať nasledovne:

| Súbor / priečinok                 | Na čo slúži                                      | Poznámka                                                                                                                                                                                                               |
| --------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.augment/rules/*.md`             | Projektové rules                                 | Rules v `.augment/rules` sú Markdown súbory; vo VS Code môžu byť **always_apply**, **manual**, alebo **agent_requested**. Workspace rules sú určené na commitovanie do repozitára. ([docs.augmentcode.com][augment-1]) |
| `AGENTS.md`                       | Hierarchické pravidlá                            | Môže byť v roote aj podadresároch; Augment ho pri práci so súborom hľadá v aktuálnom adresári a rodičovských adresároch. ([docs.augmentcode.com][augment-2], [agents.md](https://agents.md/))                          |
| `CLAUDE.md`                       | Hierarchické pravidlá kompatibilné s Claude Code | Funguje podobne ako `AGENTS.md`; iba `AGENTS.md` a `CLAUDE.md` sa objavujú hierarchicky, nie `.augment/rules` v podadresároch. ([docs.augmentcode.com][augment-2])                                                     |
| `.augment/skills/<name>/SKILL.md` | Skills                                           | Každý skill je vlastný adresár so `SKILL.md`; musí mať YAML frontmatter `name` a `description`. ([docs.augmentcode.com][augment-3])                                                                                    |
| `.claude/skills/<name>/SKILL.md`  | Skills kompatibilné s Claude Code                | Augment ich vie objaviť ako workspace skills. ([docs.augmentcode.com][augment-3])                                                                                                                                      |
| `.agents/skills/<name>/SKILL.md`  | Štandardný agentskills.io formát                 | Tiež podporované ako workspace skills. ([docs.augmentcode.com][augment-3])                                                                                                                                             |
| `.augment/commands/*.md`          | Vlastné slash commands                           | Objavia sa v `/` autocomplete menu v chate; napr. `.augment/commands/security-review.md` → `/security-review`. ([docs.augmentcode.com][augment-4])                                                                     |
| `.augment/commands/foo/bar.md`    | Namespaced commands                              | Napr. `.augment/commands/frontend/component.md` → `/frontend:component`. ([docs.augmentcode.com][augment-4])                                                                                                           |
| `.claude/commands/*.md`           | Claude-compatible commands                       | Augment ich vie použiť ako kompatibilné commands. ([docs.augmentcode.com][augment-4])                                                                                                                                  |
| `.cursor/commands/*.md`           | Cursor-compatible commands                       | Podporované vo VS Code custom commands lokáciách. ([docs.augmentcode.com][augment-4])                                                                                                                                  |
| `.augmentignore`                  | Čo sa nemá indexovať                             | Funguje podobne ako `.gitignore`; Augment indexuje workspace okrem súborov z `.gitignore` a `.augmentignore`. Vieš použiť aj `!` na zahrnutie gitignored súborov. ([docs.augmentcode.com][augment-5])                  |

[augment-1]: https://docs.augmentcode.com/setup-augment/guidelines "Rules & Guidelines for Agent and Chat - Augment"
[augment-2]: https://docs.augmentcode.com/cli/rules "Rules & Guidelines - Augment"
[augment-3]: https://docs.augmentcode.com/using-augment/skills "Skills - Augment"
[augment-4]: https://docs.augmentcode.com/using-augment/custom-commands "Custom Commands - Augment"
[augment-5]: https://docs.augmentcode.com/setup-augment/workspace-indexing "Index your workspace - Augment"

V adresárovej štrukúre to vyzerá nasledovne:

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
    settings.json          # skôr Auggie/CLI a pokročilé shared nastavenia
    settings.local.json    # lokálne, necommitovať
    agents/                # subagents, hlavne Auggie/CLI
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

### Inštalácia

VS Code rozšírenie je v devcontaineri nainštalované **automaticky** pomocou `.devcontainer/devcontainer.json` > `"customizations"` > `"vscode"` > `"extensions"` > `"anthropic.claude-code"`.

CLI (`claude`) je v devcontaineri nainštalované **automaticky** pomocou `.devcontainer/post-create.sh` > `# install Claude Code CLI`.

### Prihlásenie

Na [platform.claude.com](https://platform.claude.com/) je potrebné vytvoriť si osobný účet. V prípade súkromného použitia si zaplatiť niektorý z plánov. **V prípade pracovného použitia** požiadať o pridanie svojho osobného užívateľa medzi [firemných úžívateľov](https://platform.claude.com/settings/members) (s role `Clade Code` alebo `Developer`).

Pri prihlásení v `claude` > `/login` zvoliť `2. Anthropic Console account · API usage billing` a použiť osobný účet vytvorený na [platform.claude.com](https://platform.claude.com/).

Na firemnom účte je možné sledovať [kredity spotrebované jednotlivými užívateľmi](https://platform.claude.com/cost?group_by=key_id).

### Konfigurácia

Claude Code je možné konfigurovať nasledovne:

| Súbor / priečinok                 | Na čo slúži                                                                                    | Poznámka                                                                                                                                                   |
| --------------------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE.md`                       | Hlavné projektové inštrukcie: architektúra, build/test príkazy, coding conventions, workflow.  | Projektový `CLAUDE.md` môže byť v roote alebo ako `.claude/CLAUDE.md`; Claude ho načítava ako persistent instructions. ([Claude API Docs][claude-1])       |
| `.claude/CLAUDE.md`               | Alternatívne miesto pre projektové inštrukcie.                                                 | Rovnaký účel ako root `CLAUDE.md`, len uložený v `.claude/`. ([Claude API Docs][claude-1])                                                                 |
| `CLAUDE.local.md`                 | Tvoje súkromné projektové poznámky/preferencie.                                                | Claude ho načítava spolu s `CLAUDE.md`; má byť v `.gitignore`. ([Claude API Docs][claude-1])                                                               |
| `.claude/rules/*.md`              | Modulárne pravidlá, napr. coding style, testing, security, API pravidlá.                       | Rules môžu byť rozdelené do podadresárov a môžu byť path-scoped. ([Claude API Docs][claude-1])                                                             |
| `.claude/settings.json`           | Zdieľané projektové nastavenia: permissions, env, hooks, pluginy, vylúčenie citlivých súborov. | Shared project settings uložené v repozitári. ([Claude API Docs][claude-2])                                                                                |
| `.claude/settings.local.json`     | Lokálne overrides pre konkrétny projekt.                                                       | Lokálne nastavenia, Claude Code ich pri vytvorení nastaví ako gitignored. ([Claude API Docs][claude-2])                                                    |
| `.claude/skills/<skill>/SKILL.md` | Skills: opakovateľné postupy, checklisty, workflow a špecializované znalosti.                  | Skills sa dajú volať cez `/skill-name`; `.claude/commands/*.md` aj `.claude/skills/<name>/SKILL.md` vytvárajú slash command. ([Claude API Docs][claude-3]) |
| `.claude/commands/*.md`           | Legacy custom slash commands.                                                                  | Stále fungujú, ale custom commands boli zlúčené so skills; nové veci je lepšie dávať do skills. ([Claude API Docs][claude-3])                              |
| `.claude/agents/*.md`             | Custom subagents so samostatným promptom, tool access a permissions.                           | Projektové subagents žijú v `.claude/agents/`; používajú sa na špecializované úlohy a izolovaný kontext. ([Claude API Docs][claude-4])                     |
| `.mcp.json`                       | Projektové MCP servery zdieľané s tímom.                                                       | Project-scoped MCP konfigurácia sa ukladá do `.mcp.json` v roote projektu. ([Claude API Docs][claude-5])                                                   |
| `.gitignore`                      | Ochrana pred commitnutím lokálnych Claude súborov a citlivých dát.                             | Na blokovanie prístupu Claude Code k citlivým súborom použi aj `permissions.deny` v `.claude/settings.json`. ([Claude API Docs][claude-2])                 |

[claude-1]: https://docs.anthropic.com/en/docs/claude-code/memory "How Claude remembers your project - Claude Code Docs"
[claude-2]: https://docs.anthropic.com/en/docs/claude-code/settings "Claude Code settings - Claude Code Docs"
[claude-3]: https://docs.anthropic.com/en/docs/claude-code/skills "Extend Claude with skills - Claude Code Docs"
[claude-4]: https://docs.anthropic.com/en/docs/claude-code/sub-agents "Create custom subagents - Claude Code Docs"
[claude-5]: https://docs.anthropic.com/en/docs/claude-code/mcp "Connect Claude Code to tools via MCP - Claude Code Docs"

V adresárovej štrukúre to vyzerá nasledovne:

```
repo/
  CLAUDE.md
  CLAUDE.local.md          # lokálne, necommitovať
  .mcp.json                # zdieľané MCP servery

  .claude/
    CLAUDE.md              # alternatíva k root CLAUDE.md
    settings.json          # zdieľané project settings
    settings.local.json    # lokálne project settings, necommitovať

    rules/
      general.md
      frontend/react.md
      backend/api.md

    skills/
      deploy-staging/
        SKILL.md
        scripts/
        examples.md

    commands/              # legacy; stále funguje
      review.md
      fix-issue.md

    agents/
      code-reviewer.md
      debugger.md
      security-auditor.md
```

## Antigravity

### Inštalácia

VS Code rozšírenie nie je nainštalované (neexistuje).

CLI (`agy`) je v devcontaineri nainštalované **automaticky** pomocou `.devcontainer/post-create.sh` > `# install Antigravity CLI`.

### Prihlásenie

Na [accounts.google.com](https://accounts.google.com) je potrebné vytvoriť si google účet - t.j. stačí mať bežný osobný google účet. **Antigravity je možné použivať aj zadarmo** cez svoj osobný google účet, treba však rátať s limitmi, dostupnosťou podľa kapacity, prípadne si zaplatiť niektorý z [plánov](https://antigravity.google/pricing). **V prípade pracovného použitia** požiadať o pridanie svojho osobného užívateľa medzi [firemných úžívateľov](https://console.cloud.google.com/iam-admin/iam).

Pri prihlásení v `agy` zvoliť `2. Use a Google Cloud project`, použiť osobný účet vytvorený na [accounts.google.com](https://accounts.google.com) a ako ID projektu zadať `project-605967c9-39ce-4929-b5b`.

Na firemnom účte je možné sledovať [aktuálnu cenu (spotrebu) za použité služby](https://console.cloud.google.com/billing/reports).

#### Uvodné nastavenie firemného účtu

Pre google účet, ktorý sa rozhodneš použiť ako firemný účet, je potrebné v [Google Cloud Console](https://console.cloud.google.com/):

- [Vytvoriť projekt](https://console.cloud.google.com/projectcreate), napr. `Run AI`.
- [Pridať mu billing account](https://console.cloud.google.com/billing), napr. `Run billing`.
- Povoliť `Agent platform API`: [konzola](https://console.cloud.google.com/apis/dashboard?cloudshell=true) (ikona `|>_|` vpravo hore) > `gcloud services enable aiplatform.googleapis.com`

### Konfigurácia

Antigravity je možné konfigurovať nasledovne:

| Súbor / priečinok                 | Na čo slúži                                                                               | Poznámka                                                                                                                                                                                                                            |
| --------------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GEMINI.md`                       | Workspace context / všeobecné projektové inštrukcie pre Gemini/Antigravity CLI.           | Antigravity CLI podporuje workspace context súbory `GEMINI.md` aj `AGENTS.md`. ([Google Antigravity][agy-1])                                                                                                                        |
| `AGENTS.md`                       | Tool-agnostic projektové inštrukcie pre coding agentov.                                   | Antigravity CLI číta `AGENTS.md` z aktívneho workspace; AGENTS.md je všeobecný otvorený formát pre agent instructions. ([Google Antigravity][agy-1], [agents.md](https://agents.md/))                                               |
| `.agents/agents.md`               | Definícia tímu/personas, napr. PM, engineer, QA, DevOps.                                  | Google codelab používa `.agents/agents.md` na centralizované definovanie špecializovaných agent personas. ([Google Codelabs][agy-2])                                                                                                |
| `.agents/rules/*.md`              | Workspace rules: projektové pravidlá pre štýl kódu, architektúru, testovanie, bezpečnosť. | Workspace rules žijú v `.agents/rules/`; globálne rules sú v `~/.gemini/GEMINI.md`. ([Google Antigravity][agy-3])                                                                                                                   |
| `.agents/skills/<skill>/SKILL.md` | Projektové skills: opakovateľné schopnosti/workflow balené ako adresár so `SKILL.md`.     | Antigravity dnes defaultuje na `.agents/skills`; skill je priečinok obsahujúci `SKILL.md`. ([Google Antigravity][agy-4], [medium][agy-5])                                                                                           |
| `.agents/workflows/*.md`          | Workspace workflows / custom slash commands.                                              | Workflows sú uložené Markdown súbory a spúšťajú sa cez `/workflow-name`; workspace workflows žijú v `.agents/workflows/`. ([Google Antigravity][agy-3])                                                                             |
| `.agents/hooks.json`              | Hooks: lokálne shell skripty spúšťané v určených bodoch agent execution cycle.            | Hooks sa konfigurujú v `hooks.json` v customization directory, napr. `.agents/` vo workspace. ([Google Antigravity][agy-6])                                                                                                         |
| `.agents/mcp_config.json`         | Projektová MCP konfigurácia, hlavne pre Antigravity CLI / workspace setup.                | Antigravity používa samostatný `mcp_config.json`; IDE dokumentácia uvádza globálny `~/.gemini/antigravity/mcp_config.json`, zatiaľ čo CLI/workspace návody uvádzajú aj projektové MCP pod `.agents/`. ([Google Antigravity][agy-7]) |

[agy-1]: https://antigravity.google/docs/gcli-migration "Migrating from Gemini CLI"
[agy-2]: https://codelabs.developers.google.com/autonomous-ai-developer-pipelines-antigravity "Build Autonomous Developer Pipelines using agents.md and skills.md in Antigravity  |  Google Codelabs"
[agy-3]: https://antigravity.google/docs/rules-workflows "Google Antigravity - Rules"
[agy-4]: https://antigravity.google/docs/skills "Agent Skills"
[agy-5]: https://medium.com/google-cloud/tutorial-getting-started-with-antigravity-skills-864041811e0d "Tutorial : Getting Started with Google Antigravity Skills"
[agy-6]: https://antigravity.google/docs/hooks "Hooks"
[agy-7]: https://antigravity.google/docs/mcp "Antigravity Editor: MCP Integration"

V adresárovej štrukúre to vyzerá nasledovne:

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
    mcp_config.json          # hlavne Antigravity CLI / projektové MCP; IDE MCP býva často globálne
```

## Codex

### Inštalácia

VS Code rozšírenie je v devcontaineri nainštalované **automaticky** pomocou `.devcontainer/devcontainer.json` > `"customizations"` > `"vscode"` > `"extensions"` > `"openai.chatgpt"`.

CLI (`codex`) je v devcontaineri nainštalované **automaticky** pomocou `.devcontainer/post-create.sh` > `# install Codex CLI`.

### Prihlásenie

Na [chatgpt.com](https://chatgpt.com/) je potrebné vytvoriť si osobný účet. **Codex je možné použivať aj zadarmo** cez svoj osobný GPT účet, treba však rátať s limitmi, dostupnosťou podľa kapacity, prípadne si zaplatiť niektorý z [plánov](https://chatgpt.com/#pricing). **V prípade pracovného použitia** požiadať o pridanie svojho osobného užívateľa medzi [firemných úžívateľov](https://chatgpt.com/admin/members).

Pri prihlásení v `codex` zvoliť `1. Sign in with ChatGPT` (pripadne `2. Sign in with Device Code` ak prvá možnosť nefunguje), použiť osobný účet vytvorený na [chatgpt.com](https://chatgpt.com/) a pri prihlásení v prehliadači vybrať `Run Development's Workspace`.

Na firemnom účte je možné sledovať [kredity spotrebované jednotlivými užívateľmi](https://chatgpt.com/admin/usage).

### Konfigurácia

| Súbor / priečinok                            | Na čo slúži                                                                                                               | Poznámka                                                                                                                                                                                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `AGENTS.md`                                  | Hlavné projektové inštrukcie pre Codex: build/test príkazy, architektúra, konvencie, čo znamená “done”.                   | Codex číta `AGENTS.md` pred prácou; v projekte ho hľadá od rootu po aktuálny adresár a skladá inštrukcie hierarchicky. ([OpenAI Developers][codex-1])                                                  |
| `AGENTS.override.md`                         | Voliteľný override pre inštrukcie v danom adresári.                                                                       | Pri discovery má prednosť pred `AGENTS.md`; Codex berie najviac jeden instruction súbor na adresár. ([OpenAI Developers][codex-1])                                                                     |
| `*/AGENTS.md`                                | Inštrukcie pre konkrétny podadresár, modul alebo service.                                                                 | Súbory bližšie k aktuálnemu pracovisku sa pridajú neskôr, takže môžu prebiť všeobecnejšie pravidlá z rootu. ([OpenAI Developers][codex-1])                                                             |
| `.codex/config.toml`                         | Projektové nastavenia Codexu: model, approvals, sandbox, MCP servery, hooks inline, skill overrides, subagent nastavenia. | Codex používa `~/.codex/config.toml` pre user config a `.codex/config.toml` pre projektové overrides; projektové `.codex/` vrstvy načíta iba v trusted projektoch. ([OpenAI Developers][codex-2])      |
| `.codex/hooks.json`                          | Lifecycle hooks pre projekt, napr. validácia promptov, logovanie, kontroly po tool calle alebo pri ukončení turnu.        | Codex hľadá hooks vedľa aktívnych config vrstiev ako `hooks.json` alebo inline `[hooks]` v `config.toml`; projektové hooks sa načítajú len v trusted projektoch. ([OpenAI Developers][codex-3])        |
| `.codex/rules/*.rules`                       | Pravidlá pre povolenie/promptovanie/blokovanie príkazov mimo sandboxu.                                                    | `.rules` sú experimentálne command rules; Codex skenuje `rules/` vedľa aktívnej config vrstvy, vrátane `<repo>/.codex/rules/`. ([OpenAI Developers][codex-4])                                          |
| `.codex/agents/*.toml`                       | Projektové custom subagents / custom agents s vlastným modelom, sandboxom, MCP, skills a developer instructions.          | Projektové custom agents sú samostatné TOML súbory v `.codex/agents/`; povinné polia sú `name`, `description`, `developer_instructions`. ([OpenAI Developers][codex-5])                                |
| `.agents/skills/<skill>/SKILL.md`            | Repo skills: opakovateľné workflow, runbooky, checklisty a špecializované postupy.                                        | Codex číta repo skills z `.agents/skills` od aktuálneho adresára po root repozitára; skill je adresár so `SKILL.md` a voliteľnými `scripts/`, `references/`, `assets/`. ([OpenAI Developers][codex-6]) |
| `.agents/plugins/marketplace.json`           | Repo marketplace katalóg pluginov pre tím/projekt.                                                                        | Repo-scoped marketplace sa dá uložiť do `$REPO_ROOT/.agents/plugins/marketplace.json`; položky ukazujú na plugin priečinky, často pod `./plugins/`. ([OpenAI Developers][codex-7])                     |
| `plugins/<plugin>/.codex-plugin/plugin.json` | Manifest Codex pluginu.                                                                                                   | Plugin má povinný manifest `.codex-plugin/plugin.json`; môže baliť skills, MCP servery, hooks, app integrácie a assets. ([OpenAI Developers][codex-7])                                                 |
| `plugins/<plugin>/skills/<skill>/SKILL.md`   | Skills zabalené v plugine.                                                                                                | Plugin manifest môže ukazovať na `skills` priečinok a tým distribuovať jeden alebo viac skills. ([OpenAI Developers][codex-7])                                                                         |
| `plugins/<plugin>/hooks/hooks.json`          | Hooks zabalené v plugine.                                                                                                 | Plugin môže obsahovať lifecycle hooks; pred spustením ich používateľ musí reviewnúť a trustnúť. ([OpenAI Developers][codex-7])                                                                         |
| `plugins/<plugin>/.mcp.json`                 | MCP servery zabalené v plugine.                                                                                           | V bežnom projekte sa MCP nastavuje cez `.codex/config.toml`; plugin môže mať vlastnú `.mcp.json`, na ktorú ukazuje manifest. ([OpenAI Developers][codex-8])                                            |
| `plugins/<plugin>/.app.json`                 | App / connector mappings pre plugin.                                                                                      | Plugin štruktúra môže obsahovať `.app.json` pre app alebo connector integrácie. ([OpenAI Developers][codex-7])                                                                                         |

[codex-1]: https://developers.openai.com/codex/guides/agents-md "Custom instructions with AGENTS.md – Codex | OpenAI Developers"
[codex-2]: https://developers.openai.com/codex/config-basic "Config basics – Codex | OpenAI Developers"
[codex-3]: https://developers.openai.com/codex/hooks "Hooks – Codex | OpenAI Developers"
[codex-4]: https://developers.openai.com/codex/rules "Rules – Codex | OpenAI Developers"
[codex-5]: https://developers.openai.com/codex/subagents "Subagents – Codex | OpenAI Developers"
[codex-6]: https://developers.openai.com/codex/skills "Agent Skills – Codex | OpenAI Developers"
[codex-7]: https://developers.openai.com/codex/plugins/build "Build plugins – Codex | OpenAI Developers"
[codex-8]: https://developers.openai.com/codex/mcp "Model Context Protocol – Codex | OpenAI Developers"

V adresárovej štrukúre to vyzerá nasledovne:

```
repo/
  AGENTS.md
  AGENTS.override.md          # voliteľné, dočasné override
  services/
    api/
      AGENTS.md               # voliteľné, špecifické pre podadresár

  .codex/
    config.toml               # projektový Codex config; len trusted projekty
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
