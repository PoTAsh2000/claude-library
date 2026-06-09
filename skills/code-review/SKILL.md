---
name: code-review
description: Run a structured code review on recent changes, a specific file/directory, or a commit range. Produces severity-rated findings and a verdict. Invoked with /review.
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
argument-hint: "[path or commit range] (optional — defaults to uncommitted changes)"
---

# Code Review Skill

Run a structured code review. If no argument is provided, reviews uncommitted changes.

## Workflow

### Step 1: Determine Scope

- **No argument**: Review uncommitted changes (`git diff` + `git diff --staged`).
- **File or directory path**: Review that specific path.
- **Commit range** (e.g., `HEAD~3..HEAD`): Review changes in that range.

Run the appropriate git command to get the diff. Also read the full files for context, not just the diff.

### Step 2: Understand Context

- What feature or fix do these changes implement?
- Are there related requirements in `docs/requirements/`?
- Are there related design docs in `docs/design/`?
- Read any relevant test files to understand coverage.

### Step 3: Apply Review Checklist

Check systematically:

1. **Architecture** — Is logic in the correct layer? Dependencies flowing the right way?
2. **Correctness** — Does the code do what it claims? Edge cases handled?
3. **Security** — Input validation? Injection risks? Secrets? Auth checks?
4. **Error handling** — All failure paths covered? Errors informative but safe?
5. **Testing** — Are the right things tested? Coverage adequate?
6. **Performance** — N+1 queries? Unbounded collections? Blocking calls?
7. **Conventions** — Follows existing project patterns? Names descriptive?

### Step 4: Produce Review

Output the review in this format:

```markdown
## Code Review: [scope description]

### Summary
[1-2 sentence overall assessment]

### Findings

| # | Severity | File:Line | Issue | Suggestion |
|---|----------|-----------|-------|------------|

### Positive Observations
[Things done well]

### Verdict
APPROVE / REQUEST_CHANGES / COMMENT
```

### Step 5: Recommend Next Steps

- If CRITICAL security findings: suggest invoking the `security-reviewer` agent for deeper analysis.
- If test gaps found: suggest invoking the `qa-test-engineer` agent.
- If architecture concerns: suggest consulting the `software-architect` agent.
