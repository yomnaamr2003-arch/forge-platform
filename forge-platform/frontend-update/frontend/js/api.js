// ============================================================
// Forge — API client + shared auth/session helpers
// ============================================================
const API_BASE = "http://127.0.0.1:8000/api";

const Session = {
  getToken(){ return localStorage.getItem("forge_token"); },
  setToken(t){ localStorage.setItem("forge_token", t); },
  clear(){ localStorage.removeItem("forge_token"); localStorage.removeItem("forge_user"); },
  getUser(){
    const raw = localStorage.getItem("forge_user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(u){ localStorage.setItem("forge_user", JSON.stringify(u)); },
  isLoggedIn(){ return !!this.getToken(); },
  isAdmin(){ const u = this.getUser(); return u && u.role === "admin"; },
};

async function apiRequest(path, { method = "GET", body = null, form = false, auth = true } = {}) {
  const headers = {};
  if (auth && Session.getToken()) headers["Authorization"] = "Bearer " + Session.getToken();
  let payload = null;
  if (body) {
    if (form) {
      payload = new URLSearchParams(body);
      headers["Content-Type"] = "application/x-www-form-urlencoded";
    } else {
      payload = JSON.stringify(body);
      headers["Content-Type"] = "application/json";
    }
  }
  let res;
  try {
    res = await fetch(API_BASE + path, { method, headers, body: payload });
  } catch (err) {
    throw new Error("Can't reach the Forge API. Is the backend running on port 8000?");
  }
  let data = null;
  const text = await res.text();
  if (text) { try { data = JSON.parse(text); } catch { data = text; } }
  if (!res.ok) {
    const detail = (data && data.detail) ? data.detail : `Request failed (${res.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

const Api = {
  register: (name, email, password) => apiRequest("/auth/register", { method: "POST", body: { name, email, password }, auth: false }),
  login: (email, password) => apiRequest("/auth/login", { method: "POST", body: { username: email, password }, form: true, auth: false }),
  me: () => apiRequest("/auth/me"),

  listPrograms: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiRequest("/programs" + (qs ? "?" + qs : ""), { auth: false });
  },
  getProgram: (id) => apiRequest(`/programs/${id}`, { auth: false }),
  createProgram: (data) => apiRequest("/programs", { method: "POST", body: data }),
  updateProgram: (id, data) => apiRequest(`/programs/${id}`, { method: "PUT", body: data }),
  deleteProgram: (id) => apiRequest(`/programs/${id}`, { method: "DELETE" }),

  myEnrollments: () => apiRequest("/enrollments/me"),
  enroll: (program_id) => apiRequest("/enrollments", { method: "POST", body: { program_id } }),
  toggleModule: (enrollmentId, module_index, completed) =>
    apiRequest(`/enrollments/${enrollmentId}/module`, { method: "PATCH", body: { module_index, completed } }),

  listServices: () => apiRequest("/services", { auth: false }),
  createService: (data) => apiRequest("/services", { method: "POST", body: data }),
  updateService: (id, data) => apiRequest(`/services/${id}`, { method: "PUT", body: data }),
  deleteService: (id) => apiRequest(`/services/${id}`, { method: "DELETE" }),

  myRequests: () => apiRequest("/service-requests/me"),
  createRequest: (service_id, message) => apiRequest("/service-requests", { method: "POST", body: { service_id, message } }),
  allRequests: () => apiRequest("/service-requests"),
  updateRequestStatus: (id, status) => apiRequest(`/service-requests/${id}/status`, { method: "PATCH", body: { status } }),

  listUsers: () => apiRequest("/admin/users"),
  analytics: () => apiRequest("/admin/analytics"),
};

function requireAuth() {
  if (!Session.isLoggedIn()) window.location.href = "login.html";
}
function requireAdmin() {
  if (!Session.isLoggedIn() || !Session.isAdmin()) window.location.href = "login.html";
}
function redirectIfLoggedIn() {
  if (Session.isLoggedIn()) window.location.href = Session.isAdmin() ? "admin.html" : "dashboard.html";
}

function showToast(msg, isError = false) {
  let el = document.querySelector(".toast");
  if (!el) {
    el = document.createElement("div");
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.toggle("error", isError);
  requestAnimationFrame(() => el.classList.add("show"));
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("show"), 3200);
}

const CATEGORY_PALETTE = ["tag-c1", "tag-c2", "tag-c3", "tag-c4", "tag-c5", "tag-c6"];
function categoryColorClass(label) {
  let hash = 0;
  for (let i = 0; i < label.length; i++) hash = (hash * 31 + label.charCodeAt(i)) >>> 0;
  return CATEGORY_PALETTE[hash % CATEGORY_PALETTE.length];
}
function levelColorClass(level) {
  return "level-" + level.toLowerCase();
}

function initials(name) {
  return name.split(" ").map(p => p[0]).slice(0, 2).join("").toUpperCase();
}

function logout() {
  Session.clear();
  window.location.href = "index.html";
}

// Render nav auth state on pages that include #nav-actions
function renderNavAuth() {
  const el = document.getElementById("nav-actions");
  if (!el) return;
  if (Session.isLoggedIn()) {
    const user = Session.getUser();
    const dest = Session.isAdmin() ? "admin.html" : "dashboard.html";
    el.innerHTML = `
      <a href="${dest}" class="btn btn-ghost btn-sm">Dashboard</a>
      <button class="btn btn-sm" onclick="logout()">Sign out</button>
    `;
  } else {
    el.innerHTML = `
      <a href="login.html" class="btn btn-ghost btn-sm">Sign in</a>
      <a href="register.html" class="btn btn-primary btn-sm">Get started</a>
    `;
  }
}
document.addEventListener("DOMContentLoaded", renderNavAuth);
