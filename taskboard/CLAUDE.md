# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

TaskBoard is a small task manager used for a **ticket analysis and bug reproduction** workshop. The bugs are planted on purpose. The tickets (TB-101 … TB-105) are in `../TICKETS.md`, one level up at the git root (`ai-tools/`). Each fix goes on its own `fix/tb-XXX` branch with a commit like `fix(<area>): <summary> (TB-XXX)` and is merged through a PR.

The project has no dependencies and nothing to build: the server uses only the Python 3.8+ standard library, and the UI is plain HTML and JS with no bundler.

## Commands

Run all commands from `taskboard/`.

```bash
python3 reset_data.py        # (re)create data/tasks.json with 25 seed tasks; due dates are relative to today
python3 server.py [port]     # serve on http://localhost:3000 (or [port]); exits if data/tasks.json is missing
```

`reset_data.py` can run while the server is up. The server reads the JSON file on every request, so reloading the page is enough. Reset before each reproduction attempt.

Tests (regression tests for the ticket fixes):

```bash
python3 -m unittest discover tests                                   # server tests
python3 -m unittest tests.test_server.TestPagination                 # one class
python3 -m unittest tests.test_server.TestPagination.test_<name>     # one test
node --test                                                          # front-end tests (tests/app.test.mjs)
node --test --test-name-pattern "TB-103"                             # filter by name
```

Each test is tagged with its ticket ID. Tests for tickets that are not fixed yet are expected to fail.

Lint (needs only `python3` and Node; `npx` fetches the pinned tools on first run, so there is no `npm install` or `pip install`):

```bash
./lint.sh          # compileall + pyright (Python), eslint + prettier --check (JS/HTML/CSS)
./lint.sh --fix    # apply eslint fixes and prettier formatting
```

Tool versions are pinned in `lint.sh`. Config lives in `eslint.config.mjs` (core rules only, no plugins), `.prettierrc.json` and `pyrightconfig.json`.

## Architecture

- **`server.py`** holds everything on the backend. The file has two sections:
  - **Business logic:** `list_tasks`, `get_stats`, `create_task`, `update_task`, `delete_task`. These are pure functions over the JSON file and are what the Python tests call directly.
  - **HTTP:** a `BaseHTTPRequestHandler` that routes `/api/*` and serves static files from `public/`. Static serving is guarded against path traversal.
  - Routes: `GET /api/tasks?q=&page=`, `GET /api/stats`, `POST /api/tasks {title, due, priority}`, `PATCH /api/tasks/:id {done}`, `DELETE /api/tasks/:id`. Errors return 400/404 with `{error}`.
- **Storage:** `data/tasks.json` is a flat list that is loaded in full and rewritten in full on every call. It has no locking.
  - Deletes are **soft**: they set `deleted: true`. Every read path has to filter deleted tasks out itself, and missing that filter is a common source of bugs.
  - New tasks are inserted at the front of the list, with `id = max + 1`.
  - Task fields are `id`, `title`, `due` (`YYYY-MM-DD` or null), `priority` (high/medium/low), `done`, `deleted` and `createdAt`.
- **Pagination** happens on the server: `PAGE_SIZE = 10`, and the response is `{items, total, page, pages}`. Search is a case-insensitive substring match on `title`.
- **`public/app.js`** is a single browser script with global `state`. It touches the DOM as soon as it loads, so `tests/app.test.mjs` pulls individual pure functions (e.g. `isOverdue`) out of the source with a regex. Keep those functions as top-level `function name(...) {...}` declarations that end with `\n}\n`, or the test extraction breaks.
- **Python tests** patch `server.DATA_FILE` to point at a temp file (see `ServerTestCase`) so they never touch the real data. Build fixtures with `make_task(...)`.

## Conventions

- **Libraries:** standard library only, on both sides. Python uses `http.server`, `json`, `pathlib` and `unittest` (with `unittest.mock`), and the front end uses plain DOM and `fetch`. Don't add pip/npm dependencies or a `package.json`. Lint tools run through `npx` in `lint.sh` and are not dependencies.
- **Naming:**
  - Python: `snake_case` functions, `UPPER_CASE` module constants (`PAGE_SIZE`, `DATA_FILE`). Business functions are named `verb_noun` (`list_tasks`, `create_task`). They return plain data, and the handler maps that to a status: `create_task` → `(task, error)` gives 400, `update_task` → task or `None` gives 404, `delete_task` → `bool` gives 404.
  - JS: `camelCase` functions, `UPPER_CASE` lookup constants (`PRIORITY_LABEL`), and the `$(id)` helper for `getElementById`.
- **Layout:** backend logic stays in `server.py` (no packages/modules), the UI stays in `public/` (`index.html`, `app.js`, `style.css`), and tests go in `tests/` (`test_server.py` for the server, `app.test.mjs` for the front end).
- **Tests:** one `TestXxx(ServerTestCase)` class per ticket, with a docstring starting `TB-XXX:` that states the expected behavior. Methods are named `test_<behavior>`. Node tests are named `'TB-XXX: <behavior>'`.
- **Git:**
  - Branches: `fix/tb-XXX` for ticket fixes, `feat/...` for features.
  - Commits: Conventional Commits `<type>(<scope>): <summary> (TB-XXX)`. The scope is the feature area (`search`, `pagination`, `stats`, `hooks`…), the summary is imperative and lowercase with no period, and the whole subject is ≤ 72 chars. See the `commit-format` skill for full rules.

## Never do

- Don't commit to or push `main`. Merge through a PR.
- Don't fix several tickets on one branch or in one commit. Use one `fix/tb-XXX` branch per ticket.
- Don't commit changes to `data/tasks.json` that come from running `reset_data.py` or from using the app. The file is tracked, but its due dates are relative to the day it was generated.
- Don't edit `../TICKETS.md` or `screenshots/`. They are the workshop's ticket specs and evidence.
- Don't weaken, skip or delete a failing test to get green. A failing `TB-XXX` test means that ticket is still open. Fix the code instead.
- Don't turn soft deletes into hard deletes, and don't add a read path without the `deleted` filter.
- Don't add pip/npm dependencies, a `package.json` or a build step.
- Don't rewrite `public/app.js` functions as arrow functions, methods or classes, because the test extraction breaks (see Architecture).

## Claude Code tooling (`.claude/`)

This config loads only when Claude Code is started from `taskboard/`, because the hooks use `$CLAUDE_PROJECT_DIR`.

- **PostToolUse `format.sh`:** every Edit/Write auto-formats js/mjs/json/css/html/md files with `npx prettier` (`.py` is not formatted, and `data/tasks.json` is skipped). Expect formatting-only diffs, and keep the `app.js` function shape that the tests need.
- **PreToolUse `block-main.sh`:** rejects `git commit`/`git push` while on `main`, plus any Bash command that matches `git push.*(main|master)`, even inside a string such as a test payload. Work on a branch.
- **PreToolUse `block-forbidden.sh`:** rejects force pushes (`--force`, `--force-with-lease`, `-f`, `+refspec`). It only guards Claude's Bash calls, not pushes typed by hand. It matches the command text, so a command that merely mentions a force push (e.g. in a `gh pr create --body`) is blocked too; pass such text through a file (`--body-file`). Without `jq` it blocks every Bash call.
- Also defined: the read-only `code-reviewer` subagent and the `commit-format` skill.
