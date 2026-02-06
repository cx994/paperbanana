# Repository Guidelines

## Project Structure & Module Organization

- `paperbanana/`: core library and Typer CLI (`paperbanana/cli.py`), organized into `agents/`, `core/`,
  `providers/`, `evaluation/`, `reference/`, and `guidelines/`.
- `mcp_server/`: Model Context Protocol server (`mcp_server/server.py`) exposed via the
  `paperbanana-mcp` console script.
- `prompts/`: prompt templates for diagram/plot generation and evaluation.
- `configs/`: default configuration (`configs/config.yaml`) plus provider/pipeline presets.
- `data/`: reference dataset and curation assets (`data/reference_sets/`, `data/guidelines/`).
- `examples/` and `scripts/`: runnable examples and dataset tooling.
- `tests/`: pytest suite grouped by feature area.

## Build, Test, and Development Commands

- Install (editable + dev tools): `pip install -e ".[dev,google]"`.
- Configure API key: `paperbanana setup` (writes `.env`) or `cp .env.example .env`.
- Run locally:
  - Diagram: `paperbanana generate -i <txt> -c "<caption>"`
  - Plot: `paperbanana plot -d <csv|json> --intent "<intent>"`
  - Evaluate: `paperbanana evaluate -g <png> -r <png> --context <txt> -c "<caption>"`
- Lint/format: `ruff check paperbanana/ mcp_server/ tests/ scripts/` and `ruff format ...`.
- Tests: `pytest tests/ -v`.

## Coding Style & Naming Conventions

- Python 3.10+; prefer type hints and small, single-purpose functions.
- Formatting/linting is enforced by Ruff (line length: 100; config in `pyproject.toml`).
- Naming: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_CASE` for constants.

## Testing Guidelines

- Use `pytest` (+ `pytest-asyncio`) and place tests under `tests/` (e.g., `tests/test_pipeline/`).
- Add tests for new behavior (happy path + error handling). Name files `test_*.py`.

## Commit & Pull Request Guidelines

- Commits in this repo use short, sentence-case summaries (e.g., “Resolve linter errors”, “Updated code for
  python packaging”).
- PRs should follow `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`: include “What changed”, “How
  to test”, and ensure `pytest` + `ruff check` pass. For dataset additions, verify `metadata.json` and
  aspect ratio in [1.5, 2.5].

## Security & Configuration Tips

- Never commit `.env` or API keys; store `GOOGLE_API_KEY` locally.
- `paperbanana plot` executes generated Matplotlib code—review outputs before running in sensitive
  environments.
- The MCP server is intended for local use; don’t expose it to untrusted networks.
