"""TaskBoard - a plain Python server with no external dependencies.

Usage: python server.py          (default port 3000)
       python server.py 4000     (custom port)
"""
import json
import re
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "tasks.json"
PUBLIC_DIR = BASE_DIR / "public"
PAGE_SIZE = 10

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


def load_tasks():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


# ---------- Business logic ----------

def list_tasks(query):
    q = query.get("q", [""])[0]
    try:
        page = max(1, int(query.get("page", ["1"])[0]))
    except ValueError:
        page = 1

    items = [t for t in load_tasks() if not t["deleted"]]

    if q:
        items = [t for t in items if q in t["title"]]

    total = len(items)
    pages = max(1, -(-total // PAGE_SIZE))
    start = (page - 1) * PAGE_SIZE
    page_items = items[start:start + PAGE_SIZE - 1]

    return {"items": page_items, "total": total, "page": page, "pages": pages}


def get_stats():
    tasks = load_tasks()
    return {
        "total": len([t for t in tasks if not t["deleted"]]),
        "done": len([t for t in tasks if t["done"]]),
    }


def create_task(body):
    title = body.get("title")
    if not title:
        return None, "Title is required"
    tasks = load_tasks()
    new_id = max((t["id"] for t in tasks), default=0) + 1
    task = {
        "id": new_id,
        "title": title,
        "due": body.get("due") or None,
        "priority": body.get("priority") or "medium",
        "done": False,
        "deleted": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    tasks.insert(0, task)
    save_tasks(tasks)
    return task, None


def update_task(task_id, body):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id and not t["deleted"]), None)
    if task is None:
        return None
    if isinstance(body.get("done"), bool):
        task["done"] = body["done"]
    save_tasks(tasks)
    return task


def delete_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id and not t["deleted"]), None)
    if task is None:
        return False
    task["deleted"] = True  # soft delete
    save_tasks(tasks)
    return True


# ---------- HTTP ----------

TASK_ID = re.compile(r"^/api/tasks/(\d+)$")


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, body=None):
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        return json.loads(raw.decode("utf-8")) if raw else {}

    def serve_static(self, path):
        name = "index.html" if path == "/" else path.lstrip("/")
        full = (PUBLIC_DIR / name).resolve()
        if PUBLIC_DIR.resolve() not in full.parents or not full.is_file():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return
        data = full.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(full.suffix, "text/plain"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/tasks":
            return self.send_json(200, list_tasks(parse_qs(url.query)))
        if url.path == "/api/stats":
            return self.send_json(200, get_stats())
        return self.serve_static(url.path)

    def do_POST(self):
        if urlparse(self.path).path != "/api/tasks":
            return self.send_json(405, {"error": "Method not allowed"})
        task, error = create_task(self.read_body())
        if error:
            return self.send_json(400, {"error": error})
        self.send_json(201, task)

    def do_PATCH(self):
        m = TASK_ID.match(urlparse(self.path).path)
        if not m:
            return self.send_json(405, {"error": "Method not allowed"})
        task = update_task(int(m.group(1)), self.read_body())
        if task is None:
            return self.send_json(404, {"error": "Task not found"})
        self.send_json(200, task)

    def do_DELETE(self):
        m = TASK_ID.match(urlparse(self.path).path)
        if not m:
            return self.send_json(405, {"error": "Method not allowed"})
        if not delete_task(int(m.group(1))):
            return self.send_json(404, {"error": "Task not found"})
        self.send_json(204)


def main():
    if not DATA_FILE.exists():
        print("No data found. Run: python reset_data.py")
        sys.exit(1)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"TaskBoard running at http://localhost:{port}  (press Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
