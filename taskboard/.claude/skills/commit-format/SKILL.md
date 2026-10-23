---
name: commit-format
description: Writes git commit messages in this repo's Conventional Commits format with a TB ticket ID, e.g. "fix(search): make task search case-insensitive (TB-101)". Use when asked to commit, write or fix a commit message, or check whether a commit message follows the convention.
---

# Commit message format

Every commit in this repo follows Conventional Commits with the ticket ID at the end of the subject:

```
<type>(<scope>): <summary> (<TICKET>)

<body: why the change was needed and what it does, wrapped at 72 chars>

<footer>
```

Examples from history:

```
fix(search): make task search case-insensitive (TB-101)
fix(pagination): show all tasks on each page (TB-102)
```

## Subject line

- **type** — one of:
  - `feat` new user-facing behavior
  - `fix` bug fix
  - `refactor` code change with no behavior change
  - `test` adding or fixing tests only
  - `docs` README, TICKETS.md, CLAUDE.md, comments
  - `style` formatting only
  - `perf` performance improvement
  - `chore` tooling, config, data reset scripts, `.claude/` files
- **scope** — the area touched, lowercase, one word. Prefer the feature over the file: `search`, `pagination`, `tasks`, `stats`, `delete`, `due-date`, `ui`, `server`, `tests`. Omit the parentheses only if the change truly spans everything.
- **summary** — imperative mood ("make", "show", "add" — not "made", "fixes"), lowercase first letter, no trailing period, describes the effect for the user rather than the code mechanics.
- **ticket** — `(TB-<number>)` when the work belongs to a ticket in `TICKETS.md`. Take it from the branch name (`fix/tb-102` → `TB-102`) or the conversation. If there is no ticket, leave it off rather than inventing one.
- Whole subject ≤ 72 characters.

## Body

Add a body whenever the change is not obvious from the subject (always for `fix`):

- Line 1–2: the cause — what was wrong and why (e.g. "Search compared the raw query against titles, so 'weekly' did not match 'Weekly report'.").
- Then: what the change does, and any test added.
- Wrap at 72 characters. Separate from the subject with a blank line.

## Footer

- `BREAKING CHANGE: <what breaks>` if an API response or data format changes (add `!` after the type/scope too: `feat(tasks)!: ...`).
- Keep any attribution trailer (e.g. `Co-Authored-By:`) that the session requires, as the last line.

## Workflow

1. Run `git status` and `git diff --staged` (or `git diff` if nothing is staged) to see what is actually being committed. Base the message on the diff, not on memory of the conversation.
2. If the diff mixes unrelated changes (e.g. a bug fix plus an unrelated refactor), suggest splitting into separate commits.
3. Do not stage unrelated files such as `__pycache__/` or local data.
4. Draft the message following the rules above and show it to the user.
5. Only run `git commit` when the user asked to commit. Pass the message with a heredoc so line breaks survive:

   ```bash
   git commit -F - <<'EOF'
   fix(pagination): show all tasks on each page (TB-102)

   Pages were sliced before deleted tasks were filtered out, so pages
   with deleted tasks showed fewer than 10 items and tasks were skipped.
   Filter first, then paginate. Add a test covering deleted tasks.
   EOF
   ```

6. When asked to check an existing message, list each rule it breaks and give a corrected version.
