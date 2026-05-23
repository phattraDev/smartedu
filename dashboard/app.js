/**
 * School Bot Dashboard — Frontend Logic
 * Communicates with the FastAPI backend at API_BASE.
 */

const API_BASE = window.location.protocol === "file:"
  ? "http://localhost:8000"
  : window.location.origin;

// ── State ──────────────────────────────────────────────────────────────────
let authToken = localStorage.getItem("token") || null;
let userRole = localStorage.getItem("role") || null;
let classes = [];

// ── Modal (replaces window.confirm / alert) ────────────────────────────────

function showModal({ title, message, type = "danger", confirmText = "Confirm", cancelText = "Cancel", onConfirm, onCancel }) {
  const overlay  = document.getElementById("modal-overlay");
  const iconWrap = document.getElementById("modal-icon-wrap");
  const icon     = document.getElementById("modal-icon");
  const titleEl  = document.getElementById("modal-title");
  const msgEl    = document.getElementById("modal-message");
  const confirmBtn = document.getElementById("modal-confirm");
  const cancelBtn  = document.getElementById("modal-cancel");

  const icons = {
    danger:  '<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>',
    warning: '<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>',
    info:    '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>',
  };

  const btnColors = { danger: "btn-danger", warning: "btn-primary", info: "btn-primary" };

  iconWrap.className = `modal-icon-wrap ${type}`;
  icon.innerHTML = icons[type] || icons.info;
  titleEl.textContent = title;
  msgEl.textContent = message;
  confirmBtn.textContent = confirmText;
  confirmBtn.className = `btn ${btnColors[type] || "btn-primary"}`;
  cancelBtn.textContent = cancelText;

  overlay.classList.remove("hidden");

  const close = () => overlay.classList.add("hidden");

  confirmBtn.onclick = () => { close(); onConfirm && onConfirm(); };
  cancelBtn.onclick  = () => { close(); onCancel && onCancel(); };
  overlay.onclick    = (e) => { if (e.target === overlay) { close(); onCancel && onCancel(); } };
}

// ── Toast notifications ────────────────────────────────────────────────────

function showToast(message, type = "success", duration = 3500) {
  const container = document.getElementById("toast-container");
  const icons = {
    success: '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>',
    error:   '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>',
    info:    '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>',
  };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">${icons[type]||icons.info}</svg><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ── Helpers ────────────────────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;
  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (resp.status === 401) {
    logout();
    throw new Error("Session expired. Please log in again.");
  }
  return resp;
}

function showMsg(elementId, text, type = "success") {
  const el = document.getElementById(elementId);
  el.textContent = text;
  el.className = `msg ${type}`;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 4000);
}

function formatDate(isoString) {
  if (!isoString) return "—";
  return new Date(isoString).toLocaleDateString("en-GB", {
    day: "numeric", month: "short", year: "numeric",
  });
}

// ── Auth ───────────────────────────────────────────────────────────────────

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("login-btn");
  const errEl = document.getElementById("login-error");
  btn.disabled = true;
  btn.textContent = "Signing in…";
  errEl.classList.add("hidden");

  const body = new URLSearchParams({
    username: document.getElementById("username").value.trim(),
    password: document.getElementById("password").value.trim(),
  });

  try {
    const resp = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!resp.ok) {
      const data = await resp.json();
      errEl.textContent = data.detail || "Invalid credentials";
      errEl.classList.remove("hidden");
      return;
    }
    const data = await resp.json();
    authToken = data.access_token;
    userRole = data.role;
    localStorage.setItem("token", authToken);
    localStorage.setItem("role", userRole);
    enterDashboard();
  } catch {
    errEl.textContent = "Could not connect to server. Is the backend running?";
    errEl.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "Sign In";
  }
});

function logout() {
  authToken = null;
  userRole = null;
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  document.getElementById("dashboard-screen").classList.remove("active");
  document.getElementById("login-screen").classList.add("active");
}

document.getElementById("logout-btn").addEventListener("click", logout);

// ── Dashboard init ─────────────────────────────────────────────────────────

function enterDashboard() {
  document.getElementById("login-screen").classList.remove("active");
  document.getElementById("dashboard-screen").classList.add("active");

  const username = userRole === "admin" ? "Admin" : "Teacher";
  document.getElementById("user-label").textContent = username;
  document.getElementById("user-avatar").textContent = username[0].toUpperCase();

  // Hide admin-only nav items for teachers
  if (userRole !== "admin") {
    document.querySelectorAll('[data-tab="broadcast"], [data-tab="classes"], [data-tab="users"]').forEach(el => {
      el.style.display = "none";
    });
  }

  loadStats();
  loadClasses();
  loadHomework();
  loadHolidays();
  if (userRole === "admin") {
    loadBroadcastHistory();
    loadUsers();
  }
}

// Auto-login if token exists
if (authToken) enterDashboard();

// ── Tab navigation ─────────────────────────────────────────────────────────

const TAB_TITLES = {
  homework: "Homework",
  holidays: "Holidays",
  broadcast: "Broadcast",
  classes: "Classes",
  users: "Users",
};

document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    document.getElementById("topbar-title").textContent = TAB_TITLES[btn.dataset.tab] || "";
  });
});

// ── Stats ──────────────────────────────────────────────────────────────────

async function loadStats() {
  try {
    const [subResp, clsResp] = await Promise.all([
      apiFetch("/api/subscribers/count"),
      apiFetch("/api/classes"),
    ]);
    if (subResp.ok) {
      const d = await subResp.json();
      document.getElementById("stat-subscribers").textContent = d.count;
    }
    if (clsResp.ok) {
      const d = await clsResp.json();
      document.getElementById("stat-classes").textContent = d.length;
    }
  } catch { /* silent */ }
}

// ── Classes ────────────────────────────────────────────────────────────────

async function loadClasses() {
  try {
    const resp = await apiFetch("/api/classes");
    if (!resp.ok) return;
    classes = await resp.json();
    renderClasses();
    populateClassSelects();
  } catch { /* silent */ }
}

function renderClasses() {
  const container = document.getElementById("classes-list");
  if (!classes.length) {
    container.innerHTML = '<p class="empty-state">No classes yet. Add one above.</p>';
    return;
  }
  container.innerHTML = classes.map(c => `
    <div class="item-card">
      <div class="item-body">
        <div class="item-title">
          <span class="badge badge-violet">${c.code}</span>
          ${c.name}
        </div>
        <div class="item-meta">Added ${formatDate(c.created_at)}</div>
      </div>
      ${userRole === "admin" ? `<button class="btn btn-ghost-red" onclick="deleteClass(${c.id})">Delete</button>` : ""}
    </div>
  `).join("");
}

function populateClassSelects() {
  const selects = ["hw-class", "hw-filter-class"];
  selects.forEach(id => {
    const sel = document.getElementById(id);
    const current = sel.value;
    sel.innerHTML = id === "hw-filter-class"
      ? '<option value="">All classes</option>'
      : '<option value="">Select class…</option>';
    classes.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.code;
      opt.textContent = `${c.name} (${c.code})`;
      sel.appendChild(opt);
    });
    if (current) sel.value = current;
  });
}

document.getElementById("class-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById("cls-name").value.trim(),
    code: document.getElementById("cls-code").value.trim().toUpperCase(),
  };
  try {
    const resp = await apiFetch("/api/classes", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) { showMsg("cls-msg", data.detail || "Error", "error"); return; }
    showMsg("cls-msg", `Class "${data.name}" added successfully.`, "success");
    e.target.reset();
    loadClasses();
    loadStats();
  } catch {
    showMsg("cls-msg", "Connection error.", "error");
  }
});

async function deleteClass(id) {
  showModal({
    title: "Delete Class",
    message: "This will permanently delete the class and all its homework. This cannot be undone.",
    type: "danger",
    confirmText: "Delete",
    onConfirm: async () => {
      try {
        await apiFetch(`/api/classes/${id}`, { method: "DELETE" });
        showToast("Class deleted.", "success");
        loadClasses();
        loadStats();
      } catch { showToast("Error deleting class.", "error"); }
    }
  });
}

// ── Homework ───────────────────────────────────────────────────────────────

async function loadUsers() {
  if (userRole !== "admin") return;

  const container = document.getElementById("users-list");
  container.innerHTML = '<p class="empty-state">Loading users...</p>';

  try {
    const resp = await apiFetch("/api/subscribers");
    const users = resp.ok ? await resp.json() : [];
    const active = users.filter(u => u.is_active).length;
    const inactive = users.length - active;

    document.getElementById("users-total").textContent = users.length;
    document.getElementById("users-active").textContent = active;
    document.getElementById("users-inactive").textContent = inactive;
    document.getElementById("stat-subscribers").textContent = active;

    if (!users.length) {
      container.innerHTML = '<p class="empty-state">No Telegram users have started the bot yet.</p>';
      return;
    }

    container.innerHTML = users.map(user => {
      const name = escapeHtml(user.first_name || "Unknown user");
      const username = user.username ? `@${escapeHtml(user.username)}` : "No username";
      const classCode = user.class_code ? escapeHtml(user.class_code) : "No class";
      const language = escapeHtml((user.language || "en").toUpperCase());
      const statusClass = user.is_active ? "badge-emerald" : "badge-amber";
      const statusText = user.is_active ? "Active" : "Inactive";

      return `
        <div class="item-card">
          <div class="item-body">
            <div class="item-title">
              <span class="badge ${statusClass}">${statusText}</span>
              ${name}
            </div>
            <div class="item-meta">
              Telegram ID: <strong>${escapeHtml(user.telegram_id)}</strong>
              <span class="dot">Â·</span>
              ${username}
              <span class="dot">Â·</span>
              Class: <strong>${classCode}</strong>
              <span class="dot">Â·</span>
              Language: <strong>${language}</strong>
              <span class="dot">Â·</span>
              Joined ${formatDate(user.subscribed_at)}
            </div>
          </div>
        </div>
      `;
    }).join("");
  } catch {
    container.innerHTML = '<p class="empty-state">Failed to load users.</p>';
  }
}

async function loadHomework(classCode = "") {
  const container = document.getElementById("homework-list");
  container.innerHTML = '<p class="empty-state">Loading…</p>';
  try {
    const path = classCode ? `/api/homework/${classCode}` : "/api/homework/ALL";
    // If no filter, load for each class and merge
    let allHw = [];
    if (!classCode) {
      const results = await Promise.all(
        classes.map(c => apiFetch(`/api/homework/${c.code}`).then(r => r.ok ? r.json() : []))
      );
      allHw = results.flat().sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else {
      const resp = await apiFetch(`/api/homework/${classCode}`);
      allHw = resp.ok ? await resp.json() : [];
    }

    if (!allHw.length) {
      container.innerHTML = '<p class="empty-state">No homework submissions found.</p>';
      return;
    }

    container.innerHTML = allHw.map(hw => `
      <div class="item-card">
        <div class="item-body">
          <div class="item-title">
            <span class="badge badge-indigo">${hw.subject}</span>
            ${hw.description}
          </div>
          <div class="item-meta">
            Due: <strong>${hw.due_date}</strong>
            <span class="dot">·</span>
            ${hw.submitted_by}
            <span class="dot">·</span>
            ${formatDate(hw.created_at)}
            ${hw.file_name ? `<span class="dot">·</span> <a href="${hw.file_url}" target="_blank" class="file-link">📎 ${hw.file_name}</a>` : ""}
          </div>
        </div>
        <button class="btn btn-ghost-red" onclick="deleteHomework(${hw.id})">Delete</button>
      </div>
    `).join("");
  } catch {
    container.innerHTML = '<p class="empty-state">Failed to load homework.</p>';
  }
}

document.getElementById("hw-filter-class").addEventListener("change", (e) => {
  loadHomework(e.target.value);
});

document.getElementById("homework-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("hw-file");
  const formData = new FormData();
  formData.append("class_code", document.getElementById("hw-class").value);
  formData.append("subject", document.getElementById("hw-subject").value.trim());
  formData.append("description", document.getElementById("hw-description").value.trim());
  formData.append("due_date", document.getElementById("hw-due").value.trim());
  formData.append("submitted_by", document.getElementById("hw-teacher").value.trim());
  if (fileInput.files[0]) {
    formData.append("file", fileInput.files[0]);
  }
  try {
    const headers = {};
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;
    const resp = await fetch(`${API_BASE}/api/homework`, {
      method: "POST",
      headers,
      body: formData,
    });
    const data = await resp.json();
    if (!resp.ok) { showMsg("hw-msg", data.detail || "Error", "error"); return; }
    showMsg("hw-msg", "Homework submitted successfully.", "success");
    e.target.reset();
    document.getElementById("file-preview").classList.add("hidden");
    loadHomework(document.getElementById("hw-filter-class").value);
  } catch {
    showMsg("hw-msg", "Connection error.", "error");
  }
});

async function deleteHomework(id) {
  showModal({
    title: "Delete Homework",
    message: "This homework entry will be permanently removed.",
    type: "danger",
    confirmText: "Delete",
    onConfirm: async () => {
      try {
        await apiFetch(`/api/homework/${id}`, { method: "DELETE" });
        showToast("Homework deleted.", "success");
        loadHomework(document.getElementById("hw-filter-class").value);
      } catch { showToast("Error deleting homework.", "error"); }
    }
  });
}

// ── Holidays ───────────────────────────────────────────────────────────────

async function loadHolidays() {
  const container = document.getElementById("holidays-list");
  try {
    const resp = await apiFetch("/api/holidays");
    const holidays = resp.ok ? await resp.json() : [];
    if (!holidays.length) {
      container.innerHTML = '<p class="empty-state">No holidays scheduled.</p>';
      return;
    }
    container.innerHTML = holidays.map(h => `
      <div class="item-card">
        <div class="item-body">
          <div class="item-title">
            <span class="badge badge-emerald">Holiday</span>
            ${h.title}
          </div>
          <div class="item-meta">
            ${h.start_date === h.end_date ? h.start_date : `${h.start_date} → ${h.end_date}`}
            ${h.reason ? `<span class="dot">·</span> ${h.reason}` : ""}
          </div>
        </div>
        ${userRole === "admin" ? `<button class="btn btn-ghost-red" onclick="deleteHoliday(${h.id})">Delete</button>` : ""}
      </div>
    `).join("");
  } catch {
    container.innerHTML = '<p class="empty-state">Failed to load holidays.</p>';
  }
}

document.getElementById("holiday-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    title: document.getElementById("hol-title").value.trim(),
    start_date: document.getElementById("hol-start").value,
    end_date: document.getElementById("hol-end").value,
    reason: document.getElementById("hol-reason").value.trim() || null,
  };
  try {
    const resp = await apiFetch("/api/holidays", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) { showMsg("hol-msg", data.detail || "Error", "error"); return; }
    showMsg("hol-msg", "Holiday added successfully.", "success");
    e.target.reset();
    loadHolidays();
  } catch {
    showMsg("hol-msg", "Connection error.", "error");
  }
});

async function deleteHoliday(id) {
  showModal({
    title: "Delete Holiday",
    message: "This holiday will be removed from the schedule.",
    type: "danger",
    confirmText: "Delete",
    onConfirm: async () => {
      try {
        await apiFetch(`/api/holidays/${id}`, { method: "DELETE" });
        showToast("Holiday deleted.", "success");
        loadHolidays();
      } catch { showToast("Error deleting holiday.", "error"); }
    }
  });
}

// ── Broadcast ──────────────────────────────────────────────────────────────

document.getElementById("bc-message").addEventListener("input", (e) => {
  document.getElementById("bc-char-count").textContent = e.target.value.length;
});

document.getElementById("broadcast-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = document.getElementById("bc-message").value.trim();
  if (!message) return;

  showModal({
    title: "Send Broadcast",
    message: `Send this message to ALL subscribers?\n\n"${message.substring(0, 80)}${message.length > 80 ? '…' : ''}"`,
    type: "warning",
    confirmText: "Send Now",
    onConfirm: async () => {
      const btn = document.querySelector("#broadcast-form button[type=submit]");
      btn.disabled = true;
      btn.textContent = "Sending…";
      try {
        const resp = await apiFetch("/api/broadcast", {
          method: "POST",
          body: JSON.stringify({ message }),
        });
        const data = await resp.json();
        if (!resp.ok) { showToast(data.detail || "Error sending broadcast.", "error"); return; }
        showToast(`✅ Sent to ${data.sent_to} subscriber(s).`, "success", 5000);
        e.target.reset();
        document.getElementById("bc-char-count").textContent = "0";
        loadBroadcastHistory();
      } catch {
        showToast("Connection error.", "error");
      } finally {
        btn.disabled = false;
        btn.textContent = "Send to All Subscribers";
      }
    }
  });
});

async function loadBroadcastHistory() {
  const container = document.getElementById("broadcast-history");
  try {
    const resp = await apiFetch("/api/broadcast/history");
    const logs = resp.ok ? await resp.json() : [];
    if (!logs.length) {
      container.innerHTML = '<p class="empty-state">No broadcasts sent yet.</p>';
      return;
    }
    container.innerHTML = logs.map(l => `
      <div class="item-card">
        <div class="item-body">
          <div class="item-title">
            <span class="badge badge-amber">${l.recipient_count} sent</span>
            ${l.message}
          </div>
          <div class="item-meta">
            By ${l.sent_by}
            <span class="dot">·</span>
            ${formatDate(l.sent_at)}
          </div>
        </div>
      </div>
    `).join("");
  } catch {
    container.innerHTML = '<p class="empty-state">Failed to load history.</p>';
  }
}

async function clearBroadcastHistory() {
  showModal({
    title: "Clear Broadcast History",
    message: "All broadcast history will be permanently deleted. This cannot be undone.",
    type: "danger",
    confirmText: "Clear All",
    onConfirm: async () => {
      try {
        const resp = await apiFetch("/api/broadcast/history", { method: "DELETE" });
        if (!resp.ok) { showToast("Failed to clear history.", "error"); return; }
        showToast("Broadcast history cleared.", "success");
        loadBroadcastHistory();
      } catch { showToast("Connection error.", "error"); }
    }
  });
}

// ── File drop zone ────────────────────────────────────────────────────────

const fileDrop = document.getElementById("file-drop");
const fileInput = document.getElementById("hw-file");
const filePreview = document.getElementById("file-preview");
const fileNameDisplay = document.getElementById("file-name-display");
const fileClear = document.getElementById("file-clear");

if (fileDrop) {
  // Click to browse
  fileDrop.addEventListener("click", () => fileInput.click());
  document.querySelector(".file-drop-link")?.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  // Drag and drop
  fileDrop.addEventListener("dragover", (e) => {
    e.preventDefault();
    fileDrop.classList.add("drag-over");
  });
  fileDrop.addEventListener("dragleave", () => fileDrop.classList.remove("drag-over"));
  fileDrop.addEventListener("drop", (e) => {
    e.preventDefault();
    fileDrop.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) setFile(file);
  });

  // File input change
  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) setFile(fileInput.files[0]);
  });

  // Clear button
  fileClear.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.value = "";
    filePreview.classList.add("hidden");
    fileDrop.style.display = "flex";
  });
}

function setFile(file) {
  fileNameDisplay.textContent = file.name;
  filePreview.classList.remove("hidden");
  fileDrop.style.display = "none";
}
