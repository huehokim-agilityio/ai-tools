# Loop check (TaskBoard)

Instructions for each `/loop` run in this repo. Run every command from `taskboard/`.

## 1. Branch state

- `git status -sb`: note uncommitted changes and whether the branch is ahead of or behind its remote.
- `git fetch origin && git log --oneline HEAD..origin/main`: is the branch behind `main`?
  - If it is, report how many commits behind and propose a rebase.
  - Don't rebase, merge or force-push unless the user says so.
- If the branch is `main`, don't commit or push. Report it and stop.

## 2. Tests and lint

```bash
python3 -m unittest discover tests
node --test
./lint.sh
```

- A failing `TB-XXX` test means that ticket is still open. That's expected and isn't a regression.
- On the first run, list the currently failing tests and lint errors as the baseline.
- On later runs, report only new failures: failures not in that baseline, or lint errors in files changed on this branch.
- Never weaken, skip or delete a test to get green.

## 3. PR (needs `gh`, logged in)

- `gh pr view --json number,state,statusCheckRollup,reviewDecision,url`
- Failing CI: read the logs (`gh run view --log-failed`).
  - Flaky failures (timeouts, network): re-run the job at most once. If it fails again, report it instead of re-running.
  - Real failures: reproduce locally and report.
- Unresolved review comments: read them and summarize what has to change.

## Rules

- **Don't fix bugs on your own initiative.** Investigate and propose, and only edit code after the user says "fix it".
- One ticket per `fix/tb-XXX` branch. Commits follow the `commit-format` skill, with no `Co-Authored-By` trailer.
- Don't commit `data/tasks.json` changes produced by `reset_data.py` or by using the app.
- Don't edit `../TICKETS.md` or `screenshots/`.
- Push only when the work clearly continues something the user has already approved.

## Report

- If nothing changed, say so in one sentence.
- If something changed, give a short list of what changed and what needs the user's decision.