const API_BASE = "/api"; // same host as backend when behind ingress

const taskList = document.getElementById("task-list");
const taskForm = document.getElementById("task-form");
const filters = document.querySelectorAll(".filters button");

let currentStatusFilter = "";

async function fetchTasks() {
  let url = `${API_BASE}/tasks`;
  if (currentStatusFilter) {
    url += `?status=${encodeURIComponent(currentStatusFilter)}`;
  }

  const res = await fetch(url);
  const tasks = await res.json();
  renderTasks(tasks);
}

function renderTasks(tasks) {
  taskList.innerHTML = "";

  if (!tasks.length) {
    taskList.innerHTML = "<p>No tasks yet.</p>";
    return;
  }

  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = "task";

    const left = document.createElement("div");
    const title = document.createElement("div");
    title.textContent = task.title;

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = [
      task.description || "",
      task.due_date ? `Due: ${task.due_date.slice(0, 10)}` : "",
    ]
      .filter(Boolean)
      .join(" • ");

    const badge = document.createElement("span");
    badge.className = `badge ${task.status}`;
    badge.textContent = task.status.replace("_", " ");

    left.appendChild(title);
    left.appendChild(meta);
    left.appendChild(badge);

    const actions = document.createElement("div");
    actions.className = "task-actions";

    if (task.status !== "done") {
      const doneBtn = document.createElement("button");
      doneBtn.className = "mark-done";
      doneBtn.textContent = "Mark done";
      doneBtn.onclick = () => updateTaskStatus(task.id, "done");
      actions.appendChild(doneBtn);
    }

    const delBtn = document.createElement("button");
    delBtn.className = "delete";
    delBtn.textContent = "Delete";
    delBtn.onclick = () => deleteTask(task.id);
    actions.appendChild(delBtn);

    li.appendChild(left);
    li.appendChild(actions);
    taskList.appendChild(li);
  }
}

async function updateTaskStatus(id, status) {
  await fetch(`${API_BASE}/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  fetchTasks();
}

async function deleteTask(id) {
  await fetch(`${API_BASE}/tasks/${id}`, {
    method: "DELETE",
  });
  fetchTasks();
}

taskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const dueDate = document.getElementById("due_date").value;

  if (!title) return;

  await fetch(`${API_BASE}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title,
      description,
      due_date: dueDate ? new Date(dueDate).toISOString() : null,
    }),
  });

  taskForm.reset();
  fetchTasks();
});

filters.forEach((btn) => {
  btn.addEventListener("click", () => {
    filters.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentStatusFilter = btn.dataset.status || "";
    fetchTasks();
  });
});

// initial load
fetchTasks();
