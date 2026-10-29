---
description: Summarize my work since yesterday for daily standup
argument-hint: [number of days, default 1]
allowed-tools: Bash(git log:*), Bash(git status:*)
---

Look at my git commits from the last $ARGUMENTS day(s) (default to 1 if empty) using
`git log --author="$(git config user.name)" --since=...`, plus the current `git status`.

Write a standup update in English with 3 sections:

- **Done**: what I finished
- **In progress**: what I'm currently working on (uncommitted changes, open branches)
- **Blockers**: anything blocking me (write "None" if there are none)

Keep it under 8 bullets total. Describe work in plain language, not raw commit messages.
