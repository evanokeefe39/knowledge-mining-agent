# AGENTS.md

## Temporary Files Policy
ALL temporary, ad-hoc, or sample data MUST go in agent-specific working folders (e.g., .db-agent/, .devops-agent/, etc.):

- **Location**: Agent-specific folders at project root, prefixed with a dot (e.g., .db-agent/ for the database agent)
- **Git Status**: Automatically ignored via .gitignore (add patterns like .*-agent/ to ignore all such folders)
- **Purpose**: Keep repository clean of non-essential files while providing isolated working areas for each sub-agent
- **Working Area Usage**: These folders serve as dedicated scratch spaces for agents to create and manage temporary files during operations. Agents must be instructed to move any files that become useful or permanent (e.g., finalized schemas, tested configurations) out of their working area and into appropriate main project directories before committing.

Files that BELONG in agent-specific folders:

- Database schema dumps (sample_schema_output.txt in .db-agent/)
- Test data exports (test_export.csv in relevant agent folder)
- Debug outputs (debug_results.json in relevant agent folder)
- Exploratory data analysis results
- Any file created for investigation that shouldn't be committed

Files that do NOT belong in agent-specific folders:

- Configuration files
- Source code
- Documentation
- Production data

## Utilities Policy
Place helper functions, scripts, or tools for repetitive development tasks in a `/utils` folder. These are not part of the application runtime but speed up developer workflows.

**Examples:**
- **Database helpers** → `utils/db_inspector.py` for schema exploration
- **Health checks** → `utils/health_check.py` for service verification
- **Build scripts** → Docker image builders, artifact packagers
- **Code quality tools** → Linting, formatting, test runners
- **Data sampling scripts** → Preview external data sources

## GitHub & Git Policy
- Use feature branches from `main` (default). If the user requests, migrate to new strategy.
- Commit with [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Work only on `dev` or feature branches. Confirm with user if multiple feature branches are active.
- Always use Git. If missing, init repo with `.gitignore` (Python if Python project), README, and LICENSE.
- Use **GitHub CLI (`gh`)** if available to publish branches, open pull requests, and manage repo interactions. Fall back to the GitHub web UI if CLI is unavailable.
- when generating the body of the pull request description, use a temporary markdown file and the --body-file argument, delete the markdown file when finished.

## Pthon Package Management Policy and Virtual Environments
- Use **Poetry** in all Python projects, do not use anything other than Poetry.
- Default dependencies are:
    - python-dotenv
    - pyyaml
    - pydantic
    - mkdocs-material


## Project Initialization Policy
- Create  `.env`, `config.yaml` and `config.py` according to configuration policy
- Create `LICENSE` file according to Licensing Policy
- Create `log.py` according to logging policy
- Create `README.md` according to the project policy

## Documentation Policy
- Use **MkDocs**;
- Documentation goes under docs/ folder at root level

## Logging Policy
- let the user decide whether logs should be recorded to file/db for different modules
- implement and update logging according to project context. i.e logging for api's, apps, ai agents differ slightly in their requirements
- you can refer to SPEC.md at project root for any logging specifc requirements

## Licensing Policy
- Add LICENSE at repo root.
- Default: MIT.
- If specified, generate standard text for license type (Apache-2.0, GPL-3.0, AGPL-3.0, BSD, MPL, LGPL, CC0, Unlicense).
- Replace `[year]` with current year, `[fullname]` with repo owner/org.
- If `spec.md`, `SECURITY.md`, or NFRs suggest stricter requirements, propose a restrictive license (e.g., GPL, AGPL, or proprietary) and prompt user.

## Coding Standards & Design Patterns
- Store DB connection details in `.env`.
- Namespace env vars with `__` to avoid conflicts (e.g., `SUPABASE__DB_USER`).
- Follow **PEP8**.
- Add comments and up-to-date docstrings to functions.
- Do not add dependencies on external services without asking first

## Configuration Management
- **config.yaml:** store non-secret configuration.
- **.env:** store secrets (passwords, tokens, API keys). Use `SERVICE__ITEM` format. NEVER overwrite existing .env env vars unless explicitly instructed.
- **Dynamic expansion:** use a YAML loader that expands `${VAR}` from env. Leave unresolved vars unchanged.
- **config.py:** parse both `config.yaml` and `.env`; expose a unified `config` object
- Keep `config.yaml`, `.env`

## Databasese, Data Pipelines & Integrations
- Validate table names by checking schemas of connected databases (using `.env` creds + health checks).
- Generate YAML ingestion contracts for every external ingestion; include in MkDocs.
- Follow Configuration Management rules for integration settings. Group multiple creds/endpoints clearly under service name.
- Document integration-specific requirements in both `SPEC.md` and MkDocs.

## Project Policy
- Never overwrite `AGENTS.md` unless explicitly instructed.
- Create `SPEC.md` at root. Keep it updated with functional + non-functional requirements.
- In `README.md`, include basic set up instructions and cards that demonstrate quality metrics like test pass fails, CI/CD status and any other relevant information. Include basic setup instructions and usage examples. Include a brief 2-3 sentences on the projects goal and what problem it solves. i.e "we made <the tool> to help <the target audience> do <the task> better / faster etc."

## Database Access Policy
All future database access should use the `get_db()` function from `db.py` to ensure consistent connection management and configuration.