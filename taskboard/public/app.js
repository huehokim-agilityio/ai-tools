const state = { page: 1, pages: 1, q: '' };

const PRIORITY_LABEL = { high: 'High', medium: 'Medium', low: 'Low' };

const $ = (id) => document.getElementById(id);

function isOverdue(task) {
  if (!task.due || task.done) return false;
  return new Date(task.due) < new Date();
}

function formatDate(iso) {
  if (!iso) return 'No due date';
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y}`;
}

async function loadStats() {
  const res = await fetch('/api/stats');
  const s = await res.json();
  $('stats').textContent = `Completed: ${s.done}/${s.total}`;
}

async function loadTasks() {
  const params = new URLSearchParams({ page: state.page, q: state.q });
  const res = await fetch(`/api/tasks?${params}`);
  const data = await res.json();
  state.pages = data.pages;

  const list = $('list');
  list.innerHTML = '';
  if (data.items.length === 0) {
    list.innerHTML = '<li class="empty">No tasks found.</li>';
  }
  for (const t of data.items) {
    const li = document.createElement('li');
    li.className = 'item' + (t.done ? ' done' : '');
    li.innerHTML = `
      <input type="checkbox" ${t.done ? 'checked' : ''} />
      <div class="info">
        <span class="title"></span>
        <span class="meta">
          <span class="badge ${t.priority}">${PRIORITY_LABEL[t.priority] || t.priority}</span>
          ${formatDate(t.due)}
          ${isOverdue(t) ? '<span class="overdue">Overdue</span>' : ''}
        </span>
      </div>
      <button class="delete" title="Delete">✕</button>`;
    li.querySelector('.title').textContent = t.title;
    li.querySelector('input').addEventListener('change', (e) => toggle(t.id, e.target.checked));
    li.querySelector('.delete').addEventListener('click', () => remove(t.id));
    list.appendChild(li);
  }

  $('page-info').textContent = `Page ${data.page}/${data.pages} · ${data.total} tasks`;
  $('prev').disabled = data.page <= 1;
  $('next').disabled = data.page >= data.pages;
}

async function refresh() {
  await Promise.all([loadTasks(), loadStats()]);
}

async function toggle(id, done) {
  await fetch(`/api/tasks/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ done }),
  });
  refresh();
}

async function remove(id) {
  if (!confirm('Delete this task?')) return;
  await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  refresh();
}

$('add-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  $('error').textContent = '';
  const res = await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: $('title').value,
      due: $('due').value || null,
      priority: $('priority').value,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    $('error').textContent = err.error;
    return;
  }
  $('title').value = '';
  $('due').value = '';
  state.page = 1;
  refresh();
});

let searchTimer;
$('search').addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.q = e.target.value;
    state.page = 1;
    loadTasks();
  }, 250);
});

$('prev').addEventListener('click', () => { state.page--; loadTasks(); });
$('next').addEventListener('click', () => { state.page++; loadTasks(); });

refresh();
