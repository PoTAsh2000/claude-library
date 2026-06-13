---
name: project-version-manager
description: >-
  Increment the project version (major/minor/patch) following semantic versioning rules.
  Detects the version file automatically (pom.xml, package.json, build.gradle, etc.),
  proposes the correct increment based on git changes or an explicit argument, and applies it.
  Invoked with /project-version-manager.
  <example>User: /project-version-manager patch</example>
  <example>User: /project-version-manager "added new search feature"</example>
  <example>User: /project-version-manager (no arg — analyzes recent git changes)</example>
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Edit
  - AskUserQuestion
arguments:
  - name: increment
    description: >-
      Explicit increment type (patch / minor / major) OR a free-text description of the
      change (the skill infers the increment type from it). If omitted, the skill analyzes
      recent git history since the last tag to determine the appropriate increment.
    required: false
    argument-hint: "[patch|minor|major|\"description of change\"] (optional)"
---

# Project Version Manager

Locate the **project's** version declaration, determine the correct version increment, confirm
with the user, and apply it. The versioning rules below are authoritative — follow them
exactly, with the primary rules taking precedence over supplementary ones.

## Versioning Rules

### Primary rules (always take precedence)

| Increment | When to apply |
|------|---------------|
| **patch** | Bug fixes and very minor changes that users will probably not notice |
| **minor** | New features, or changes to existing features that users will notice |
| **major** | Changes to **core** functionality that make previous versions incompatible with the new version |

When a set of changes spans multiple increment types (e.g., a bug fix and a new feature in
the same release), always apply the **highest** applicable increment (minor in that example).

### Supplementary rules (fill edge cases not covered above)

- **Version resets:** Incrementing major → reset minor and patch to 0. Incrementing minor → reset patch to 0.
- **Initial development:** Versions `0.x.y` indicate an unstable, pre-release API. `1.0.0` is the first stable public release.
- **Never modify a released version.** Always produce a new, higher version number.
- **Pre-release suffixes** (e.g., `-SNAPSHOT`, `-alpha`, `-rc.1`): strip the suffix before calculating the next version; do not carry it into the new version unless the user explicitly requests it.

## Workflow

### Step 1 — Find the version file

Search the project root for a version declaration. Check in this order:

1. `pom.xml` — project-level `<version>` (the first `<version>` inside `<project>`, before any `<dependencies>` block)
2. `package.json` — top-level `"version"` field
3. `build.gradle` or `build.gradle.kts` — `version = "..."` or `version = '...'`
4. `pyproject.toml` — `version = "..."` under `[project]` or `[tool.poetry]`
5. `Cargo.toml` — `version = "..."` under `[package]`

If no version file is found, stop and tell the user:
> "No version file detected. Add a version declaration to pom.xml, package.json, or a similar project manifest first."

If multiple version files are found, list them and ask the user which one to update via `AskUserQuestion` before continuing.

### Step 2 — Read the current version

Extract the current version string and validate it matches `X.Y.Z` (with an optional
pre-release suffix). Strip any suffix before computing the next version.

Report: `Current version: X.Y.Z`

### Step 3 — Determine increment type

**If a `increment` argument was provided:**
- If it is exactly `patch`, `minor`, or `major` → use it directly, no analysis needed.
- If it is a description of a change → apply the primary versioning rules to classify it, state which increment type you chose and why, then continue.

**If no argument was provided:**
- Run:
  ```
  git log $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD --oneline
  ```
  to list commits since the last tag (or since the initial commit when no tag exists).
- If the result is empty, stop and tell the user:
  > "No commits found since the last release — nothing to increment."
- Analyze the commit messages. Apply the primary versioning rules to determine the highest required increment. State which commits drove the decision.

### Step 4 — Propose the new version

Calculate the new version:
1. Start from the stripped (suffix-free) current version
2. Increment the chosen segment
3. Apply version resets per the supplementary rules

Display the proposal clearly:

```
Current version : X.Y.Z
Increment type       : patch | minor | major
Reason          : [one sentence referencing the specific change(s) or argument]
New version     : X'.Y'.Z'
```

Use `AskUserQuestion` to ask the user to confirm before making any file changes.

### Step 5 — Apply the increment

After the user confirms:
- Use `Edit` to replace the version string in the file identified in Step 1.
- For `pom.xml`: update only the project-level `<version>` tag — never touch dependency or plugin version tags.
- For all files: preserve surrounding syntax (XML tags, quotes, key names) exactly; change only the version value itself.

Report: `Updated version to X'.Y'.Z' in [filename]`

**Do not** create a git commit, tag, or push anything. Editing the version file is where this skill stops. Use `/commit` afterwards to commit the change.
