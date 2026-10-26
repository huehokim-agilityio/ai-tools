#!/bin/bash

FILE=$(jq -r '.tool_input.file_path // empty')

case "$FILE" in
  *.py)
    black -q "$FILE" ;;
  *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.md)
    npx prettier --write "$FILE" >/dev/null 2>&1 ;;
esac
exit 0