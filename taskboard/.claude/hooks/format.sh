#!/bin/bash

# Keep in sync with lint.sh so the hook and the lint check agree on formatting
PRETTIER=prettier@3.9.10

FILE=$(jq -r '.tool_input.file_path // empty')
status=0

# Formatting is best effort: report problems on stderr (exit 1 is non-blocking) instead of failing silently
warn() {
  echo "format.sh: $*" >&2
  status=1
}

case "$FILE" in
  *.py)
    if ! command -v black >/dev/null 2>&1; then
      warn "black is not installed, $FILE was not formatted"
    elif ! out=$(black -q "$FILE" 2>&1); then
      warn "black failed on $FILE: $out"
    fi ;;
  *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.md)
    if ! command -v npx >/dev/null 2>&1; then
      warn "npx is not installed, $FILE was not formatted"
    elif ! out=$(npx --yes "$PRETTIER" --write "$FILE" 2>&1); then
      warn "prettier failed on $FILE: $out"
    fi ;;
esac
exit $status
