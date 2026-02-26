# Releasing a New PyPI Package Version

## Prerequisites

Install the build and upload tools:

```sh
pip install build twine
```

You will also need a PyPI account with upload rights to the `sapcli` project.

## Automated steps (steps 1–5)

Steps 1–5 below are fully automated by one of three Makefile targets.
The target computes the next version from `pyproject.toml`, patches both
`pyproject.toml` and `sap/cli/_entry.py`, runs the full `check` suite, commits
the result, and creates the git tag.

| Command | Increments | Example: `1.2.3` → |
|---|---|---|
| `make release-major` | MAJOR, resets MINOR and PATCH to 0 | `2.0.0` |
| `make release-minor` | MINOR, resets PATCH to 0 | `1.3.0` |
| `make release-fix` | PATCH only | `1.2.4` |

If `make check` fails the process stops before any commit or tag is created,
so the working tree is left with the version files already patched — fix the
issue, reset the two files, and re-run the target.

## Steps

### 1. Update the version in `pyproject.toml`

Edit the `version` field in `pyproject.toml`:

```toml
[project]
version = "X.Y.Z"
```

### 2. Update the fallback version in the entry point

Patch `_FALLBACK_VERSION` in `sap/cli/_entry.py` to match:

```python
_FALLBACK_VERSION = 'X.Y.Z'
```

### 3. Run the test suite

```sh
make check
```

All tests and linters must pass before proceeding.

### 4. Commit the version bump

```sh
git add pyproject.toml sap/cli/_entry.py
git commit -m "release: bump version to X.Y.Z"
```

### 5. Tag the release

```sh
git tag X.Y.Z
```

The tag is used by `get_version.sh` to derive the runtime version string reported by
`sapcli --version`.

### 6. Build the distribution packages

```sh
python -m build
```

This produces two files under `dist/`:

- `sapcli-X.Y.Z.tar.gz` — source distribution
- `sapcli-X.Y.Z-py3-none-any.whl` — wheel

### 7. Upload to PyPI

```sh
twine upload dist/sapcli-X.Y.Z*
```

Enter your PyPI credentials when prompted, or configure them in `~/.pypirc`.

### 8. Push the commit and tag

```sh
git push origin master
git push origin X.Y.Z
```

## Verify the release

Install the newly published package in a clean environment and check the version:

```sh
pip install --upgrade sapcli
sapcli --version
```

## Version scheme

The project follows a simple `MAJOR.MINOR.PATCH` scheme. Choose the next version
according to the scope of changes since the last release:

| Change type | Component to increment |
|---|---|
| Breaking / incompatible change | MAJOR |
| New backwards-compatible feature | MINOR |
| Bug fix or documentation update | PATCH |
