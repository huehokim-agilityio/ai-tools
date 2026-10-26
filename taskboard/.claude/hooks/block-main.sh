#!/bin/bash

CMD=$(jq -r '.tool_input.command // empty')
BRANCH=$(git -C "$CLAUDE_PROJECT_DIR" branch --show-current 2>/dev/null)

if echo "$CMD" | grep -qE 'git[[:space:]]+push.*(main|master)'; then
  echo "Pushing to main is not allowed. Create a new branch and open a Pull Request." >&2
  exit 2
fi

# Block commit/push while on the main branch
if echo "$CMD" | grep -qE 'git[[:space:]]+(commit|push)' && [ "$BRANCH" = "main" ]; then
  echo "You are on the main branch. Commit/push is not allowed. Create a new branch first: git switch -c branch-name" >&2
  exit 2
fi
exit 0