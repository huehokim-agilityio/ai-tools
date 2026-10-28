"""Regression tests for the server-side bug fixes.

Run from the taskboard folder:  python3 -m unittest discover tests
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import server  # noqa: E402


def make_task(task_id, title, done=False, deleted=False):
    return {
        "id": task_id,
        "title": title,
        "due": None,
        "priority": "medium",
        "done": done,
        "deleted": deleted,
        "createdAt": "2026-10-01T00:00:00+00:00",
    }


class ServerTestCase(unittest.TestCase):
    """Points server.DATA_FILE at a temporary file so tests never touch real data."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data_file = Path(tmp.name) / "tasks.json"
        patcher = mock.patch.object(server, "DATA_FILE", self.data_file)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write_tasks(self, tasks):
        self.data_file.write_text(json.dumps(tasks), encoding="utf-8")

    def read_tasks(self):
        return json.loads(self.data_file.read_text(encoding="utf-8"))


class TestSearchCaseInsensitive(ServerTestCase):
    """TB-101: search must ignore letter case."""

    def setUp(self):
        super().setUp()
        self.write_tasks([
            make_task(1, "Weekly Report"),
            make_task(2, "Sprint planning"),
        ])

    def titles(self, q):
        return [t["title"] for t in server.list_tasks({"q": [q]})["items"]]

    def test_lowercase_query_matches_capitalised_title(self):
        self.assertEqual(self.titles("weekly"), ["Weekly Report"])

    def test_uppercase_query_matches_lowercase_title(self):
        self.assertEqual(self.titles("PLANNING"), ["Sprint planning"])

    def test_non_matching_query_returns_nothing(self):
        self.assertEqual(self.titles("budget"), [])


class TestPagination(ServerTestCase):
    """TB-102: every page must show PAGE_SIZE tasks, none skipped."""

    def setUp(self):
        super().setUp()
        self.write_tasks([make_task(i, f"Task {i}") for i in range(1, 26)])

    def page(self, n):
        return server.list_tasks({"page": [str(n)]})

    def test_full_page_has_page_size_items(self):
        self.assertEqual(len(self.page(1)["items"]), server.PAGE_SIZE)

    def test_all_tasks_appear_exactly_once_across_pages(self):
        first = self.page(1)
        self.assertEqual(first["pages"], 3)
        ids = [t["id"] for n in range(1, first["pages"] + 1) for t in self.page(n)["items"]]
        self.assertEqual(ids, list(range(1, 26)))


class TestStatsIgnoreDeleted(ServerTestCase):
    """TB-104: deleted tasks must not count towards Completed."""

    def test_deleted_done_task_not_counted(self):
        self.write_tasks([
            make_task(1, "Done", done=True),
            make_task(2, "Open"),
            make_task(3, "Done then deleted", done=True, deleted=True),
        ])
        self.assertEqual(server.get_stats(), {"total": 2, "done": 1})

    def test_done_never_exceeds_total(self):
        self.write_tasks([make_task(1, "Gone", done=True, deleted=True)])
        stats = server.get_stats()
        self.assertLessEqual(stats["done"], stats["total"])


class TestRejectBlankTitles(ServerTestCase):
    """TB-105: blank titles (incl. whitespace / zero-width only) are rejected."""

    def setUp(self):
        super().setUp()
        self.write_tasks([])

    def assert_rejected(self, title):
        task, error = server.create_task({"title": title})
        self.assertIsNone(task)
        self.assertEqual(error, "Title is required")
        self.assertEqual(self.read_tasks(), [], "nothing should be saved")

    def test_missing_title(self):
        task, error = server.create_task({})
        self.assertIsNone(task)
        self.assertEqual(error, "Title is required")

    def test_empty_title(self):
        self.assert_rejected("")

    def test_whitespace_only_title(self):
        self.assert_rejected("   \t\n ")

    def test_zero_width_only_title(self):
        self.assert_rejected("​‌‍⁠﻿")

    def test_zero_width_mixed_with_spaces(self):
        self.assert_rejected(" ​ ﻿ ")

    def test_valid_title_is_trimmed_and_saved(self):
        task, error = server.create_task({"title": "  Buy milk​  "})
        self.assertIsNone(error)
        self.assertEqual(task["title"], "Buy milk")
        self.assertEqual([t["title"] for t in self.read_tasks()], ["Buy milk"])


if __name__ == "__main__":
    unittest.main()
