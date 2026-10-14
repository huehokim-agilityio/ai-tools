"""Reset the sample data in data/tasks.json.

Due dates are relative to today, so the data always looks fresh.
Usage: python reset_data.py
"""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "tasks.json"

# (title, due date offset in days from today, priority, done)
SEED = [
    ("Weekly report for team lead", 0, "high", False),
    ("Sprint planning meeting", 1, "high", False),
    ("Update API documentation", 3, "medium", False),
    ("Review Lan's pull request", 0, "medium", True),
    ("Fix mobile login issue", -2, "high", False),
    ("Write tests for payment module", 5, "medium", False),
    ("Send monthly invoice to client", 2, "low", True),
    ("Clean up the backlog", 7, "low", False),
    ("Prepare client demo", 4, "high", False),
    ("Check server logs", -1, "medium", True),
    ("Book meeting room for Friday", 2, "low", False),
    ("Q3 expense report", 10, "medium", False),
    ("Upgrade frontend libraries", 14, "low", False),
    ("Interview QA candidate", 1, "high", True),
    ("Write onboarding guide", 6, "medium", False),
    ("Back up the database", 0, "high", False),
    ("Run user feedback survey", 9, "low", False),
    ("Design settings screen", 8, "medium", True),
    ("Optimize homepage load time", 12, "medium", False),
    ("Call the supplier", -3, "low", False),
    ("Schedule internal training", 11, "low", False),
    ("Test release 2.1", 3, "high", False),
    ("Update price list", 15, "medium", True),
    ("Reply to customer emails", 0, "medium", False),
    ("Sprint retro summary", 5, "low", False),
]


def main():
    today = date.today()
    now = datetime.now(timezone.utc).isoformat()
    tasks = [
        {
            "id": i + 1,
            "title": title,
            "due": (today + timedelta(days=offset)).isoformat(),
            "priority": priority,
            "done": done,
            "deleted": False,
            "createdAt": now,
        }
        for i, (title, offset, priority, done) in enumerate(SEED)
    ]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    print(f"Created {len(tasks)} sample tasks in data/tasks.json")


if __name__ == "__main__":
    main()
