---
name: commit
description: >
  Detect current code changes with git, analyze what changed, then stage
  everything (git add .) and create a Conventional Commits message
  (type(scope): description). Trigger: /commit, "commit changes",
  "make a commit", "commit my work".
user-invocable: true
model: haiku
context: fork
arguments:
  - name: message
    description: Optional commit description. If provided, it becomes the subject text; the skill still detects/prepends the correct type(scope). If omitted, the message is generated from the diff analysis.
    required: false
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
argument-hint: "[message] (optional, auto-generated from the diff if omitted)"
---

# Commit Skill

Detect the current code changes, analyze them, stage everything with `git add .`,
and create a Conventional Commits message — committing immediately (no push).

Follow these steps in order. Stop immediately if any step says to stop.

## Performance — keep this fast

This skill must run in **exactly two Bash calls**: one to read (Step 1), one to write
(Step 6). Do **not** split git commands into separate calls. Steps 2–5 are pure
reasoning off the Step 1 output — perform them silently. Do **not** narrate each step
or echo the diff back to the user; go straight from the read to the commit. Serial tool
round-trips are the main cost, so minimizing them is the whole point.

## Step 1 — Read repo state (single Bash call)

Run all reads in **one** Bash invocation:

```
git rev-parse --git-dir && echo "===STATUS===" && git status --porcelain && echo "===DIFF===" && git diff HEAD
```

- If the first command fails (non-git directory), the chain short-circuits — **stop**
  and tell the user: "This directory is not a git repository — nothing to commit."
- The `===STATUS===` / `===DIFF===` markers separate the sections in the single output.
  `git status --porcelain` catches staged, unstaged, and untracked files; `git diff HEAD`
  gives the content of tracked changes (note untracked files from the status section).
- If the status section is empty, **stop** and tell the user: "No changes to commit."
- **Fresh repo with no commits:** `git diff HEAD` errors because there's no `HEAD`.
  Ignore that error and treat every file in the status section as newly added.

## Step 3 — Safety guard (hard stop)

Before staging, inspect the changes from Step 2. **Stop and warn the user** (do NOT
commit) if you see either of the following:

- **Secrets / credentials** — API keys, tokens, passwords, private keys, connection
  strings, or `.env` files containing real values. (Aligns with the security rule:
  never commit secrets.)
- **Generated / dependency / IDE artifacts** being added — e.g. `node_modules/`,
  `target/`, `dist/`, `build/`, `.idea/`, `.vscode/`, compiled binaries, large
  build outputs. (Aligns with the git-conventions rule: never commit these.)

If found, report exactly what triggered the guard and suggest the user gitignore or
unstage it. This guard is the only thing that overrides "commit immediately."

## Step 4 — Analyze the changes (silently)

Determine what actually changed: which files/modules were touched and the nature of
the change (new behavior, bug fix, refactor, docs, config, etc.). Do this internally —
do not write a summary to the user.

From that analysis, choose **exactly one** commit type from the menu below, and — when
a clear module, component, or feature is involved — an optional `scope`. Prefer the
**core set**; reach into the extended set only when one of those clearly fits better.

### Core set

| Type | Use for |
|------|---------|
| `feature` | a new feature, capability, or minor additions or changes |
| `fix` | a bug fix in **INCORRECTLY** existing code, logic and behavior. minor code additions are **not** specified as fix |
| `refactor` | code change that neither fixes a bug nor adds a feature |
| `performance` | performance improvement |
| `test` | adding or correcting tests |
| `docs` | documentation only |
| `style` | formatting/whitespace, no logic change |
| `build` | build system or external dependencies |
| `cicd` | CI/pipeline configuration |
| `chore` | maintenance, tooling, housekeeping |

### Extended set

| Type | Use for |
|------|---------|
| `revert` | reverting a previous commit |
| `security` | security fix or hardening |
| `dependency` | dependency version bumps/updates |
| `config` | runtime/app configuration changes (non-build) |
| `hotfix` | urgent production fix |
| `release` | version bump / release commit |
| `init` | initial scaffolding / project setup |
| `i18n` | internationalization / localization |
| `a11y` | accessibility improvements |
| `ui` | user-interface / visual changes |
| `database` | database schema / migration changes |
| `api` | API contract changes |
| `data` | data / seed / fixture changes |
| `infra` | infrastructure-as-code changes |
| `assets` | images, fonts, static assets |
| `cleanup` | removing dead code / unused files |
| `merge` | merge commit |

**Breaking changes:** append `!` after the type/scope (`feature!:` or `feature(api)!:`)
and/or add a `BREAKING CHANGE:` footer line.

## Step 5 — Build the commit message

Compose a Conventional Commits message:

- **Subject line:** `type(scope): description`
  - `description` is **lowercase**, **imperative mood** ("add" not "added"),
    and **≤ 72 characters**.
  - Scope is optional — use the module/component name when there's a clear one.
- If the user supplied the `message` argument, use it as the description text. Still
  detect and prepend `type(scope)` — unless the supplied message already starts with a
  `type:` or `type(scope):` prefix, in which case use it as-is.
- **Optional body:** one short line explaining *why* (not *what* — the diff shows the
  what). Keep the whole message to **max 2 content lines** (subject + at most one body line).

## Step 6 — Stage, commit, and report (single Bash call)

No confirmation. Stage, commit, and report in **one** Bash invocation. The two `-m`
flags are reliable in PowerShell and produce the standard blank line between subject
and body; `&&` ensures `git log` only runs after a successful commit (a failing
pre-commit hook surfaces its error naturally):

```
git add . && git commit -m "<subject>" -m "<optional why-body>" && git log -1 --stat
```

Omit the second `-m` if there is no body line.

Then report the created commit (hash + final message) to the user in one or two lines.
**Do not push** — the skill stops at the local commit.