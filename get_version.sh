#!/bin/sh

git describe --tags --dirty --abbrev=6 2>/dev/null || \
  python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"
