# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A personal Claude Code marketplace library — a curated collection of reusable **skills**, **agents**, and **rules** published to GitHub and distributed as a marketplace source. This is not a compiled project; all artifacts are prompt/config files that Claude Code loads directly.

To use this library, add it to `~/.claude/settings.json` under `extraKnownMarketplaces`.

## Repository Structure

```
.claude-plugin/marketplace.json   # Single source of truth: all plugins registered here
skills/                           # User-invocable commands (triggered with /)
agents/                           # Specialized AI orchestrators
rules/                            # Always-applied conventions (alwaysApply: true)
```

Each plugin directory contains:
- `plugin.json` — Minimal metadata (name, description, version)
- `agent.md`, `SKILL.md`, or `rule.md` — The system prompt / behavioral definition

## Plugin Conventions

**File naming is case-sensitive:**
- Skills: `SKILL.md`
- Agents: `agent.md`
- Rules: `rule.md`

**Directory names:** lowercase with hyphens (`backend-developer`, `code-review`)

**Registering a new plugin:** Add an entry to `.claude-plugin/marketplace.json` with `name`, `description`, `source` (relative path), and `category` (`skills`, `agents`, or `rules`). There is no build step — the manifest change is the registration.

## No Build System

There are no commands to build, test, or lint this repository. The "artifacts" are markdown/JSON files. Validation is implicit: if Claude Code can load and invoke the plugin, it works.

## Target Tech Stack

The skills and agents in this library are authored for projects using:
- **Backend:** Java, Spring Boot, Apache Camel, Maven
- **Frontend:** Vue 3 with TypeScript (strict mode)
- **Data:** SQL (PostgreSQL)
- **Infrastructure:** Docker, Kubernetes, CI/CD pipelines

Skills and agents are designed to be framework-aware but not framework-locked — the frontend agent is explicitly framework-agnostic.

## Authoring Guidelines for Plugins

**Skills** should define: invocation trigger, expected inputs (args), step-by-step workflow, and output format. See `skills/code-review/SKILL.md` or `skills/commit/SKILL.md` for reference patterns.

**Agents** should define: role, 8–10 architectural/behavioral principles, a phased workflow, and what the agent must always/never do. See `agents/software-architect/agent.md` for the most complete example (8-phase design workflow with evaluation framework).

**Rules** use `alwaysApply: true` and should be concise, non-overlapping standards. Each rule file covers one domain (security, performance, database, etc.). Avoid cross-domain overlap between rule files.

## Frontmatter Schema

Each content file (`.md`) contains YAML frontmatter that defines metadata. The richer metadata lives in the content `.md` frontmatter; `plugin.json` stays minimal (name, description only).

**`agent.md` frontmatter:**
```yaml
name: agent-name
description: >-
  Role and purpose. Include <example>context blocks</example> to show how this agent is invoked.
model: inherit  # inherit (default, uses session model), haiku (fast/cheap), or opus (complex analysis)
color: cyan     # Display color in Claude Code UI
tools:          # List of available tools; use Agent(agent-name) syntax for inter-agent delegation
  - Read
  - Grep
  - Agent(analyst)
```

**`SKILL.md` frontmatter:**
```yaml
name: skill-name
description: >-
  What this skill does. Include <example>usage</example>.
user-invocable: true        # (Canonical: hyphen, not underscore)
allowed-tools:              # Tools this skill can call
  - Bash
  - Read
arguments:                  # Input args (optional)
  - name: arg-name
    description: What this arg does
    required: true
    argument-hint: "Shown in the / picker"
model: haiku                # (Optional override; default: inherit)
context: fork               # (Optional; isolates context window; use for lean/fast skills)
```

**`rule.md` frontmatter:**
```yaml
description: >-
  Standards for this domain. No 'name' field needed.
alwaysApply: true
```

**Model selection:**
- `inherit` — Default; runs at whatever model the session uses.
- `haiku` — Fast, cost-optimized tasks (e.g., `skills/commit` — just reads and stages).
- `opus` — High-stakes analysis needing deep reasoning (e.g., `agents/software-architect`).

**Note:** `skills/commit/SKILL.md` uses the non-canonical spelling `user_invocable` (underscore). New skills should use `user-invocable` (hyphen).

## Plugin Registry: Backlog vs. Reality

`marketplace.json` declares **39 plugins** but only **10 directories** currently exist in the repository. The manifest acts as a backlog/roadmap — when you plan a new plugin (skill, agent, or rule), add it to `marketplace.json` **before** creating the directory. This ensures the plugin is discoverable by Claude Code even while you're still authoring it.

Missing plugins are intentional and planned; they are not errors to fix. (As of the last update, 29 of 39 entries are registered but have no files yet.)

## Agent Dependencies and Context7 MCP

Several plugins reference agents that don't yet have files. When authoring new agents or updating existing ones, maintain these cross-references:

- `software-architect` agent invokes `Agent(analyst)`, `Agent(frontend-developer)`, and `Agent(security-reviewer)`.
- `/review` skill recommends invoking `security-reviewer`, `qa-test-engineer`, and `software-architect` agents for comprehensive checks.

**Context7 MCP Server:** All three existing agents (`backend-developer`, `frontend-developer`, `software-architect`) use `mcp__context7__resolve-library-id` and `mcp__context7__query-docs` tools. These require the `@upstash/context7-mcp` MCP server to be configured in Claude Code settings. Without it, those tool calls will silently fail. Document this dependency if adding a new agent that uses Context7.

## Language and Locale

The `readme` skill produces Dutch-language output (`Contactpersonen` table, `Processen` sections, Dutch description hints) for the target organization context. New skills targeting this same organization should follow the same Dutch-language convention.

## Git Conventions

Commits follow Conventional Commits format: `type(scope): description`

Valid types: `feature`, `fix`, `refactor`, `performance`, `test`, `docs`, `style`, `build`, `cicd`, `chore`

## Branch Protection and Development Workflow

**`master` is protected.** A GitHub Ruleset named `protect-master` is active with these rules:

- Restrict creations (cannot recreate master)
- Restrict deletions
- Block force pushes
- Require a pull request before merging (0 required approvals, solo project)

**Why:** `master` is the live source for all marketplace consumers. Any direct push immediately affects every user who has this library installed. All changes must be validated via a real feature-branch install before landing on master.

**Do not attempt to push directly to `master`** — it will be rejected. Use a feature branch.

### Feature Branch Naming

Follow the same prefix style as commit types:

```
feat/add-security-agent
fix/commit-skill-staging-bug
refactor/software-architect-phases
docs/update-authoring-guidelines
```

### Feature Branch Testing (Remote Install)

Claude Code resolves marketplace plugins from the raw GitHub URL, which encodes the branch name:

```
https://raw.githubusercontent.com/PoTAsh2000/claude-library/{branch}/.claude-plugin/marketplace.json
```

To test a feature branch before merging:

1. Push the feature branch to remote: `git push -u origin feat/my-branch`
2. In `~/.claude/settings.json`, add a temporary second entry to `extraKnownMarketplaces`:
   ```json
   {
     "name": "personal-library (feat/my-branch)",
     "sourceUrl": "https://raw.githubusercontent.com/PoTAsh2000/claude-library/feat/my-branch/.claude-plugin/marketplace.json"
   }
   ```
3. Open the Claude Code marketplace browser, install and validate the plugin
4. Remove the temporary entry from `settings.json` after testing (no cache clearing needed)
5. Open a PR on GitHub and merge to `master` only after the install is confirmed working
