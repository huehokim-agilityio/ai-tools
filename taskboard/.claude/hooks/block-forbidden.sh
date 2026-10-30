#!/bin/bash

CMD=$(jq -r '.tool_input.command // empty')

# Block force pushes: --force, --force-with-lease, --force-if-includes, -f (alone or in a short-flag group like -uf), or a +refspec
if echo "$CMD" | grep -qE 'git[[:space:]]+push([[:space:]]+[^;&|]*)?[[:space:]](--force|-[[:alnum:]]*f[[:alnum:]]*([[:space:]]|$)|\+[^[:space:]])'; then
  echo "Force push is not allowed. Rebase or merge onto the remote branch and push normally." >&2
  exit 2
fi
exit 0
