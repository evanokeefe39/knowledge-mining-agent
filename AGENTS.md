## Build/Lint/Test Commands
- **Install dependencies**: `poetry install`
- **Run Flask app**: `python app/app.py` (runs on http://localhost:5000)
- **Run single test**: `python utils/test_citations.py`
- **Run evaluations**: `python run_evaluations.py`
- **Build docs**: `mkdocs build`
- **Serve docs**: `mkdocs serve`

## Code Style Guidelines
- **Imports**: Standard library first, then third-party, then local imports. Use absolute imports.
- **Formatting**: Follow PEP8. Use 4 spaces for indentation. Line length <= 100 chars.
- **Types**: Use type hints for function parameters and return values (from typing import).
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants.
- **Docstrings**: Use triple quotes for all functions/classes. Include Args/Returns/Raises sections.
- **Error handling**: Use try/except blocks. Log errors with custom logger from log.py.
- **Configuration**: Use config.py for all settings. Store secrets in .env, non-secrets in config.yaml.

## Supabase Data
The data available in supabase is in the 'dw' schema and contains metadata from youtube i.e channel and video metadata. Also contains youtube transcripts, transcript summaries, and video topics.
- Only use data in the dw schema
- Do not use youtube-transcript-api

## Tech Stack
Use the bellow tech stack, you must ask before adding other services or frameworks
- Langchain for Agent development
- Supabase for relational database
- pgvector in supabase for vector database
- python programming language
- flask for web apps

## Evals
- when running evals dump the results into a .evals folder for each run, name each run with a timestamp to avoid naming collision
- .gitignore .evals folder and its children

