# Contributing

## Setup

```bash
pdm install
```

`pdm install` installs all dependencies and automatically registers the pre-commit hooks via a post-install script. You don't need to run `pre-commit install` manually. Ruff and Pyright will run automatically on every commit.

## Workflow

- Branch off `main` for every change
- Open a PR — CI must pass and the branch must be up to date with `main` before merging
- One approval required to merge

## Commands

```bash
pdm run test          # run tests with coverage report
pdm run view-coverage # open HTML coverage report in browser
pdm run lint          # lint and autofix
pdm run typecheck     # run Pyright
pdm run format        # format
```
