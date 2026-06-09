# claude-library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A personal Claude Code marketplace library built for a software developer environment. Created for personal use to learn and experiment with Claude Code — it contains a curated collection of **skills**, **agents**, and **rules** that extend Claude Code across everyday development workflows.

This library is not an official Anthropic product. It reflects my own evolving patterns and conventions as I explore what Claude can do in a real software development context.

---

## Installation & Usage

### 1. Register the marketplace

Add the following to your `~/.claude/settings.json` under `extraKnownMarketplaces`:

```json
{
  "extraKnownMarketplaces": {
    "claude-library": {
      "source": {
        "source": "github",
        "repo": "PoTAsh2000/claude-library"
      }
    }
  }
}
```

### 2. Browse and install

Open the **Claude Code marketplace browser** (type `/` in Claude Code and browse the marketplace). The `claude-library` marketplace will appear alongside any other registered sources.

Select the skills, agents, or rules you want to install into your project or globally.

### 3. Auto-updates

Because this marketplace is registered as a GitHub source, Claude Code automatically pulls the latest version every time you open the marketplace browser. No manual sync step required — you always get the most recent tools.

---

## Contributing

Contributions are welcome. The following are accepted via pull request:

- **Bug fixes and corrections** — errors or mistakes in existing skills, agents, or rules
- **Improvements to existing tools** — better prompts, expanded coverage, or refined behavior

All pull requests are subject to review before merge. Please keep contributions focused and include a clear description of what the change does and why.

---

## License

[MIT](LICENSE) — © Thomas Arensman
