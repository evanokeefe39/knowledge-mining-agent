# Agent Rules and Guidelines

This file contains the operational rules and guidelines for maintaining this codebase. Use this for audits and ensuring compliance.

## Shortcuts
- **audit** → Audit the codebase against this file. Reload rules first.
- **health** → Run all health checks. If missing, generate health checks for all services in use.
- **docs** → Generate or refresh MkDocs documentation.
- **lint** → Run style checks (PEP8 / black / flake8). Add config if missing.

## Utilities
Place helper functions, scripts, or tools for repetitive development tasks in a `/utils` folder. These are not part of the application runtime but speed up developer workflows. Examples include:

- **Build scripts** → e.g., building Docker images, packaging artifacts.
- **Database helpers** → scripts to query schema/metadata, list tables/columns, or run quick validation queries.
- **Health checks** → scripts to test connectivity to databases, APIs, or other services (e.g., `"SELECT 1"` for SQL).
- **Code quality tools** → wrappers for linting, formatting, or running test suites.
- **Data sampling scripts** → quick extract/transform scripts to preview external data sources and inform the agent when clarity is needed.
- **Automation tasks** → scripts to bootstrap configs, rotate logs, or refresh environments.

For **ad-hoc or temporary data**, use a `.temp` folder at the project root and add it to `.gitignore` to avoid committing. Keep `.temp` for throwaway datasets, test exports, or sandbox files.

## GitHub & Git
- Use feature branches from `main` (default). If the user requests, migrate to new strategy.
- Commit with [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Work only on `dev` or feature branches. Confirm with user if multiple feature branches are active.
- Always use Git. If missing, init repo with `.gitignore` (Python if Python project), README, and LICENSE.
- Use **GitHub CLI (`gh`)** if available to publish branches, open pull requests, and manage repo interactions. Fall back to the GitHub web UI if CLI is unavailable.

## Package Management & Artifacts
- Use **Poetry** in all Python projects.
- Add **python-dotenv** as a default dependency.
- Create `.env` with placeholder values.
- Use **MkDocs**; keep docs updated per branch and verify before merging.
- Create `config.yaml` for non-secret config. Secrets go in `.env`. Promote config to env only if user specifies.
- Create `config.py` to parse `config.yaml` + `.env`, expose a unified config object, obfuscate secrets in logs.
- Create `log.py` with a colorful custom logger.

## Licensing
- Add LICENSE at repo root.
- Default: MIT.
- If specified, generate standard text for license type (Apache-2.0, GPL-3.0, AGPL-3.0, BSD, MPL, LGPL, CC0, Unlicense).
- Replace `[year]` with current year, `[fullname]` with repo owner/org.
- If `spec.md`, `SECURITY.md`, or NFRs suggest stricter requirements, propose a restrictive license (e.g., GPL, AGPL, or proprietary) and prompt user.

## Coding Standards
- Store DB connection details in `.env`.
- Namespace env vars with `__` to avoid conflicts (e.g., `SUPABASE__DB_USER`).
- Follow **PEP8**.
- Add comments and up-to-date docstrings to functions.

## Configuration Management
- **config.yaml:** store non-secret configuration.
- **.env:** store secrets (passwords, tokens, API keys). Use `SERVICE__ITEM` format.
- **Dynamic expansion:** use a YAML loader that expands `${VAR}` from env. Leave unresolved vars unchanged.
- **config.py:** parse both `config.yaml` and `.env`; expose a unified config object; obfuscate secrets when logged.
- Keep `config.yaml`, `.env`, and MkDocs consistent.

## Databases, Data Pipelines & Integrations
- Validate table names by checking schemas of connected databases (using `.env` creds + health checks).
- Generate YAML ingestion contracts for every external ingestion; include in MkDocs.
- Follow Configuration Management rules for integration settings. Group multiple creds/endpoints clearly under service name.
- Document integration-specific requirements in both `SPEC.md` and MkDocs.

## Project Specifications
- Create `SPEC.md` at root. Keep it updated with functional + non-functional requirements.
- In `README.md`, include background, goals, and challenges.
- Create `JOURNAL.md` at root to record pivots, architecture decisions, major challenges, and other notes of record. Update this file as the project evolves.