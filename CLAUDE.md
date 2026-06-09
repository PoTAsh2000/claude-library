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

## Git Conventions

Commits follow Conventional Commits format: `type(scope): description`

Valid types: `feature`, `fix`, `refactor`, `performance`, `test`, `docs`, `style`, `build`, `cicd`, `chore`
