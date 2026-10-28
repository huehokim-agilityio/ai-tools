// Regression tests for the front-end bug fixes.
// Run from the taskboard folder:  node --test
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// app.js is a plain browser script that touches the DOM on load, so pull out
// just the pure function under test instead of running the whole file.
const source = readFileSync(new URL('../public/app.js', import.meta.url), 'utf8');
const match = source.match(/function isOverdue\([\s\S]*?\n}\n/);
assert.ok(match, 'isOverdue() not found in public/app.js');
const isOverdue = new Function(`${match[0]}; return isOverdue;`)();

// Local calendar date offset by `days`, as 'YYYY-MM-DD' (the format <input type="date"> produces).
function localDay(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// TB-103: a task due today must not be shown as overdue.
test('TB-103: task due today is not overdue', () => {
  assert.equal(isOverdue({ due: localDay(0), done: false }), false);
});

test('TB-103: task due yesterday is overdue', () => {
  assert.equal(isOverdue({ due: localDay(-1), done: false }), true);
});

test('TB-103: task due tomorrow is not overdue', () => {
  assert.equal(isOverdue({ due: localDay(1), done: false }), false);
});

test('TB-103: finished or undated tasks are never overdue', () => {
  assert.equal(isOverdue({ due: localDay(-1), done: true }), false);
  assert.equal(isOverdue({ due: null, done: false }), false);
});
