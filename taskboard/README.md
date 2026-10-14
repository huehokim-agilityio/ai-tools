# TaskBoard

A small task manager app for the **ticket analysis and bug reproduction** workshop.
The server is plain Python using only the standard library, so **no `pip install` is needed**.
The UI is HTML + JavaScript running in the browser.

## Requirements

- Python 3.8 or newer. Check with:
  - macOS / Linux: `python3 --version`
  - Windows: `python --version` (or `py --version`)

## Run the app for the first time

macOS / Linux:

```bash
cd taskboard
python3 reset_data.py     # create sample data (25 tasks)
python3 server.py         # start the server
```

Open in your browser: http://localhost:3000
Stop the server: press `Ctrl + C` in the terminal.
Use another port if 3000 is busy: `python3 server.py 4000`

## Reset the data

Start each reproduction attempt from clean data. Open **a second terminal** and run:

```bash
python3 reset_data.py
```

No need to restart the server; just reload the page.

## Project structure

```
server.py                  API + serves the web page
reset_data.py              creates sample data
public/                    UI (index.html, app.js, style.css)
data/tasks.json            data file (created by reset_data.py)
TICKETS.md                 5 tickets for the workshop
```

## API

| Method | Path                  | Description                            |
| ------ | --------------------- | -------------------------------------- |
| GET    | `/api/tasks?q=&page=` | List tasks (10 per page)               |
| GET    | `/api/stats`          | Completion stats                       |
| POST   | `/api/tasks`          | Create a task `{title, due, priority}` |
| PATCH  | `/api/tasks/:id`      | Mark done `{done: true}`               |
| DELETE | `/api/tasks/:id`      | Delete a task                          |
