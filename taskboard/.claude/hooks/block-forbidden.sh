#!/bin/bash

# Exit 2 blocks the tool call and shows stderr to Claude; exit 0 lets it run

# Fail closed: without jq the command cannot be checked, so block rather than let a force push through
if ! command -v jq >/dev/null 2>&1; then
  echo "block-forbidden.sh: jq is not installed, cannot check the command" >&2
  exit 2
fi

# Join continuation lines (git push origin x \<newline>--force) so grep sees one line
CMD=$(jq -r '.tool_input.command // empty' | tr '\\\n' '  ')

# Block force pushes: --force, --force-with-lease, --force-if-includes, -f (alone or in a short-flag group like -uf), or a +refspec.
# Global options may sit between git and push (git -C dir push, git -c k=v push).
# A + only counts at the start of a refspec; src:+dst is not a force push, so leave that unmatched.
if echo "$CMD" | grep -qE 'git([[:space:]]+-[^[:space:]]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+push([[:space:]]+[^;&|]*)?[[:space:]](--force|-[[:alnum:]]*f[[:alnum:]]*([^[:alnum:]_-]|$)|\+[^[:space:]])'; then
  echo "Force push is not allowed. Rebase or merge onto the remote branch and push normally." >&2
  exit 2
fi
exit 0
