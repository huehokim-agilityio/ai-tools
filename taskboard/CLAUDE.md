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

Each test class and test name is tagged with its ticket ID. Tests for tickets that are not fixed yet are expected to fail.

## Architecture

- **`server.py`** holds everything on the backend. The file has two sections:
  - **Business logic:** `list_tasks`, `get_stats`, `create_task`, `update_task`, `delete_task`. These are pure functions over the JSON file and are what the Python tests call directly.
  - **HTTP:** a `BaseHTTPRequestHandler` that routes `/api/*` and serves static files from `public/`. Static serving is guarded against path traversal.
- **Storage:** `data/tasks.json` is a flat list that is loaded in full and rewritten in full on every call. It has no locking.
  - Deletes are **soft**: they set `deleted: true`. Every read path has to filter deleted tasks out itself, and missing that filter is a common source of bugs.
  - New tasks are inserted at the front of the list, with `id = max + 1`.
  - Task fields are `id`, `title`, `due` (`YYYY-MM-DD` or null), `priority` (high/medium/low), `done`, `deleted` and `createdAt`.
- **Pagination** happens on the server: `PAGE_SIZE = 10`, and the response is `{items, total, page, pages}`. Search is a case-insensitive substring match on `title`.
- **`public/app.js`** is a single browser script with global `state`. It touches the DOM as soon as it loads, so `tests/app.test.mjs` pulls individual pure functions (e.g. `isOverdue`) out of the source with a regex. Keep those functions as top-level `function name(...) {...}` declarations that end with `\n}\n`, or the test extraction breaks.
- **Python tests** patch `server.DATA_FILE` to point at a temp file (see `ServerTestCase`) so they never touch the real data. Build fixtures with `make_task(...)`.
