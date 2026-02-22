const state = {
  data: null,
  selectedProject: null,
  filter: "",
  currentProjectMdContent: "",
};

const ui = {
  workspacePath: document.getElementById("workspace-path"),
  refreshBtn: document.getElementById("refresh-btn"),
  status: document.getElementById("status"),
  projectList: document.getElementById("project-list"),
  projectCount: document.getElementById("project-count"),
  projectDetails: document.getElementById("project-details"),
  projectMdDisplay: document.getElementById("project-md-display"),
  projectMdEditor: document.getElementById("project-md-editor"),
  projectMdTextarea: document.getElementById("project-md-textarea"),
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
  refreshProjectMdBtn: document.getElementById("refresh-project-md"),
  toggleEditModeBtn: document.getElementById("toggle-edit-mode"),
  saveProjectMdBtn: document.getElementById("save-project-md"),
  cancelEditBtn: document.getElementById("cancel-edit"),
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

async function loadProjectMdContent(projectPath) {
  if (!projectPath) {
    ui.projectMdDisplay.innerHTML = '<p class="placeholder">No project selected</p>';
    return;
  }
  
  try {
    setStatus("Loading PROJECT.md...");
    const response = await fetch(`/api/project-content?path=${encodeURIComponent(projectPath)}`);
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.error || "Failed to load PROJECT.md");
    }
    
    // Store content for potential editing
    state.currentProjectMdContent = result.content;
    
    // Simple markdown rendering
    const markdownContent = result.content;
    const htmlContent = markdownToHtml(markdownContent);
    ui.projectMdDisplay.innerHTML = htmlContent;
    ui.projectMdTextarea.value = markdownContent;
    setStatus("");
  } catch (error) {
    ui.projectMdDisplay.innerHTML = `<p class="placeholder error">Error loading PROJECT.md: ${error.message}</p>`;
    setStatus(`Error loading PROJECT.md: ${error.message}`, true);
  }
}

async function saveProjectMdContent(projectPath, content) {
  if (!projectPath) {
    setStatus("No project selected", true);
    return false;
  }
  
  try {
    setStatus("Saving PROJECT.md...");
    const response = await fetch('/api/project-content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        path: projectPath,
        content: content
      })
    });
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.error || "Failed to save PROJECT.md");
    }
    
    setStatus("PROJECT.md saved successfully!");
    return true;
  } catch (error) {
    setStatus(`Error saving PROJECT.md: ${error.message}`, true);
    return false;
  }
}

function toggleEditMode(enabled) {
  if (enabled) {
    // Switch to edit mode
    ui.projectMdDisplay.style.display = 'none';
    ui.projectMdEditor.style.display = 'block';
    ui.toggleEditModeBtn.textContent = 'View';
    ui.projectMdTextarea.focus();
  } else {
    // Switch to view mode
    ui.projectMdDisplay.style.display = 'block';
    ui.projectMdEditor.style.display = 'none';
    ui.toggleEditModeBtn.textContent = 'Edit';
  }
}

// More robust markdown to HTML converter for PROJECT.md
function markdownToHtml(md) {
  let html = md;
  
  // Split content into lines to process them individually
  const lines = html.split('\n');
  let result = [];
  let inUl = false;
  let inOl = false;
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    let trimmedLine = line.trim();
    
    // Handle headings
    if (trimmedLine.startsWith('# ')) {
      if (inUl) { result.push('</ul>'); inUl = false; }
      if (inOl) { result.push('</ol>'); inOl = false; }
      result.push(`<h1>${escapeHtml(trimmedLine.substring(2))}</h1>`);
      continue;
    } else if (trimmedLine.startsWith('## ')) {
      if (inUl) { result.push('</ul>'); inUl = false; }
      if (inOl) { result.push('</ol>'); inOl = false; }
      result.push(`<h2>${escapeHtml(trimmedLine.substring(3))}</h2>`);
      continue;
    } else if (trimmedLine.startsWith('### ')) {
      if (inUl) { result.push('</ul>'); inUl = false; }
      if (inOl) { result.push('</ol>'); inOl = false; }
      result.push(`<h3>${escapeHtml(trimmedLine.substring(4))}</h3>`);
      continue;
    }
    
    // Handle list items
    if (trimmedLine.match(/^\d+\.\s+/)) { // Ordered list item
      if (inUl) { result.push('</ul>'); inUl = false; }
      if (!inOl) { result.push('<ol>'); inOl = true; }
      const content = trimmedLine.replace(/^\d+\.\s+/, '');
      result.push(`<li>${processInlineMarkdown(escapeHtml(content))}</li>`);
      continue;
    } else if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) { // Unordered list item
      if (inOl) { result.push('</ol>'); inOl = false; }
      if (!inUl) { result.push('<ul>'); inUl = true; }
      const content = trimmedLine.replace(/^[-*]\s+/, '');
      result.push(`<li>${processInlineMarkdown(escapeHtml(content))}</li>`);
      continue;
    }
    
    // Handle blank lines to close lists
    if (!trimmedLine) {
      if (inUl) { result.push('</ul>'); inUl = false; }
      if (inOl) { result.push('</ol>'); inOl = false; }
      continue;
    }
    
    // Handle regular paragraphs
    if (inUl) { result.push('</ul>'); inUl = false; }
    if (inOl) { result.push('</ol>'); inOl = false; }
    
    // Handle code blocks (fenced)
    if (trimmedLine.startsWith('```')) {
      // Find the closing ```
      let codeBlock = [];
      i++; // Move to next line
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeBlock.push(lines[i]);
        i++;
      }
      result.push(`<pre><code>${escapeHtml(codeBlock.join('\n'))}</code></pre>`);
      continue;
    }
    
    // Regular paragraph with inline markdown
    result.push(`<p>${processInlineMarkdown(escapeHtml(trimmedLine))}</p>`);
  }
  
  // Close any remaining open lists
  if (inUl) { result.push('</ul>'); }
  if (inOl) { result.push('</ol>'); }
  
  return result.join('');
}

// Process inline markdown elements (bold, italic, code, links)
function processInlineMarkdown(text) {
  return text
    // Bold: **text** or __text__
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    // Code: `code`
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // Links: [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
}

// Simple HTML escaping function
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderProjectDetails() {
  const data = state.data;
  const project = data.projects.find((p) => p.path === state.selectedProject);
  if (!project) {
    ui.projectDetails.innerHTML = `<div class="project-details"><h2>No project selected</h2></div>`;
    loadProjectMdContent(null);
    toggleEditMode(false); // Ensure we're in view mode
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
  
  // Load PROJECT.md content for the selected project
  loadProjectMdContent(project.path);
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
ui.refreshProjectMdBtn.addEventListener("click", () => {
  const project = state.data?.projects?.find((p) => p.path === state.selectedProject);
  if (project) {
    loadProjectMdContent(project.path);
  }
});

ui.toggleEditModeBtn.addEventListener("click", () => {
  const project = state.data?.projects?.find((p) => p.path === state.selectedProject);
  if (!project) {
    setStatus("Please select a project first", true);
    return;
  }
  
  // Toggle between edit and view modes
  const isCurrentlyEditing = ui.projectMdEditor.style.display !== 'none';
  toggleEditMode(!isCurrentlyEditing);
});

ui.saveProjectMdBtn.addEventListener("click", async () => {
  const project = state.data?.projects?.find((p) => p.path === state.selectedProject);
  if (!project) {
    setStatus("Please select a project first", true);
    return;
  }
  
  const newContent = ui.projectMdTextarea.value;
  const success = await saveProjectMdContent(project.path, newContent);
  
  if (success) {
    // Reload the content to update the display
    loadProjectMdContent(project.path);
    // Switch back to view mode
    toggleEditMode(false);
  }
});

ui.cancelEditBtn.addEventListener("click", () => {
  // Confirm if there are unsaved changes
  if (state.currentProjectMdContent !== ui.projectMdTextarea.value) {
    const confirmed = confirm("You have unsaved changes. Are you sure you want to cancel?");
    if (!confirmed) return;
  }
  
  // Reload the content to revert any changes
  const project = state.data?.projects?.find((p) => p.path === state.selectedProject);
  if (project) {
    loadProjectMdContent(project.path);
  }
  
  // Switch back to view mode
  toggleEditMode(false);
});

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
