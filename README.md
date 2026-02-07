# AI Toolkit LangGraph — Quick Start (uv-focused)

This README explains how to prepare your system, create an environment with `uv`, run the CLI commands, and build the package using `uv` on Windows (PowerShell examples). It also includes alternative venv instructions where appropriate.

---

## Overview

AI Toolkit LangGraph is a CLI-first Python package that provides:
- AI-assisted code review with structured Pydantic output
- Conventional commit message generation from git diffs
- Multi-provider LLM support (OpenAI, Anthropic, etc.)
- A console script `ai-toolbox` as the primary user interface

The project uses a `src/` layout and ships a PEP-561 typing marker (`py.typed`).

---

## 1) Prerequisites & system setup

Minimum required tools:
- Python 3.12+ (Windows installer from python.org or a version manager)
- Git (for repo operations)
- pip (bundled with Python; upgrade recommended)
- (Optional for developers) `build` and `twine` when creating distributions
- `uv` (optional, recommended for reproducible environment management)

PowerShell commands to verify and install core tools:

```powershell
# Verify Python and pip
python --version
python -m pip --version

# Upgrade pip
python -m pip install --upgrade pip

# Install uv globally (optional)
python -m pip install --upgrade uv
uv --version

# Install build & twine for packaging
python -m pip install --upgrade build twine
```

Notes:
- Use the Microsoft Store / installer or a version manager to install Python. Ensure the installed Python is on your PATH.
- If you cannot install `uv`, skip its steps and use a virtual environment instead (see venv instructions below).

---

## 2) Clone the repo and create a `.env` for local development

```powershell
git clone <your-repo-url>
cd ai_toolkit_langgraph
```

Create a `.env` in the project root for local development keys (do NOT commit it):

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=claude-...
```

Add `.env` to `.gitignore` so secrets are not committed.

---

## 3) Create and manage environment with `uv` (recommended)

`uv` provides a reproducible environment defined by lock files. Commands below assume `uv` supports `sync`, `run`, `shell`, and `--extra` flags. If your `uv` version uses different subcommands (e.g., `install` instead of `sync`), adapt accordingly.

1) Sync environment from lock and install dev extras:

```powershell
# Sync and install runtime + dev extras
uv sync --extra dev
# or (if your uv uses `install`):
uv install --extra dev
```

- `--extra dev` installs the optional dev dependencies declared in `pyproject.toml` (linters, test tools).
- If a `uv.lock` does not exist yet, you can create one after installing dependencies with `uv lock` (command depends on uv release).

2) Run single commands inside the uv-managed environment:

```powershell
# Run python inside uv env
uv run python --version

# Run tests
uv run pytest -q

# Run the ai-toolbox CLI
uv run ai-toolbox --help
uv run ai-toolbox commit
uv run ai-toolbox review
uv run ai-toolbox review --uncommitted
```

3) Open an interactive shell inside uv environment (convenient for iterative work):

```powershell
uv shell
# now you are inside the env; run commands normally
python -m pip install -e .[dev]   # optional local editable install
ai-toolbox --help
exit
```

4) Manage dependencies with `uv` (examples — exact commands depend on uv version):

```powershell
# Add a new dependency (if supported by your uv version)
uv add <package>
# Update lockfile after changes
uv lock
```

---

## 4) Useful `uv run` command patterns (playground)

Run the CLI with different inputs:

```powershell
# Default behavior (uses default model from CLI)
uv run ai-toolbox commit

# Use a specific model
uv run ai-toolbox --model gpt-4o-mini commit
uv run ai-toolbox --model anthropic/claude-3-5-sonnet-20241022 review

# Review uncommitted changes (if your review command supports a flag)
uv run ai-toolbox review --uncommitted

# Run with environment variables inline (temporary override)
uv run env OPENAI_API_KEY="sk-..." ai-toolbox review

# Combine with other tools
uv run ruff src tests
uv run mypy src
```

Notes:
- If `uv run ai-toolbox review --uncommitted` is not implemented in the CLI, run `uv run ai-toolbox review` and pass the intended flag or mode supported by the CLI.

---

## 5) Alternative: Use a Virtualenv (if you don't use `uv`)

```powershell
python -m pip install --upgrade pip
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest -q
ai-toolbox --help
```

This flow is more portable and familiar if you don't use `uv`.

---

## 6) Build the Python package using `uv`

Build inside the uv-managed environment so the exact build tools from your lock are used.

```powershell
# ensure build is available inside the uv env
uv run python -m pip install --upgrade build

# create source and wheel distributions
uv run python -m build

# list artifacts
dir .\dist\
```

Validate artifacts and metadata with twine inside `uv`:

```powershell
uv run python -m pip install --upgrade twine
uv run twine check dist/*

# test upload to TestPyPI
uv run python -m twine upload --repository testpypi dist/*

# when ready, upload to real PyPI
uv run python -m twine upload dist/*
```

If you prefer an interactive flow:

```powershell
uv shell
python -m pip install --upgrade build twine
python -m build
twine check dist/*
twine upload --repository testpypi dist/*
exit
```

---

## 7) Verifying install from TestPyPI (example)

```powershell
pip install --index-url https://test.pypi.org/simple/ --no-deps ai-toolkit-langgraph==0.1.0
```

Replace package name & version accordingly. Use `--no-deps` to avoid attempting to fetch dependencies from TestPyPI.

---

## 8) Credentials & safety

- Twine requires credentials for TestPyPI/PyPI. Provide them using `~/.pypirc` or `TWINE_USERNAME` / `TWINE_PASSWORD` env vars, or you'll be prompted interactively.
- Never include `.env` or secret keys in the package or commit history.

---

## 9) Troubleshooting

- If `uv` commands differ, run `uv --help` and adapt. Different uv releases have slightly different CLIs.
- For dependency resolver failures, upgrade pip and use a fresh Python/uv environment.
- If `ai-toolbox` isn't found after running `uv sync`, ensure the project entry points are installed in the uv env, or inside `uv shell` run `python -m pip install -e .`.

---

## 10) Quick Start Playbook (copy-paste)

```powershell
# install uv and tools
python -m pip install --upgrade pip
pip install uv build twine

# sync project with dev extras
uv sync --extra dev

# run tests
uv run pytest -q

# run CLI
uv run ai-toolbox commit
uv run ai-toolbox review --uncommitted

# build and check
uv run python -m build
uv run twine check dist/*

# test upload
uv run python -m twine upload --repository testpypi dist/*
```

---

If you want, I can also:
- add a sample `~/.pypirc` template for TestPyPI,
- create a GitHub Actions workflow that builds and publishes to TestPyPI on tag, or
- generate a short help doc with `uv` commands adapted to your installed `uv` version (run `uv --version` and paste it here). Which would you like next?
