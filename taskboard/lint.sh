#!/bin/bash
# Lint and format-check the project. Needs only python3 and Node (already
# required for `node --test`); npx downloads the pinned tools on first run.
#   ./lint.sh          check only
#   ./lint.sh --fix    apply ESLint fixes and Prettier formatting

ESLINT=eslint@10.12.0
PRETTIER=prettier@3.9.10
PYRIGHT=pyright@1.1.414

cd "$(dirname "$0")" || exit 1

if [ "$1" = "--fix" ]; then
  npx --yes "$ESLINT" --fix .
  npx --yes "$PRETTIER" --write public tests/*.mjs eslint.config.mjs
  exit 0
fi

status=0
echo "== python syntax";   python3 -m compileall -q server.py reset_data.py tests || status=1
echo "== pyright";         npx --yes "$PYRIGHT" || status=1
echo "== eslint";          npx --yes "$ESLINT" . || status=1
echo "== prettier";        npx --yes "$PRETTIER" --check public tests/*.mjs eslint.config.mjs || status=1
exit $status
