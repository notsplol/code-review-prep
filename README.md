# Code Review Prep Tool
This project is a pretty basic Python CLI tool to automatically analyze a git branch, make short summaries of changes, suggest review focus areas, and recommend code reviewers.

## Installation

Clone the repo:

```bash
git clone https://github.com/yourusername/code-review-prep.git
cd code-review-prep
```
Create virtual env and activate:
```bash
python3 -m venv venv
source venv/bin/activate  #for macOS/Linux
venv\Scripts\activate     #for Windows
```
Install dependencies:
`pip install -e .[dev]   # installs the CLI and dev dependencies`

Run the CLI tool on any branch:

`review-ready --branch=feature/my-feature --base=main`

Flags:

--branch : branch you want to analyze

--base : base branch to compare against (default: main)

## Development

- Code is organized under `src/`
- Tests are under `tests/`
- Use `black .` for formatting and `flake8 src tests` for linting


## Running Tests

```bash
pytest tests/ --maxfail=1 --disable-warnings -v
