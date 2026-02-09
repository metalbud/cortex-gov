const state = {
  data: null,
  selectedProject: null,
  filter: "",
};

const ui = {
  workspacePath: document.getElementById("workspace-path"),
  refreshBtn: document.getElementById("refresh-btn"),
  status: document.getElementById("status"),
  projectList: document.getElementById("project-list"),
  projectCount: document.getElementById("project-count"),
  projectDetails: document.getElementById("project-details"),
  agentsList: document.getElementById("agents-list"),
  search: document.getElementById("search"),
  spawnForm: document.getElementById("spawn-form"),
  spawnId: document.getElementById("spawn-id"),
  spawnPrefix: document.getElementById("spawn-prefix"),
  spawnCount: document.getElementById("spawn-count"),
  spawnModel: document.getElementById("spawn-model"),
  spawnHeartbeat: document.getElementById("spawn-heartbeat"),
  spawnPrompt: document.getElementById("spawn-prompt"),
  spawnBinds: document.getElementById("spawn-binds"),
};

const DEFAULT_PROMPT = (controlDoc) =>
  `Read ${controlDoc} if it exists (workspace context). Follow the rules set in that doc strictly. ` +
  `Do not infer or repeat old tasks from prior chats. Complete the first available TODO task in ${controlDoc} ` +
  `and update its status and evidence. If no task to do in ${controlDoc} reply with HEARTBEAT_OK and include your agent ID.`;

function setStatus(message, isError = false) {
  if (!message) {
    ui.status.classList.add("hidden");
    ui.status.textContent = "";
    return;
  }
  ui.status.classList.remove("hidden");
  ui.status.textContent = message;
  ui.status.style.background = isError ? "#fdecea" : "#fff1e7";
  ui.status.style.borderColor = isError ? "#f5a3a3" : "#f4c6a5";
  ui.status.style.color = isError ? "#7a1d1d" : "#7a3e18";
}

async function fetchState() {
  setStatus("Loading workspace data...");
  const res = await fetch("/api/state");
  const data = await res.json();
  state.data = data;
  if (!state.selectedProject && data.projects.length > 0) {
    state.selectedProject = data.projects[0].path;
  }
  if (state.selectedProject && !data.projects.find((p) => p.path === state.selectedProject)) {
    state.selectedProject = data.projects.length ? data.projects[0].path : null;
  }
  render();
  if (data.errors && data.errors.length) {
    setStatus(data.errors.join(" | "), true);
  } else {
    setStatus("");
  }
}

function render() {
  const data = state.data;
  if (!data) return;
  ui.workspacePath.textContent = data.workspace_root || "-";
  renderProjects();
  renderProjectDetails();
  renderAgents();
  syncSpawnDefaults();
}

function renderProjects() {
  const data = state.data;
  const filter = state.filter.toLowerCase();
  const projects = data.projects.filter((p) => {
    return (
      p.name.toLowerCase().includes(filter) ||
      p.path.toLowerCase().includes(filter)
    );
  });
  ui.projectCount.textContent = projects.length;
  ui.projectList.innerHTML = "";

  if (!projects.length) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = "No PROJECT.md folders found.";
    ui.projectList.appendChild(empty);
    return;
  }

  projects.forEach((project) => {
    const card = document.createElement("div");
    card.className = "project-card";
    if (project.path === state.selectedProject) {
      card.classList.add("active");
    }
    const title = document.createElement("div");
    title.className = "project-title";
    title.textContent = project.name;
    const meta = document.createElement("div");
    meta.className = "project-meta";
    meta.textContent = project.path;
    const pill = document.createElement("div");
    pill.className = "project-pill";
    pill.textContent = `${project.agents.length} agent${project.agents.length === 1 ? "" : "s"}`;

    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(pill);
    card.addEventListener("click", () => {
      state.selectedProject = project.path;
      render();
    });
    ui.projectList.appendChild(card);
  });
}

function renderProjectDetails() {
  const data = state.data;
  const project = data.projects.find((p) => p.path === state.selectedProject);
  if (!project) {
    ui.projectDetails.innerHTML = `<div class="project-details"><h2>No project selected</h2></div>`;
    return;
  }

  ui.projectDetails.innerHTML = `
    <div class="project-details">
      <h2>${project.name}</h2>
      <p>${project.summary || "No summary found in PROJECT.md."}</p>
      <div class="detail-row">
        <span>Path:</span>
        <code>${project.path}</code>
      </div>
      <div class="detail-row">
        <span>Control doc:</span>
        <code>${project.control_doc}</code>
      </div>
      <div class="detail-row">
        <span>Heartbeat file:</span>
        <code>${project.heartbeat_exists ? "HEARTBEAT.md present" : "Missing HEARTBEAT.md"}</code>
      </div>
    </div>
  `;
}

function renderAgents() {
  const data = state.data;
  const agents = data.agents.filter((a) => a.project_path === state.selectedProject);
  ui.agentsList.innerHTML = "";

  if (!agents.length) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = "No agents attached to this workspace yet.";
    ui.agentsList.appendChild(empty);
    return;
  }

  agents.forEach((agent) => {
    const card = document.createElement("div");
    card.className = "agent-card";
    card.innerHTML = `
      <div class="agent-header">
        <div class="agent-id">${agent.id}</div>
        <div class="agent-pill">model: ${agent.model_source}</div>
        <div class="agent-pill">heartbeat: ${agent.heartbeat_source}</div>
      </div>
      <div class="field-grid">
        <div class="field">
          <label>Model</label>
          <input class="agent-model" type="text" value="${agent.model || ""}" placeholder="inherit default" />
        </div>
        <div class="field">
          <label>Heartbeat Every</label>
          <input class="agent-heartbeat" type="text" value="${agent.heartbeat_every || ""}" placeholder="e.g. 30m, 2h" />
        </div>
      </div>
      <div class="field">
        <label>Heartbeat Prompt</label>
        <textarea class="agent-prompt" rows="3" placeholder="inherit default">${agent.heartbeat_prompt || ""}</textarea>
      </div>
      <div class="actions">
        <button class="btn primary apply-btn">Apply</button>
        <button class="btn defaults-btn" type="button">Use defaults</button>
        <button class="btn prompt-btn" type="button">Use project prompt</button>
      </div>
    `;

    const modelInput = card.querySelector(".agent-model");
    const heartbeatInput = card.querySelector(".agent-heartbeat");
    const promptInput = card.querySelector(".agent-prompt");
    const applyBtn = card.querySelector(".apply-btn");
    const defaultsBtn = card.querySelector(".defaults-btn");
    const promptBtn = card.querySelector(".prompt-btn");

    applyBtn.addEventListener("click", async (evt) => {
      evt.preventDefault();
      await updateAgent(agent.id, {
        model: modelInput.value.trim(),
        heartbeat_every: heartbeatInput.value.trim(),
        heartbeat_prompt: promptInput.value.trim(),
      });
    });

    defaultsBtn.addEventListener("click", () => {
      modelInput.value = "";
      heartbeatInput.value = "";
      promptInput.value = "";
    });

    promptBtn.addEventListener("click", () => {
      const project = data.projects.find((p) => p.path === state.selectedProject);
      if (!project) return;
      promptInput.value = DEFAULT_PROMPT(project.control_doc);
    });

    ui.agentsList.appendChild(card);
  });
}

async function updateAgent(agentId, updates) {
  setStatus(`Updating ${agentId}...`);
  const res = await fetch("/api/agents/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_id: agentId, updates }),
  });
  const payload = await res.json();
  if (!res.ok) {
    setStatus(payload.error || "Update failed", true);
    return;
  }
  state.data = payload;
  render();
  setStatus(`Updated ${agentId}.`);
}

async function createAgents(payload) {
  setStatus("Creating agents...");
  const res = await fetch("/api/agents/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    setStatus(data.error || "Creation failed", true);
    return;
  }
  state.data = data;
  render();
  setStatus("Agents created.");
}

function slugify(text) {
  return (text || "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function syncSpawnDefaults() {
  const project = state.data.projects.find((p) => p.path === state.selectedProject);
  if (!project) return;
  if (!ui.spawnPrefix.value) {
    ui.spawnPrefix.value = slugify(project.name) || slugify(project.path.split(/[\\/]/).pop());
  }
}

ui.refreshBtn.addEventListener("click", () => fetchState());
ui.search.addEventListener("input", (evt) => {
  state.filter = evt.target.value || "";
  renderProjects();
});

ui.spawnForm.addEventListener("submit", async (evt) => {
  evt.preventDefault();
  const project = state.data.projects.find((p) => p.path === state.selectedProject);
  if (!project) return;

  const binds = ui.spawnBinds.value
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);

  await createAgents({
    project_dir: project.path,
    control_doc: project.control_doc,
    agent_id: ui.spawnId.value.trim(),
    prefix: ui.spawnPrefix.value.trim(),
    count: Number(ui.spawnCount.value || 1),
    model: ui.spawnModel.value.trim(),
    heartbeat_every: ui.spawnHeartbeat.value.trim(),
    heartbeat_prompt: ui.spawnPrompt.value.trim(),
    binds,
  });
});

fetchState();
