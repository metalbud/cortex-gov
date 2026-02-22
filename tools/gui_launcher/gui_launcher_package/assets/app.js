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

function modelToString(model) {
  if (!model) return "";
  if (typeof model === "string") return model;
  if (typeof model === "object") {
    if (model.primary) return model.primary;
    return "";
  }
  return String(model);
}

function setStatus(message, isError = false) {
  if (!message) {
    ui.status.classList.add("hidden");
    ui.status.textContent = "";
    return;
  }
  ui.status.classList.remove("hidden");
  ui.status.textContent = message;
  ui.status.style.background = isError ? "#fee2e2" : "#ecfdf5";
  ui.status.style.borderColor = isError ? "#fca5a5" : "#6ee7b7";
  ui.status.style.color = isError ? "#991b1b" : "#166534";
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
    empty.className = "empty-state";
    empty.innerHTML = `
      <div class="empty-icon">📁</div>
      <h3>No projects found</h3>
      <p>Try adjusting your search or rescan the workspace</p>
    `;
    ui.projectList.appendChild(empty);
    return;
  }

  projects.forEach((project) => {
    const card = document.createElement("div");
    card.className = "project-card";
    if (project.path === state.selectedProject) {
      card.classList.add("active");
    }
    
    // Status indicator
    const statusDot = project.heartbeat_exists ? 
      '<div class="status-dot active"></div>' : 
      '<div class="status-dot inactive"></div>';
    
    // Progress bar
    const completedTasks = project.tasks ? project.tasks.filter(t => t.completed).length : 0;
    const totalTasks = project.tasks ? project.tasks.length : 0;
    const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
    
    const header = document.createElement("div");
    header.className = "project-header";
    header.innerHTML = `
      <div class="project-info">
        <div class="project-title">${project.name}</div>
        <div class="project-meta">${project.path}</div>
      </div>
      <div class="status-dot-container">
        ${statusDot}
      </div>
    `;
    
    const footer = document.createElement("div");
    footer.className = "project-footer";
    footer.innerHTML = `
      <div class="project-pill">
        ${project.agents.length} agent${project.agents.length === 1 ? "" : "s"}
      </div>
      <div class="progress-bar-mini">
        <div class="progress-fill" style="width: ${progress}%"></div>
      </div>
      <div class="project-pill">
        ${completedTasks}/${totalTasks} tasks
      </div>
    `;
    
    card.appendChild(header);
    card.appendChild(footer);
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
    ui.projectDetails.innerHTML = `
      <div class="project-details empty">
        <h2>No project selected</h2>
        <p>Select a project from the sidebar to view details</p>
      </div>
    `;
    return;
  }

  ui.projectDetails.innerHTML = `
    <div class="project-details fade-in-up">
      <div class="project-header">
        <h1 class="brand-title">${project.name}</h1>
        <p class="brand-subtitle">${project.summary || "No summary available"}</p>
      </div>
      
      <div class="form-grid">
        <div class="agent-card">
          <div class="agent-header">
            <div class="agent-info">
              <div class="section-title">
                <svg class="icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
                Overview
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Path</label>
            <div class="project-pill">${project.path}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Control Document</label>
            <div class="project-pill">${project.control_doc}</div>
          </div>
          <div class="form-group">
            <label class="form-label">Heartbeat</label>
            <div class="project-pill ${project.heartbeat_exists ? '' : 'inactive'}">
              ${project.heartbeat_exists ? '✓ Present' : '✗ Missing'}
            </div>
          </div>
        </div>
        
        <div class="agent-card">
          <div class="agent-header">
            <div class="agent-info">
              <div class="section-title">
                <svg class="icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 11l3 3L22 4"/>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                </svg>
                Statistics
              </div>
            </div>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Epics</label>
              <div class="project-pill">${project.epics ? project.epics.length : 0}</div>
            </div>
            <div class="form-group">
              <label class="form-label">Tasks</label>
              <div class="project-pill">${project.tasks ? project.tasks.length : 0}</div>
            </div>
            <div class="form-group">
              <label class="form-label">Agents</label>
              <div class="project-pill">${project.agents.length}</div>
            </div>
            <div class="form-group">
              <label class="form-label">Complete</label>
              <div class="project-pill">
                ${project.tasks && project.tasks.length > 0 
                  ? Math.round((project.tasks.filter(t => t.completed).length / project.tasks.length) * 100) + '%'
                  : '0%'}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      ${project.epics && project.epics.length > 0 ? `
        <h2 class="brand-title">Epics</h2>
        <div class="agents-container">
          ${project.epics.map(epic => `
            <div class="agent-card">
              <div class="project-pill">${epic.id}</div>
              <div class="project-title">${epic.title}</div>
            </div>
          `).join('')}
        </div>
      ` : ''}
      
      ${project.tasks && project.tasks.length > 0 ? `
        <h2 class="brand-title">Tasks</h2>
        <div class="agents-container">
          ${project.tasks.map(task => `
            <div class="agent-card ${task.completed ? 'completed' : ''}">
              <div class="project-pill">${task.completed ? '✓' : '○'}</div>
              <div class="project-pill">${task.id}</div>
              <div class="project-title">${task.title}</div>
            </div>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `;
}

function renderAgents() {
  const data = state.data;
  const agents = data.agents.filter((a) => a.project_path === state.selectedProject);
  ui.agentsList.innerHTML = "";

  if (!agents.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = `
      <div class="empty-icon">🤖</div>
      <h3>No agents yet</h3>
      <p>Create your first agent using the form below</p>
    `;
    ui.agentsList.appendChild(empty);
    return;
  }

  agents.forEach((agent) => {
    const card = document.createElement("div");
    card.className = "agent-card fade-in-up";
    card.innerHTML = `
      <div class="agent-header">
        <div class="agent-info">
          <div class="agent-id">${agent.id}</div>
          <div class="agent-workspace">${agent.workspace}</div>
        </div>
        <div class="agent-status">
          <div class="agent-pill">model: ${modelToString(agent.model) || 'default'}</div>
          <div class="agent-pill">heartbeat: ${agent.heartbeat_every || 'default'}</div>
        </div>
      </div>
      
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Model Override</label>
          <input class="modern-input agent-model" type="text" 
                 value="${modelToString(agent.model)}" 
                 placeholder="Leave empty to inherit default" />
        </div>
        <div class="form-group">
          <label class="form-label">Heartbeat Interval</label>
          <input class="modern-input agent-heartbeat" type="text" 
                 value="${agent.heartbeat_every || ""}" 
                 placeholder="e.g. 30m, 2h" />
        </div>
        <div class="form-group full-width">
          <label class="form-label">Heartbeat Prompt</label>
          <textarea class="modern-textarea agent-prompt" rows="3"
                    placeholder="Leave empty to inherit default">${agent.heartbeat_prompt || ""}</textarea>
        </div>
      </div>
      
      <div class="form-actions">
        <button class="modern-btn modern-btn-primary apply-btn">Apply Changes</button>
        <button class="modern-btn modern-btn-secondary defaults-btn">Use Defaults</button>
        <button class="modern-btn modern-btn-secondary prompt-btn">Use Project Prompt</button>
      </div>
    `;

    const modelInput = card.querySelector(".agent-model");
    const heartbeatInput = card.querySelector(".agent-heartbeat");
    const promptInput = card.querySelector(".agent-prompt");
    const applyBtn = card.querySelector(".apply-btn");
    const defaultsBtn = card.querySelector(".defaults-btn");
    const promptBtn = card.querySelector(".prompt-btn");

    applyBtn.addEventListener("click", async () => {
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
      if (project) {
        promptInput.value = DEFAULT_PROMPT(project.control_doc);
      }
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
  setStatus(`✓ Updated ${agentId}`);
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
  setStatus(`✓ Created agent(s)`);
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