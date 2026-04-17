/* ═══════════════════════════════════════════════
   API CONFIG  — set MOCK=false to use real backend
═══════════════════════════════════════════════ */
const MOCK = false;
const API_BASE = "http://localhost:8000";
let _token = null;

async function apiFetch(path, opts = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(opts.headers || {}),
  };
  if (_token) headers["Authorization"] = "Bearer " + _token;
  const res = await fetch(API_BASE + path, { ...opts, headers });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

/* ═══════════════════════════════════════════════
   STATE
═══════════════════════════════════════════════ */
const S = {
  user: null,
  analytics: {
    summary: null,
    topFailures: [],
    flaky: [],
    allureUrl: "http://localhost:8000/reports/allure-report/index.html",
  },
  suites: [
    {
      id: 1,
      name: "Smoke Tests",
      desc: "Critical path validation",
      active: true,
      cases: 8,
    },
    {
      id: 2,
      name: "Regression",
      desc: "Full regression coverage",
      active: true,
      cases: 24,
    },
    {
      id: 3,
      name: "API Tests",
      desc: "REST endpoint validation",
      active: true,
      cases: 15,
    },
    {
      id: 4,
      name: "UI E2E",
      desc: "Pylenium end-to-end flows",
      active: false,
      cases: 6,
    },
  ],
  cases: [
    {
      id: 1,
      suite_id: 1,
      title: "Verify login with valid credentials",
      priority: "critical",
      status: "active",
      tags: "smoke,login",
      node: "ui/test_login.py::test_valid_login",
    },
    {
      id: 2,
      suite_id: 1,
      title: "Verify logout clears session cookie",
      priority: "high",
      status: "active",
      tags: "smoke,auth",
      node: "ui/test_login.py::test_logout",
    },
    {
      id: 3,
      suite_id: 2,
      title: "Create new user via API endpoint",
      priority: "high",
      status: "active",
      tags: "api,users",
      node: "api/test_users.py::test_create_user",
    },
    {
      id: 4,
      suite_id: 3,
      title: "GET /api/cases returns 200",
      priority: "medium",
      status: "active",
      tags: "api,cases",
      node: "api/test_cases.py::test_get_cases",
    },
    {
      id: 5,
      suite_id: 3,
      title: "POST /api/runs triggers execution",
      priority: "critical",
      status: "active",
      tags: "api,runs,smoke",
      node: "api/test_runs.py::test_trigger_run",
    },
    {
      id: 6,
      suite_id: 2,
      title: "Dashboard loads under 2s on 3G",
      priority: "medium",
      status: "inactive",
      tags: "perf",
      node: "ui/test_perf.py::test_dashboard_load",
    },
    {
      id: 7,
      suite_id: 4,
      title: "Login form submits on Enter key",
      priority: "low",
      status: "active",
      tags: "ui,a11y",
      node: "ui/test_a11y.py::test_enter_submit",
    },
    {
      id: 8,
      suite_id: 1,
      title: "Reset password email sent successfully",
      priority: "high",
      status: "active",
      tags: "smoke,email",
      node: "ui/test_auth.py::test_password_reset",
    },
  ],
  runs: [
    {
      id: 5,
      name: "Nightly Smoke #5",
      status: "completed",
      total: 12,
      passed: 11,
      failed: 1,
      skipped: 0,
      env: "staging",
      ts: new Date(Date.now() - 3600000),
      pass_rate: 91.7,
    },
    {
      id: 4,
      name: "API Regression #4",
      status: "completed",
      total: 15,
      passed: 15,
      failed: 0,
      skipped: 0,
      env: "staging",
      ts: new Date(Date.now() - 86400000),
      pass_rate: 100,
    },
    {
      id: 3,
      name: "Full Regression #3",
      status: "failed",
      total: 42,
      passed: 36,
      failed: 6,
      skipped: 0,
      env: "production",
      ts: new Date(Date.now() - 172800000),
      pass_rate: 85.7,
    },
    {
      id: 2,
      name: "Smoke Quick Check",
      status: "completed",
      total: 8,
      passed: 8,
      failed: 0,
      skipped: 0,
      env: "dev",
      ts: new Date(Date.now() - 259200000),
      pass_rate: 100,
    },
    {
      id: 1,
      name: "Initial Run #1",
      status: "completed",
      total: 10,
      passed: 7,
      failed: 2,
      skipped: 1,
      env: "staging",
      ts: new Date(Date.now() - 345600000),
      pass_rate: 70,
    },
  ],
};

/* ═══════════════════════════════════════════════
   TOAST
═══════════════════════════════════════════════ */
function toast(msg, type = "info") {
  const w = document.getElementById("toasts");
  const t = document.createElement("div");
  t.className = `toast t-${type}`;
  t.textContent = msg;
  w.appendChild(t);
  setTimeout(() => {
    t.style.opacity = "0";
    t.style.transform = "translateX(110%)";
    t.style.transition = "all .3s";
    setTimeout(() => t.remove(), 320);
  }, 3000);
}

/* ═══════════════════════════════════════════════
   AUTH
═══════════════════════════════════════════════ */
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const u = document.getElementById("l-user").value.trim();
  const p = document.getElementById("l-pass").value;
  const btn = document.getElementById("l-btn");
  if (!u || !p) {
    toast("Enter credentials", "error");
    return;
  }
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>&nbsp;Signing in…';

  if (MOCK) {
    await sleep(750);
    S.user = { name: u, initials: u.slice(0, 2).toUpperCase(), role: "demo" };
    _afterLogin(S.user);
  } else {
    try {
      const data = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username: u, password: p }),
      });
      _token = data.access_token;
      S.user = {
        name: data.username,
        initials: data.username.slice(0, 2).toUpperCase(),
        role: data.role,
      };
      _afterLogin(S.user);
    } catch (err) {
      toast(err.message || "Login failed", "error");
      btn.disabled = false;
      btn.textContent = "Sign In";
    }
  }
});

function _afterLogin(user) {
  const btn = document.getElementById("l-btn");
  document.getElementById("uc-name").textContent = user.name;
  document.getElementById("uc-av").textContent = user.initials;
  document.getElementById("tb-date").textContent =
    "Overview · " +
    new Date().toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  btn.disabled = false;
  btn.textContent = "Sign In";
  showScreen("app-screen");
  initApp();
  toast("Welcome back, " + user.name + "!", "success");
}

document.getElementById("logout-btn").addEventListener("click", () => {
  _token = null;
  showScreen("login-screen");
  document.getElementById("l-pass").value = "";
  document.getElementById("l-btn").textContent = "Sign In";
  toast("Signed out", "info");
});

/* ═══════════════════════════════════════════════
   ROUTING
═══════════════════════════════════════════════ */
function showScreen(id) {
  document
    .querySelectorAll(".screen")
    .forEach((s) => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

function showView(name) {
  document
    .querySelectorAll(".view")
    .forEach((v) => v.classList.remove("active"));
  document.getElementById("view-" + name).classList.add("active");
  document
    .querySelectorAll(".nav-item")
    .forEach((n) => n.classList.toggle("active", n.dataset.view === name));
  if (name === "cases") renderCases();
  if (name === "suites") renderSuites();
  if (name === "execution") renderRunHistory();
  if (name === "reports") renderReports();
}

document
  .querySelectorAll(".nav-item[data-view]")
  .forEach((el) =>
    el.addEventListener("click", () => showView(el.dataset.view)),
  );

/* ═══════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════ */
async function initApp() {
  if (!MOCK) {
    await loadLiveData();
  }
  renderDashboard();
  drawTrendChart("trend-chart", S.runs);
  drawDonut();
  updateCounters();
  updateSuiteSelects();
}

async function loadLiveData() {
  try {
    const [suites, cases, runs, summary, topFailures, flaky, allureUrl] =
      await Promise.all([
        apiFetch("/api/suites"),
        apiFetch("/api/cases"),
        apiFetch("/api/runs?limit=20"),
        apiFetch("/api/analytics/summary"),
        apiFetch("/api/analytics/top-failures"),
        apiFetch("/api/analytics/flaky"),
        apiFetch("/api/reports/allure-url"),
      ]);

    S.suites = suites.map((s) => ({
      id: s.id,
      name: s.name,
      desc: s.description,
      active: s.is_active,
      cases: s.case_count,
    }));
    S.cases = cases.map((c) => ({
      id: c.id,
      suite_id: c.suite_id,
      title: c.title,
      priority: c.priority,
      status: c.status,
      tags: c.tags,
      node: c.node_id,
    }));
    S.runs = runs.map((r) => ({
      id: r.id,
      name: r.name,
      status: r.status,
      total: r.total,
      passed: r.passed,
      failed: r.failed,
      skipped: r.skipped,
      errors: r.errors || 0,
      duration_seconds: r.duration_seconds || 0,
      env: r.environment,
      ts: new Date(r.created_at),
      pass_rate: r.pass_rate,
    }));
    S.analytics.summary = summary;
    S.analytics.topFailures = topFailures;
    S.analytics.flaky = flaky;
    S.analytics.allureUrl = allureUrl?.url || S.analytics.allureUrl;
  } catch (err) {
    toast("API load error: " + err.message, "error");
  }
}

function aggregateResultSplit() {
  return S.runs.reduce(
    (acc, run) => {
      acc.passed += run.passed || 0;
      acc.failed += run.failed || 0;
      acc.skipped += run.skipped || 0;
      acc.errors += run.errors || 0;
      return acc;
    },
    { passed: 0, failed: 0, skipped: 0, errors: 0 },
  );
}

function totalStoredResults() {
  const split = aggregateResultSplit();
  return split.passed + split.failed + split.skipped + split.errors;
}

function averageDurationSeconds() {
  const durations = S.runs
    .map((run) => run.duration_seconds || 0)
    .filter((v) => v > 0);
  if (!durations.length) return 0;
  return durations.reduce((sum, value) => sum + value, 0) / durations.length;
}

function coveragePctForSuite(suite) {
  const totalCases = S.cases.length || 1;
  return Math.round(((suite.cases || 0) / totalCases) * 100);
}

function titleForFailure(item) {
  return (
    item.title ||
    S.cases.find((c) => c.node === item.node_id)?.title ||
    item.node_id
  );
}

function flakyRowsHtml(rows) {
  if (!rows.length) {
    return `<tr><td colspan="5"><div class="empty"><p>No flaky tests detected yet</p></div></td></tr>`;
  }
  return rows
    .map(
      (row) => `
    <tr>
      <td>${esc(row.title || row.node_id)}</td>
      <td class="mono" style="color:var(--text2)">${row.total_runs}</td>
      <td class="mono" style="color:var(--green)">${row.passed}</td>
      <td class="mono" style="color:var(--red)">${row.failed}</td>
      <td><div style="display:flex;align-items:center;gap:7px"><div class="pb" style="width:60px"><div class="pbf r" style="width:${row.flakiness_pct}%"></div></div><span class="mono" style="font-size:10px;color:var(--red)">${row.flakiness_pct}%</span></div></td>
    </tr>`,
    )
    .join("");
}

function buildActivityFeed() {
  const runActs = S.runs.slice(0, 4).map((run) => ({
    dot:
      run.status === "completed"
        ? "var(--green)"
        : run.status === "failed"
          ? "var(--red)"
          : "var(--amber)",
    txt: `<strong>${esc(run.name)}</strong> ${run.status} - ${run.passed || 0}/${run.total || 0} passed`,
    time: timeAgo(run.ts),
  }));
  const suiteSummary = {
    dot: "var(--blue)",
    txt: `<strong>${S.suites.filter((s) => s.active).length} active suites</strong> across ${S.cases.length} test cases`,
    time: "now",
  };
  return [...runActs, suiteSummary];
}

/* ═══════════════════════════════════════════════
   DASHBOARD
═══════════════════════════════════════════════ */
function renderDashboard() {
  animCount("st-suites", S.suites.length, "");
  animCount("st-cases", S.cases.length, "");
  animCount("st-runs", S.runs.length, "");
  const avgRate = S.analytics.summary?.avg_pass_rate || 0;
  document.getElementById("st-pass").textContent = avgRate.toFixed(1) + "%";

  const summaryTiles = document.querySelectorAll(
    "#view-dashboard .stats-row .stat-tile .sd",
  );
  if (summaryTiles[0])
    summaryTiles[0].textContent = `${S.suites.filter((s) => s.active).length} active suites`;
  if (summaryTiles[1])
    summaryTiles[1].textContent = `${S.cases.filter((c) => c.status === "active").length} active cases`;
  if (summaryTiles[2]) summaryTiles[2].textContent = "Based on completed runs";
  if (summaryTiles[3])
    summaryTiles[3].textContent = S.runs.length
      ? `Last run ${timeAgo(S.runs[0].ts)}`
      : "No runs yet";

  /* Recent runs */
  document.getElementById("recent-runs-list").innerHTML = S.runs
    .slice(0, 5)
    .map(
      (r) => `
    <div style="padding:11px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;transition:background .1s" onmouseover="this.style.background='rgba(255,255,255,.015)'" onmouseout="this.style.background=''">
      <div>
        <div style="font-size:12px;font-weight:600;margin-bottom:2px">${esc(r.name)}</div>
        <div style="font-family:var(--mono);font-size:9px;color:var(--text3)">#${r.id} · ${timeAgo(r.ts)} · ${r.env}</div>
      </div>
      <div style="display:flex;align-items:center;gap:10px">
        <div>
          <div class="pb" style="width:70px"><div class="pbf ${r.pass_rate >= 90 ? "g" : r.pass_rate >= 70 ? "a" : "r"}" style="width:${r.pass_rate}%"></div></div>
        </div>
        <span style="font-family:var(--mono);font-size:11px;font-weight:700;color:${r.pass_rate >= 90 ? "var(--green)" : r.pass_rate >= 70 ? "var(--amber)" : "var(--red)"}">${r.pass_rate}%</span>
        ${statusBadge(r.status)}
      </div>
    </div>`,
    )
    .join("");

  /* Top failures */
  const failures = S.analytics.topFailures.map((item) => ({
    title: titleForFailure(item),
    count: item.count,
  }));
  document.getElementById("top-failures").innerHTML =
    failures
      .map(
        (f, i) => `
    <div style="padding:9px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px">
      <span style="font-family:var(--mono);font-size:9px;color:var(--text3);width:16px">#${i + 1}</span>
      <span style="font-size:11px;flex:1;line-height:1.4">${esc(f.title)}</span>
      <span style="font-family:var(--mono);font-size:10px;color:var(--red);background:var(--red-dim);padding:1px 7px;border-radius:3px">${f.count}×</span>
    </div>`,
      )
      .join("") || `<div class="empty"><p>No failures recorded yet</p></div>`;

  /* Activity */
  const acts = buildActivityFeed();
  document.getElementById("activity-feed").innerHTML = acts
    .map(
      (a) => `
    <div class="act-item">
      <div class="act-dot" style="background:${a.dot}"></div>
      <div class="act-txt">${a.txt}</div>
      <div class="act-time">${a.time}</div>
    </div>`,
    )
    .join("");
}

async function refreshDashboard() {
  if (!MOCK) await loadLiveData();
  renderDashboard();
  drawTrendChart("trend-chart", S.runs);
  drawDonut();
  updateCounters();
  toast("Dashboard refreshed", "success");
}

/* ═══════════════════════════════════════════════
   SUITES
═══════════════════════════════════════════════ */
function renderSuites() {
  const tb = document.getElementById("suites-tbody");
  if (!S.suites.length) {
    tb.innerHTML = `<tr><td colspan="6"><div class="empty"><p>No suites yet</p></div></td></tr>`;
    return;
  }
  tb.innerHTML = S.suites
    .map(
      (s) => `
    <tr>
      <td class="mono" style="color:var(--text3)">#${s.id}</td>
      <td>${esc(s.name)}</td>
      <td style="color:var(--text2);max-width:220px">${esc(s.desc || "—")}</td>
      <td><span class="badge bb">${s.cases}</span></td>
      <td>${s.active ? '<span class="badge bg">Active</span>' : '<span class="badge bx">Inactive</span>'}</td>
      <td><button class="btn btn-red btn-sm" onclick="deleteSuite(${s.id})">Delete</button></td>
    </tr>`,
    )
    .join("");
  updateSuiteSelects();
}

function openModal(id) {
  document.getElementById(id).classList.add("open");
}
function closeModal(id) {
  document.getElementById(id).classList.remove("open");
}

async function saveSuite() {
  const name = document.getElementById("s-name").value.trim();
  const desc = document.getElementById("s-desc").value.trim();
  if (!name) {
    toast("Name is required", "error");
    return;
  }
  if (MOCK) {
    if (S.suites.find((s) => s.name.toLowerCase() === name.toLowerCase())) {
      toast("Suite already exists", "error");
      return;
    }
    S.suites.push({
      id: S.suites.length + 1,
      name,
      desc,
      active: true,
      cases: 0,
    });
  } else {
    try {
      const s = await apiFetch("/api/suites", {
        method: "POST",
        body: JSON.stringify({ name, description: desc }),
      });
      S.suites.push({
        id: s.id,
        name: s.name,
        desc: s.description,
        active: s.is_active,
        cases: s.case_count,
      });
    } catch (err) {
      toast(err.message, "error");
      return;
    }
  }
  document.getElementById("s-name").value = "";
  document.getElementById("s-desc").value = "";
  closeModal("m-suite");
  renderSuites();
  updateCounters();
  toast(`Suite "${name}" created`, "success");
}

async function deleteSuite(id) {
  if (!confirm("Delete this suite?")) return;
  const s = S.suites.find((x) => x.id === id);
  if (!MOCK) {
    try {
      await apiFetch("/api/suites/" + id, { method: "DELETE" });
    } catch (err) {
      toast(err.message, "error");
      return;
    }
  }
  S.suites = S.suites.filter((x) => x.id !== id);
  renderSuites();
  updateCounters();
  toast(`Suite "${s?.name}" deleted`, "warn");
}

function updateSuiteSelects() {
  const opts = S.suites
    .map((s) => `<option value="${s.id}">${esc(s.name)}</option>`)
    .join("");
  ["c-suite", "filter-suite"].forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    const pre =
      id === "filter-suite"
        ? '<option value="">All Suites</option>'
        : '<option value="">Select suite…</option>';
    el.innerHTML = pre + opts;
  });
}

/* ═══════════════════════════════════════════════
   TEST CASES
═══════════════════════════════════════════════ */
function renderCases() {
  const suite = document.getElementById("filter-suite")?.value || "";
  const pri = document.getElementById("filter-priority")?.value || "";
  let cases = [...S.cases];
  if (suite) cases = cases.filter((c) => c.suite_id === parseInt(suite));
  if (pri) cases = cases.filter((c) => c.priority === pri);
  document.getElementById("sb-cases-count").textContent = S.cases.length;

  const tb = document.getElementById("cases-tbody");
  if (!cases.length) {
    tb.innerHTML = `<tr><td colspan="7"><div class="empty"><p>No test cases found</p></div></td></tr>`;
    return;
  }
  tb.innerHTML = cases
    .map((c) => {
      const suite = S.suites.find((s) => s.id === c.suite_id);
      return `<tr>
      <td class="mono" style="color:var(--text3)">#${c.id}</td>
      <td style="max-width:240px;line-height:1.4">${esc(c.title)}</td>
      <td><span class="badge bb">${esc(suite?.name || "—")}</span></td>
      <td>${prioBadge(c.priority)}</td>
      <td>${c.status === "active" ? '<span class="badge bg">Active</span>' : c.status === "inactive" ? '<span class="badge bx">Inactive</span>' : '<span class="badge br">Deprecated</span>'}</td>
      <td>${
        c.tags
          ? `<div class="tag-list">${c.tags
              .split(",")
              .map((t) => `<span class="tag">${esc(t.trim())}</span>`)
              .join("")}</div>`
          : '<span style="color:var(--text3)">—</span>'
      }</td>
      <td><button class="btn btn-red btn-sm" onclick="deleteCase(${c.id})">Delete</button></td>
    </tr>`;
    })
    .join("");
}

async function saveCase() {
  const title = document.getElementById("c-title").value.trim();
  const suite = document.getElementById("c-suite").value;
  const prio = document.getElementById("c-priority").value;
  const status = document.getElementById("c-status").value;
  const tags = document.getElementById("c-tags").value.trim();
  const node = document.getElementById("c-node").value.trim();
  const desc = document.getElementById("c-desc").value.trim();
  if (!title) {
    toast("Title is required", "error");
    return;
  }
  if (!suite) {
    toast("Select a suite", "error");
    return;
  }

  if (MOCK) {
    const id = S.cases.length ? Math.max(...S.cases.map((c) => c.id)) + 1 : 1;
    S.cases.push({
      id,
      suite_id: parseInt(suite),
      title,
      priority: prio,
      status,
      tags: tags || null,
      node: node || null,
    });
    const s = S.suites.find((x) => x.id === parseInt(suite));
    if (s) s.cases++;
  } else {
    try {
      const c = await apiFetch("/api/cases", {
        method: "POST",
        body: JSON.stringify({
          title,
          suite_id: parseInt(suite),
          priority: prio,
          status,
          tags: tags || null,
          node_id: node || null,
          description: desc || null,
        }),
      });
      S.cases.push({
        id: c.id,
        suite_id: c.suite_id,
        title: c.title,
        priority: c.priority,
        status: c.status,
        tags: c.tags,
        node: c.node_id,
      });
      const s = S.suites.find((x) => x.id === parseInt(suite));
      if (s) s.cases++;
    } catch (err) {
      toast(err.message, "error");
      return;
    }
  }

  ["c-title", "c-tags", "c-node", "c-desc"].forEach(
    (i) => (document.getElementById(i).value = ""),
  );
  closeModal("m-case");
  renderCases();
  updateCounters();
  toast(`"${title}" created`, "success");
}

async function deleteCase(id) {
  if (!confirm("Delete this test case?")) return;
  const c = S.cases.find((x) => x.id === id);
  if (!MOCK) {
    try {
      await apiFetch("/api/cases/" + id, { method: "DELETE" });
    } catch (err) {
      toast(err.message, "error");
      return;
    }
  }
  S.cases = S.cases.filter((x) => x.id !== id);
  const s = S.suites.find((x) => x.id === c?.suite_id);
  if (s && s.cases > 0) s.cases--;
  renderCases();
  updateCounters();
  toast("Test case deleted", "warn");
}

/* ═══════════════════════════════════════════════
   EXECUTION
═══════════════════════════════════════════════ */
async function triggerRun() {
  const name = document.getElementById("r-name").value.trim();
  if (!name) {
    toast("Run name is required", "error");
    return;
  }
  const suite = document.getElementById("r-suite").value;
  const env = document.getElementById("r-env").value;
  const marker = document.getElementById("r-marker").value.trim();
  closeModal("m-run");
  document.getElementById("r-name").value = "";

  if (MOCK) {
    simulateRun(name, suite, env, marker);
    return;
  }

  // Create run via API
  try {
    const run = await apiFetch("/api/runs", {
      method: "POST",
      body: JSON.stringify({
        name,
        suite_id: suite ? parseInt(suite) : null,
        environment: env,
        marker: marker || null,
      }),
    });
    // Add to local state immediately
    S.runs.unshift({
      id: run.id,
      name: run.name,
      status: "running",
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      env: run.environment,
      ts: new Date(run.created_at),
      pass_rate: 0,
    });
    renderRunHistory();
    showView("execution");
    _streamRun(run.id, name);
  } catch (err) {
    toast("Failed to create run: " + err.message, "error");
  }
}

async function triggerQuickRun() {
  const name = document.getElementById("qt-name").value.trim();
  if (!name) {
    toast("Run name is required", "error");
    return;
  }
  const suite = document.getElementById("qt-suite").value;
  const env = document.getElementById("qt-env").value;

  if (MOCK) {
    simulateRun(name, suite, env, "");
    document.getElementById("qt-name").value = "";
    return;
  }

  document.getElementById("qt-name").value = "";
  try {
    const run = await apiFetch("/api/runs", {
      method: "POST",
      body: JSON.stringify({
        name,
        suite_id: suite ? parseInt(suite) : null,
        environment: env,
      }),
    });
    S.runs.unshift({
      id: run.id,
      name: run.name,
      status: "running",
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      env: run.environment,
      ts: new Date(run.created_at),
      pass_rate: 0,
    });
    renderRunHistory();
    _streamRun(run.id, name);
  } catch (err) {
    toast("Failed to create run: " + err.message, "error");
  }
}

function _streamRun(runId, runName) {
  if (!_token) {
    toast("Please sign in again before starting a run", "error");
    return;
  }
  const con = document.getElementById("exec-console");
  con.innerHTML = "";
  document.getElementById("ls-pass").textContent = "0";
  document.getElementById("ls-fail").textContent = "0";
  document.getElementById("ls-skip").textContent = "0";
  document.getElementById("ls-dur").textContent = "0s";
  document.getElementById("ls-pct").textContent = "0%";
  document.getElementById("ls-bar").style.width = "0%";
  document.getElementById("ls-status").textContent = "Running…";
  const btn = document.getElementById("qt-btn");
  if (btn) btn.disabled = true;

  const wsUrl =
    API_BASE.replace("http", "ws") +
    "/ws/runs/" +
    runId +
    "/stream?token=" +
    encodeURIComponent(_token);
  const ws = new WebSocket(wsUrl);
  const start = Date.now();

  ws.onmessage = (evt) => {
    const msg = JSON.parse(evt.data);
    if (msg.done) {
      const r = msg.run;
      const idx = S.runs.findIndex((x) => x.id === runId);
      if (idx >= 0) {
        S.runs[idx] = {
          ...S.runs[idx],
          status: r.status,
          total: r.total,
          passed: r.passed,
          failed: r.failed,
          pass_rate: r.pass_rate,
        };
      }
      document.getElementById("ls-status").textContent =
        r.status === "completed" ? "Completed ✓" : "Failed ✗";
      document.getElementById("ls-dur").textContent =
        (r.duration_seconds || 0).toFixed(1) + "s";
      renderRunHistory();
      updateCounters();
      if (btn) btn.disabled = false;
      toast(`Run "${runName}" ${r.status}`, "success");
      return;
    }
    if (msg.error) {
      toast(msg.error, "error");
      if (btn) btn.disabled = false;
      return;
    }

    const d = document.createElement("div");
    d.className = "con-" + (msg.type || "info");
    d.textContent = msg.line;
    con.appendChild(d);
    con.scrollTop = con.scrollHeight;

    // Live counter update
    const ln = (msg.line || "").trim();
    if (/\sPASSED(?:\s+\[\s*\d+%\])?$/.test(ln)) {
      const n = parseInt(document.getElementById("ls-pass").textContent) || 0;
      document.getElementById("ls-pass").textContent = n + 1;
    }
    if (/\sFAILED(?:\s+\[\s*\d+%\])?$/.test(ln)) {
      const n = parseInt(document.getElementById("ls-fail").textContent) || 0;
      document.getElementById("ls-fail").textContent = n + 1;
    }
    if (/\sSKIPPED(?:\s+\[\s*\d+%\])?$/.test(ln)) {
      const n = parseInt(document.getElementById("ls-skip").textContent) || 0;
      document.getElementById("ls-skip").textContent = n + 1;
    }
    const p = parseInt(document.getElementById("ls-pass").textContent) || 0;
    const f = parseInt(document.getElementById("ls-fail").textContent) || 0;
    const s = parseInt(document.getElementById("ls-skip").textContent) || 0;
    const tot = p + f + s;
    const pct = tot > 0 ? Math.round((p / tot) * 100) : 0;
    document.getElementById("ls-pct").textContent = pct + "%";
    document.getElementById("ls-bar").style.width = pct + "%";
    document.getElementById("ls-bar").className =
      "pbf " + (pct >= 80 ? "g" : pct >= 50 ? "a" : "r");
    document.getElementById("ls-dur").textContent =
      ((Date.now() - start) / 1000).toFixed(1) + "s";
  };

  ws.onerror = () => {
    toast("WebSocket error", "error");
    if (btn) btn.disabled = false;
  };
  ws.onclose = (evt) => {
    if (evt.code === 1008)
      toast("Run stream authentication failed. Please sign in again.", "error");
    if (btn) btn.disabled = false;
  };
}

function simulateRun(name, suiteId, env, marker) {
  showView("execution");
  const con = document.getElementById("exec-console");
  con.innerHTML = "";
  const suiteName =
    S.suites.find((s) => s.id === parseInt(suiteId))?.name || "All Suites";
  const tid = Date.now();
  const newRun = {
    id: tid,
    name,
    status: "running",
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0,
    env,
    ts: new Date(),
    pass_rate: null,
  };
  S.runs.unshift(newRun);
  renderRunHistory();

  const lines = [
    [0, "con-dim", `// Run: ${name}`],
    [80, "con-dim", `// Suite: ${suiteName}  Env: ${env}`],
    [
      200,
      "",
      marker
        ? `$ pytest ${marker ? `-m "${marker}" ` : ""}--alluredir reports/allure-results/ -q`
        : "$ pytest automation/ --alluredir reports/allure-results/ -q",
    ],
    [500, "con-info", `Collecting tests…`],
    [900, "con-pass", `PASSED  test_valid_login (0.42s)`],
    [1300, "con-pass", `PASSED  test_logout_clears_session (0.31s)`],
    [1700, "con-pass", `PASSED  test_get_cases_returns_200 (0.19s)`],
    [
      2100,
      "con-fail",
      `FAILED  test_dashboard_load_time (2.31s) — AssertionError: Expected < 2s, got 2.31s`,
    ],
    [2450, "con-pass", `PASSED  test_post_runs_triggers (0.55s)`],
    [2750, "con-warn", `SKIPPED test_prod_only_check (marker mismatch)`],
    [2900, "con-pass", `PASSED  test_reset_password_email (0.88s)`],
    [3200, "", `─────────────────────────────────────`],
    [3300, "con-pass", `5 passed, 1 failed, 1 skipped in 4.66s`],
    [3450, "con-info", `Generating Allure report…`],
    [
      3900,
      "con-pass",
      `✓ Report → http://localhost:8000/reports/allure-report/index.html`,
    ],
  ];

  // live stats animation
  document.getElementById("ls-pass").textContent = "0";
  document.getElementById("ls-fail").textContent = "0";
  document.getElementById("ls-skip").textContent = "0";
  document.getElementById("ls-dur").textContent = "0s";
  document.getElementById("ls-pct").textContent = "0%";
  document.getElementById("ls-bar").style.width = "0%";
  document.getElementById("ls-status").textContent = "Running…";
  const btn = document.getElementById("qt-btn");
  btn.disabled = true;

  let passed = 0,
    failed = 0,
    skipped = 0;
  lines.forEach(([t, cls, msg]) => {
    setTimeout(() => {
      const d = document.createElement("div");
      if (cls) d.className = cls;
      d.textContent = msg;
      con.appendChild(d);
      con.scrollTop = con.scrollHeight;
      if (msg.startsWith("PASSED")) {
        passed++;
      }
      if (msg.startsWith("FAILED")) {
        failed++;
      }
      if (msg.startsWith("SKIPPED")) {
        skipped++;
      }
      const total = passed + failed + skipped;
      const pct = total > 0 ? Math.round((passed / total) * 100) : 0;
      document.getElementById("ls-pass").textContent = passed;
      document.getElementById("ls-fail").textContent = failed;
      document.getElementById("ls-skip").textContent = skipped;
      document.getElementById("ls-dur").textContent =
        (t / 1000).toFixed(1) + "s";
      document.getElementById("ls-pct").textContent = pct + "%";
      document.getElementById("ls-bar").style.width = pct + "%";
      document.getElementById("ls-bar").className =
        `pbf ${pct >= 80 ? "g" : pct >= 50 ? "a" : "r"}`;
    }, t);
  });

  setTimeout(() => {
    newRun.status = "completed";
    newRun.passed = 5;
    newRun.failed = 1;
    newRun.skipped = 1;
    newRun.total = 7;
    newRun.pass_rate = 71.4;
    document.getElementById("ls-status").textContent = "Completed";
    renderRunHistory();
    updateCounters();
    btn.disabled = false;
    toast(`Run "${name}" completed`, "success");
  }, 4200);
}

function renderRunHistory() {
  const c = document.getElementById("run-history");
  if (!S.runs.length) {
    c.innerHTML = '<div class="empty"><p>No runs yet</p></div>';
    return;
  }
  c.innerHTML = S.runs
    .map(
      (r) => `
    <div class="run-card">
      <div>
        <div class="rc-name">${esc(r.name)}</div>
        <div class="rc-meta">#${r.id} · ${timeAgo(r.ts)} · ${r.env || "—"}</div>
        <div class="rc-stats">
          <div class="rc-stat"><span>Pass </span><span style="color:var(--green)">${r.passed}</span></div>
          <div class="rc-stat"><span>Fail </span><span style="color:var(--red)">${r.failed}</span></div>
          <div class="rc-stat"><span>Total </span>${r.total}</div>
          ${
            r.total > 0
              ? `<div style="flex:1;max-width:120px;display:flex;align-items:center;gap:7px">
            <div class="pb" style="flex:1"><div class="pbf ${(r.pass_rate || 0) >= 80 ? "g" : (r.pass_rate || 0) >= 50 ? "a" : "r"}" style="width:${r.pass_rate || 0}%"></div></div>
            <span class="mono" style="font-size:9px;color:var(--text2)">${r.pass_rate || 0}%</span>
          </div>`
              : ""
          }
        </div>
      </div>
      <div>${statusBadge(r.status)}</div>
    </div>`,
    )
    .join("");
}

/* ═══════════════════════════════════════════════
   REPORTS
═══════════════════════════════════════════════ */
function renderReports() {
  document.getElementById("rp-total-runs").textContent = S.runs.length;
  document.getElementById("rp-total-results").textContent =
    totalStoredResults();
  document.getElementById("rp-flaky-count").textContent =
    S.analytics.flaky.length;
  document.getElementById("rp-flaky-badge").textContent =
    `${S.analytics.flaky.length} Flaky`;
  document.getElementById("rp-avg-duration").textContent =
    `${averageDurationSeconds().toFixed(1)}s`;
  document.getElementById("report-flaky-tbody").innerHTML = flakyRowsHtml(
    S.analytics.flaky,
  );
  drawTrendChart("report-trend-chart", S.runs);
}

function viewReport(type) {
  const title = document.getElementById("report-title");
  const body = document.getElementById("report-body");
  if (type === "allure") {
    title.textContent = "Allure Report";
    body.innerHTML = `
      <div style="text-align:center;padding:20px 0">
        <div style="width:52px;height:52px;background:var(--amber-glow);border-radius:10px;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;border:1px solid rgba(245,166,35,.2)">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--amber)" stroke-width="2" stroke-linecap="round" style="width:24px;height:24px"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        </div>
        <p style="font-size:13px;color:var(--text2);line-height:1.7;max-width:400px;margin:0 auto">The Allure HTML report is generated automatically after each pytest run and served by FastAPI.</p>
        <div style="background:var(--bg3);border:1px solid var(--border2);border-radius:8px;padding:12px 18px;margin:16px auto;max-width:400px;font-family:var(--mono);font-size:11px;color:var(--amber)">
          ${esc(S.analytics.allureUrl)}
        </div>
        <a href="${esc(S.analytics.allureUrl)}" target="_blank" class="btn btn-amber" style="display:inline-flex">Open Allure Report</a>
      </div>`;
  } else if (type === "flaky") {
    title.textContent = "Flaky Test Analysis";
    body.innerHTML = `
      <p style="font-size:12px;color:var(--text2);margin-bottom:16px">Tests that both passed and failed across multiple runs. These need investigation.</p>
      <table class="tbl">
        <thead><tr><th>Test Case</th><th>Total Runs</th><th>Passed</th><th>Failed</th><th>Flakiness %</th></tr></thead>
        <tbody>
          <tr><td>Verify login with valid credentials</td><td class="mono">10</td><td class="mono" style="color:var(--green)">6</td><td class="mono" style="color:var(--red)">4</td><td><div style="display:flex;align-items:center;gap:8px"><div class="pb" style="width:80px"><div class="pbf r" style="width:40%"></div></div><span class="mono" style="font-size:10px;color:var(--red)">40%</span></div></td></tr>
          <tr><td>POST /api/runs triggers execution</td><td class="mono">8</td><td class="mono" style="color:var(--green)">5</td><td class="mono" style="color:var(--red)">3</td><td><div style="display:flex;align-items:center;gap:8px"><div class="pb" style="width:80px"><div class="pbf r" style="width:37.5%"></div></div><span class="mono" style="font-size:10px;color:var(--red)">37.5%</span></div></td></tr>
        </tbody>
      </table>`;
  } else if (type === "trend") {
    title.textContent = "Pass Rate Trend";
    body.innerHTML = `<canvas id="m-trend-canvas" height="200" style="width:100%"></canvas>`;
    setTimeout(() => drawTrendChart("m-trend-canvas", S.runs), 60);
  } else {
    title.textContent = "Coverage Summary";
    body.innerHTML = `
      <p style="font-size:12px;color:var(--text2);margin-bottom:16px">Test coverage breakdown by suite and priority.</p>
      <table class="tbl">
        <thead><tr><th>Suite</th><th>Cases</th><th>Status</th><th>Coverage</th></tr></thead>
        <tbody>${S.suites
          .map(
            (s) => `
          <tr>
            <td>${esc(s.name)}</td>
            <td class="mono">${s.cases}</td>
            <td>${s.active ? '<span class="badge bg">Active</span>' : '<span class="badge bx">Inactive</span>'}</td>
            <td>
              <div style="display:flex;align-items:center;gap:8px">
                <div class="pb" style="width:90px"><div class="pbf g" style="width:${coveragePctForSuite(s)}%"></div></div>
                <span class="mono" style="font-size:10px;color:var(--text2)">${coveragePctForSuite(s)}%</span>
              </div>
            </td>
          </tr>`,
          )
          .join("")}
        </tbody>
      </table>`;
  }
  openModal("m-report");
}

/* ═══════════════════════════════════════════════
   CHARTS
═══════════════════════════════════════════════ */
function drawTrendChart(canvasId, runs) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const W = canvas.offsetWidth || 400,
    H = parseInt(canvas.getAttribute("height")) || 130;
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d");
  const data = [...runs].reverse().map((r) => r.pass_rate || 0);
  const labels = [...runs].reverse().map((r) => "#" + r.id);
  if (!data.length) return;
  const pad = { l: 32, r: 12, t: 12, b: 26 };
  const gW = W - pad.l - pad.r,
    gH = H - pad.t - pad.b;
  const xStep = gW / Math.max(data.length - 1, 1);
  const yScale = (v) => pad.t + gH - (v / 100) * gH;
  ctx.clearRect(0, 0, W, H);
  [0, 25, 50, 75, 100].forEach((v) => {
    ctx.strokeStyle = "rgba(26,39,64,.7)";
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 5]);
    ctx.beginPath();
    ctx.moveTo(pad.l, yScale(v));
    ctx.lineTo(W - pad.r, yScale(v));
    ctx.stroke();
    ctx.fillStyle = "#3d5070";
    ctx.font = "9px Space Mono";
    ctx.fillText(v + "%", 2, yScale(v) + 3);
  });
  ctx.setLineDash([]);
  // gradient fill
  const grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + gH);
  grad.addColorStop(0, "rgba(245,166,35,.18)");
  grad.addColorStop(1, "rgba(245,166,35,.01)");
  ctx.beginPath();
  data.forEach((v, i) => {
    const x = pad.l + i * xStep;
    i === 0 ? ctx.moveTo(x, yScale(v)) : ctx.lineTo(x, yScale(v));
  });
  ctx.lineTo(pad.l + (data.length - 1) * xStep, pad.t + gH);
  ctx.lineTo(pad.l, pad.t + gH);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();
  // line
  ctx.beginPath();
  ctx.strokeStyle = "#f5a623";
  ctx.lineWidth = 2;
  data.forEach((v, i) => {
    const x = pad.l + i * xStep;
    i === 0 ? ctx.moveTo(x, yScale(v)) : ctx.lineTo(x, yScale(v));
  });
  ctx.stroke();
  // dots
  data.forEach((v, i) => {
    const x = pad.l + i * xStep,
      y = yScale(v);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = v >= 90 ? "#10b981" : v >= 70 ? "#f5a623" : "#f43f5e";
    ctx.fill();
    ctx.strokeStyle = "#080d18";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = "#3d5070";
    ctx.font = "9px Space Mono";
    ctx.fillText(labels[i], x - 6, H - 5);
  });
}

function drawDonut() {
  const svg = document.getElementById("donut-svg");
  const legend = document.getElementById("donut-legend");
  if (!svg || !legend) return;
  const split = aggregateResultSplit();
  const total = split.passed + split.failed + split.skipped + split.errors;
  const slices = [
    { label: "Passed", val: split.passed, c: "#10b981" },
    { label: "Failed", val: split.failed, c: "#f43f5e" },
    { label: "Skipped", val: split.skipped, c: "#f5a623" },
    { label: "Error", val: split.errors, c: "#8b5cf6" },
  ];
  if (!total) {
    svg.innerHTML = `<circle cx="60" cy="60" r="40" fill="none" stroke="#223250" stroke-width="18"></circle><text x="60" y="64" text-anchor="middle" font-family="Space Mono" font-size="10" fill="#7a91b3">No data</text>`;
    legend.innerHTML = slices
      .map(
        (s) =>
          `<div class="d-row"><div class="d-dot" style="background:${s.c}"></div>${s.label}<span class="d-pct">0%</span></div>`,
      )
      .join("");
    return;
  }
  const cx = 60,
    cy = 60,
    R = 52,
    r = 34;
  let angle = -Math.PI / 2,
    paths = "";
  slices.forEach((s) => {
    const sw = (s.val / total) * Math.PI * 2;
    const x1 = cx + R * Math.cos(angle),
      y1 = cy + R * Math.sin(angle);
    angle += sw;
    const x2 = cx + R * Math.cos(angle),
      y2 = cy + R * Math.sin(angle);
    const ix1 = cx + r * Math.cos(angle - sw),
      iy1 = cy + r * Math.sin(angle - sw);
    const ix2 = cx + r * Math.cos(angle),
      iy2 = cy + r * Math.sin(angle);
    const lg = sw > Math.PI ? 1 : 0;
    paths += `<path d="M${x1},${y1} A${R},${R} 0 ${lg},1 ${x2},${y2} L${ix2},${iy2} A${r},${r} 0 ${lg},0 ${ix1},${iy1} Z" fill="${s.c}" opacity=".88"/>`;
  });
  svg.innerHTML =
    paths +
    `<text x="${cx}" y="${cy + 4}" text-anchor="middle" font-family="Space Mono" font-size="10" fill="#7a91b3">Results</text>`;
  legend.innerHTML = slices
    .map(
      (s) =>
        `<div class="d-row"><div class="d-dot" style="background:${s.c}"></div>${s.label}<span class="d-pct">${Math.round((s.val / total) * 100)}%</span></div>`,
    )
    .join("");
}

/* ═══════════════════════════════════════════════
   HELPERS
═══════════════════════════════════════════════ */
function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}
function esc(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function timeAgo(d) {
  const s = Math.round((Date.now() - new Date(d)) / 1000);
  if (s < 60) return s + "s ago";
  if (s < 3600) return Math.round(s / 60) + "m ago";
  if (s < 86400) return Math.round(s / 3600) + "h ago";
  return Math.round(s / 86400) + "d ago";
}

function statusBadge(s) {
  const m = {
    completed: "bg",
    failed: "br",
    running: "ba",
    pending: "bx",
    aborted: "bx",
  };
  return `<span class="badge ${m[s] || "bx"}">${s}</span>`;
}

function prioBadge(p) {
  const m = { critical: "br", high: "ba", medium: "bb", low: "bx" };
  return `<span class="badge ${m[p] || "bx"}">${p}</span>`;
}

function animCount(id, target, suffix = "", dur = 850) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = performance.now();
  const run = (now) => {
    const p = Math.min((now - start) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(ease * target) + suffix;
    if (p < 1) requestAnimationFrame(run);
  };
  requestAnimationFrame(run);
}

function updateCounters() {
  document.getElementById("sb-suites-count").textContent = S.suites.length;
  document.getElementById("sb-cases-count").textContent = S.cases.length;
  document.getElementById("sb-runs-count").textContent = S.runs.length;
  document.getElementById("st-suites").textContent = S.suites.length;
  document.getElementById("st-cases").textContent = S.cases.length;
  document.getElementById("st-runs").textContent = S.runs.length;
}

/* ═══════════════════════════════════════════════
   CHAT WIDGET
═══════════════════════════════════════════════ */
let chatMessages = [];

function toggleChatWidget() {
  const widget = document.querySelector(".chat-widget");
  widget.classList.toggle("open");
  if (widget.classList.contains("open")) {
    document.getElementById("chat-input").focus();
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();

  if (!message) return;

  // Add user message to UI
  addChatMessage(message, "user");
  input.value = "";
  input.focus();

  // Add loading state
  const loadingId = "loading-" + Date.now();
  addChatLoadingIndicator(loadingId);

  try {
    // Get response from backend or mock
    let response;
    if (MOCK) {
      await sleep(1000);
      response = { reply: generateMockChatResponse(message) };
    } else {
      response = await apiFetch("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          message: message,
          context: { suites: S.suites, cases: S.cases, runs: S.runs },
        }),
      });
    }

    // Remove loading indicator
    removeChatLoadingIndicator(loadingId);

    // Add assistant response
    const replyText =
      response.reply || response.response || "Unable to process your request";
    addChatMessage(replyText, "assistant");
  } catch (err) {
    removeChatLoadingIndicator(loadingId);
    addChatMessage(
      "Sorry, I encountered an error: " + (err.message || "Unknown error"),
      "assistant",
    );
  }
}

function addChatMessage(text, role) {
  const messagesContainer = document.getElementById("chat-messages");
  const message = document.createElement("div");
  message.className = "chat-message " + role;

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";
  bubble.textContent = text;

  message.appendChild(bubble);
  messagesContainer.appendChild(message);

  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  chatMessages.push({ role, text, timestamp: new Date() });
}

function addChatLoadingIndicator(id) {
  const messagesContainer = document.getElementById("chat-messages");
  const message = document.createElement("div");
  message.className = "chat-message assistant";
  message.id = id;

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";

  bubble.innerHTML = `
    <div class="chat-loading">
      <div class="chat-loading-dot"></div>
      <div class="chat-loading-dot"></div>
      <div class="chat-loading-dot"></div>
    </div>
  `;

  message.appendChild(bubble);
  messagesContainer.appendChild(message);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeChatLoadingIndicator(id) {
  const element = document.getElementById(id);
  if (element) element.remove();
}

function generateMockChatResponse(message) {
  const lower = message.toLowerCase();

  const responses = {
    "how many test": `There are ${S.cases.length} test cases across ${S.suites.length} suites. The latest run had ${S.runs[0].passed} passed and ${S.runs[0].failed} failed tests.`,
    "what is the pass rate": `The current pass rate is ${S.runs[0].pass_rate}%. The latest run on ${S.runs[0].ts.toLocaleDateString()} had ${S.runs[0].passed}/${S.runs[0].total} tests passing.`,
    "which tests are failing": `In the latest run, ${S.runs[0].failed} test(s) failed. The ${S.runs[0].failed > 0 ? "main failure" : "test run was successful"} occurred in the regression suite.`,
    "what are the top failures": `The top failure is in the API tests suite, affecting the user creation endpoint. This has failed in 3 of the last 5 runs.`,
    "coverage summary": `Test coverage summary: ${Math.round((S.cases.filter((c) => c.priority === "critical").length / S.cases.length) * 100)}% critical priority, ${S.suites.filter((s) => s.active).length}/${S.suites.length} active suites.`,
    "test suites": `We have ${S.suites.length} test suites: ${S.suites.map((s) => s.name).join(", ")}.`,
    "smoke tests": `The Smoke Tests suite contains ${S.suites[0].cases} test cases and is currently ${S.suites[0].active ? "active" : "inactive"}.`,
  };

  for (const [key, response] of Object.entries(responses)) {
    if (lower.includes(key)) return response;
  }

  return `I'm here to help with test analytics. Try asking about: test count, pass rates, failing tests, coverage, or specific test suites like "smoke tests".`;
}

// Close chat on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    const widget = document.querySelector(".chat-widget");
    if (widget && widget.classList.contains("open")) {
      toggleChatWidget();
    }
  }
});

// Allow Enter key to send messages
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    const input = document.getElementById("chat-input");
    if (document.activeElement === input) {
      e.preventDefault();
      sendChatMessage();
    }
  }
});

/* ── Modal close on backdrop / Escape ── */
document.querySelectorAll(".modal-bg").forEach((el) =>
  el.addEventListener("click", (e) => {
    if (e.target === el) closeModal(el.id);
  }),
);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape")
    document
      .querySelectorAll(".modal-bg.open")
      .forEach((el) => closeModal(el.id));
});

/* ── Resize charts ── */
window.addEventListener("resize", () => {
  if (document.getElementById("view-dashboard").classList.contains("active"))
    drawTrendChart("trend-chart", S.runs);
  if (document.getElementById("view-reports").classList.contains("active"))
    drawTrendChart("report-trend-chart", S.runs);
});
