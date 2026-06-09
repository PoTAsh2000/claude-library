---
name: readme
description: >
  This skill should be used when the user asks to "generate a README",
  "create a README", "update the README", "make a README.md",
  or mentions generating project documentation.
  It creates or updates a compact, high-level README.md based on the
  project's file structure, code, and optional user context.
user_invocable: true
arguments:
  - name: context
    description: Extra context van de gebruiker die niet uit de code te halen is (bijv. klantnaam, specifieke details over processen of endpoints).
    required: false
---

# README Generator Skill

Generate or update a compact, high-level README.md for the current project.

## Steps

### 1. Analyze the project

- Use Glob to map the full project structure (`**/*`).
- Read configuration files (e.g. `pom.xml`, `package.json`, `build.gradle`, `docker-compose.yml`, `application.yml`, `application.properties`, `.env.example`) to identify the tech stack.
- Read relevant source code to identify endpoints, services, APIs, databases, queues, scheduled jobs, and business processes.
- If a `CLAUDE.md` exists in the project root, read it and use it as additional context.
- If the user provided the `context` argument, incorporate that information into the analysis.

### 2. Generate or update README.md

Write the README.md using **exactly** this format:

```markdown
# {Project Name}

{Short description of the project in 4-10 sentences, summarize what business goals are achived with this application}

## Contactpersonen

| Naam | Email | Bedrijf | Functie |
|------|-------|---------|---------|
|      |       |         |         |

## Tech Stack

{List all external systems, endpoints, tools, databases, message brokers, etc.
Each item gets a short description, but dont specify every full endpoints, some ftp servers for example, use multiple directories. It is not important which directories or API paths are used, just the API, server, etc. Note any exceptions or special details.}

## Processen

{For each process, write a high-level description that references Tech Stack items in **bold**.
No implementation details — only describe the flow at a high level.
Sometimes applications also contain maintanence processes like: temp file cleanups, monitoring. for these processes, give a short description on why they are needed}

{Optional: note about shared patterns such as exception handling, mailing, retry logic, etc.}
```

### 3. Rules

- Write compact and high-level — no implementation details.
- **Bold** Tech Stack items when referencing them in the Processen section.
- Always leave the Contactpersonen table empty (the user fills this in themselves). If the table already contains content, **DO NOT** overwrite it or empty it when updating the README file.
- If a README.md already exists: preserve the structure, update the content. If there is no README, create one using the format.
- Always write the README in English.
- Do not invent information that cannot be derived from the code or the provided context.