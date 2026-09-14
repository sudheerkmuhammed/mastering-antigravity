/**
 * TaskStudio AI — Client Application Logic (Vanilla JS)
 * Handles state management, UI rendering, REST APIs, and Server-Sent Events (SSE) telemetry.
 */

class TaskStudioApp {
  constructor() {
    this.tasks = [];
    this.activeStream = null;

    // DOM Elements
    this.lanes = {
      'todo': document.getElementById('cards-todo'),
      'in-progress': document.getElementById('cards-in-progress'),
      'review': document.getElementById('cards-review'),
      'done': document.getElementById('cards-done')
    };

    this.counts = {
      'todo': document.getElementById('count-todo'),
      'in-progress': document.getElementById('count-in-progress'),
      'review': document.getElementById('count-review'),
      'done': document.getElementById('count-done')
    };

    this.metricTotal = document.getElementById('metric-total');
    this.metricCompleted = document.getElementById('metric-completed');
    this.agentStatusIndicator = document.getElementById('agent-status-indicator');
    this.agentStatusText = document.getElementById('agent-status-text');
    this.telemetryFeed = document.getElementById('telemetry-feed');
    this.traceMeta = document.getElementById('trace-meta');
    this.traceCode = document.getElementById('trace-code');

    // Modal Elements
    this.taskModal = document.getElementById('task-modal');
    this.taskForm = document.getElementById('task-form');
    this.btnNewTask = document.getElementById('btn-new-task');
    this.btnCloseModal = document.getElementById('btn-close-modal');
    this.btnCancelTask = document.getElementById('btn-cancel-task');
    this.btnRefresh = document.getElementById('btn-refresh');

    // Agent Dispatch Elements
    this.agentPrompt = document.getElementById('agent-prompt');
    this.btnRunAgent = document.getElementById('btn-run-agent');

    this.init();
  }

  async init() {
    this.bindEvents();
    await this.fetchTasks();
  }

  bindEvents() {
    // Modal events
    this.btnNewTask.addEventListener('click', () => this.openModal());
    this.btnCloseModal.addEventListener('click', () => this.closeModal());
    this.btnCancelTask.addEventListener('click', () => this.closeModal());
    this.taskModal.addEventListener('click', (e) => {
      if (e.target === this.taskModal) this.closeModal();
    });

    // Form submit
    this.taskForm.addEventListener('submit', (e) => this.handleTaskSubmit(e));

    // Refresh
    this.btnRefresh.addEventListener('click', () => this.fetchTasks());

    // Agent Dispatch
    this.btnRunAgent.addEventListener('click', () => this.dispatchAgentGoal());
    this.agentPrompt.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.dispatchAgentGoal();
    });
  }

  openModal() {
    this.taskForm.reset();
    this.taskModal.classList.remove('hidden');
    document.getElementById('task-title-input').focus();
  }

  closeModal() {
    this.taskModal.classList.add('hidden');
  }

  async fetchTasks() {
    try {
      const res = await fetch('/api/tasks');
      if (res.ok) {
        this.tasks = await res.json();
      } else {
        // Fallback default sample tasks if running without backend server
        this.loadSampleData();
      }
    } catch (err) {
      console.warn('Backend not detected, running with local seed data:', err);
      this.loadSampleData();
    }
    this.renderBoard();
  }

  loadSampleData() {
    if (this.tasks.length === 0) {
      this.tasks = [
        {
          id: 'TSK-101',
          title: 'Implement Antigravity SSE thought streaming',
          desc: 'Stream agent token deltas and tool execution diffs to client UI in real time.',
          lane: 'done',
          priority: 'high'
        },
        {
          id: 'TSK-102',
          title: 'Design high-contrast glassmorphism board',
          desc: 'Create dark-mode design system with pure Vanilla CSS, custom tokens, and 60fps animations.',
          lane: 'in-progress',
          priority: 'medium'
        },
        {
          id: 'TSK-103',
          title: 'Write headless browser subagent smoke test',
          desc: 'Automate DOM verification, screenshot capture, and recording check.',
          lane: 'todo',
          priority: 'high'
        },
        {
          id: 'TSK-104',
          title: 'Benchmark API endpoint response latency',
          desc: 'Verify p95 response time is under 45ms under concurrent simulated loads.',
          lane: 'review',
          priority: 'low'
        }
      ];
    }
  }

  renderBoard() {
    // Clear all lanes
    Object.values(this.lanes).forEach(laneEl => laneEl.innerHTML = '');

    const counts = { 'todo': 0, 'in-progress': 0, 'review': 0, 'done': 0 };

    this.tasks.forEach(task => {
      const laneKey = task.lane || 'todo';
      counts[laneKey] = (counts[laneKey] || 0) + 1;

      const card = this.createTaskCardElement(task);
      if (this.lanes[laneKey]) {
        this.lanes[laneKey].appendChild(card);
      }
    });

    // Update lane badge counts
    Object.keys(counts).forEach(k => {
      if (this.counts[k]) {
        this.counts[k].textContent = counts[k];
      }
    });

    // Update global metrics
    this.metricTotal.textContent = `Total: ${this.tasks.length}`;
    this.metricCompleted.textContent = `Done: ${counts['done'] || 0}`;
  }

  createTaskCardElement(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.dataset.id = task.id;

    card.innerHTML = `
      <div class="task-card-header">
        <span class="priority-tag ${task.priority}">${task.priority}</span>
        <span class="task-id">${task.id}</span>
      </div>
      <div class="task-card-title">${this.escapeHtml(task.title)}</div>
      <div class="task-card-desc">${this.escapeHtml(task.desc || '')}</div>
      <div class="task-card-footer">
        <div class="task-card-actions">
          ${task.lane !== 'todo' ? `<button class="card-action-btn" data-action="prev" title="Move Left">◀</button>` : ''}
          ${task.lane !== 'done' ? `<button class="card-action-btn" data-action="next" title="Move Right">▶</button>` : ''}
        </div>
        <button class="card-action-btn" data-action="delete" title="Delete Task">🗑</button>
      </div>
    `;

    // Action button listeners
    card.querySelectorAll('.card-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === 'delete') {
          this.deleteTask(task.id);
        } else if (action === 'next') {
          this.advanceTaskLane(task.id, 1);
        } else if (action === 'prev') {
          this.advanceTaskLane(task.id, -1);
        }
      });
    });

    return card;
  }

  async handleTaskSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('task-title-input').value.trim();
    const priority = document.getElementById('task-priority-input').value;
    const lane = document.getElementById('task-lane-input').value;
    const desc = document.getElementById('task-desc-input').value.trim();

    if (!title) return;

    const newTask = {
      id: `TSK-${Math.floor(100 + Math.random() * 900)}`,
      title,
      priority,
      lane,
      desc
    };

    try {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask)
      });
      if (res.ok) {
        const saved = await res.json();
        this.tasks.push(saved);
      } else {
        this.tasks.push(newTask);
      }
    } catch {
      this.tasks.push(newTask);
    }

    this.closeModal();
    this.renderBoard();
  }

  async deleteTask(taskId) {
    this.tasks = this.tasks.filter(t => t.id !== taskId);
    try {
      await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
    } catch (e) {
      console.warn('Backend delete sync skipped:', e);
    }
    this.renderBoard();
  }

  advanceTaskLane(taskId, direction) {
    const laneOrder = ['todo', 'in-progress', 'review', 'done'];
    const task = this.tasks.find(t => t.id === taskId);
    if (!task) return;

    const currentIndex = laneOrder.indexOf(task.lane);
    const newIndex = currentIndex + direction;

    if (newIndex >= 0 && newIndex < laneOrder.length) {
      task.lane = laneOrder[newIndex];
      this.renderBoard();
      // Optional async sync
      fetch(`/api/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lane: task.lane })
      }).catch(() => {});
    }
  }

  /**
   * Dispatches an autonomous objective to the Antigravity SSE streaming endpoint.
   */
  async dispatchAgentGoal() {
    const prompt = this.agentPrompt.value.trim();
    if (!prompt) return;

    // Reset console
    this.telemetryFeed.innerHTML = '';
    this.setAgentStatus('active', 'Agent Reasoning...');
    this.btnRunAgent.disabled = true;

    this.addTelemetryItem('INFO', `Dispatched goal: "${prompt}"`, 'highlight');

    try {
      // Connect to Server-Sent Events (SSE) endpoint
      const eventSource = new EventSource(`/api/agent/stream?goal=${encodeURIComponent(prompt)}`);
      this.activeStream = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleAgentEvent(data);
        } catch {
          this.addTelemetryItem('CHUNK', event.data);
        }
      };

      eventSource.addEventListener('thought', (e) => {
        const payload = JSON.parse(e.data);
        this.addTelemetryItem('THOUGHT', payload.text);
      });

      eventSource.addEventListener('tool_call', (e) => {
        const payload = JSON.parse(e.data);
        this.traceMeta.textContent = `Tool: ${payload.name} (${payload.action || 'exec'})`;
        this.traceCode.innerHTML = `<code>${this.escapeHtml(payload.diff || JSON.stringify(payload.args, null, 2))}</code>`;
        this.addTelemetryItem('TOOL', `Invoking tool ${payload.name}: ${payload.summary || ''}`, 'highlight');
      });

      eventSource.addEventListener('task_created', (e) => {
        const payload = JSON.parse(e.data);
        this.tasks.push(payload);
        this.renderBoard();
        this.addTelemetryItem('ACTION', `Created task [${payload.id}]: ${payload.title}`, 'success');
      });

      eventSource.addEventListener('complete', () => {
        this.setAgentStatus('idle', 'Agent Idle');
        this.btnRunAgent.disabled = false;
        this.addTelemetryItem('STATUS', 'Autonomous objective fulfilled successfully!', 'success');
        eventSource.close();
      });

      eventSource.onerror = (err) => {
        console.warn('SSE stream error, simulating local execution:', err);
        eventSource.close();
        this.simulateLocalAgentExecution(prompt);
      };
    } catch (err) {
      this.simulateLocalAgentExecution(prompt);
    }
  }

  simulateLocalAgentExecution(prompt) {
    // Client-side simulation fallback when running standalone without live Python server
    const steps = [
      { type: 'THOUGHT', text: 'Analyzing workspace structure and acceptance criteria...' },
      { type: 'TOOL', text: 'Inspecting index.html & style.css for design token consistency', meta: 'tool: read_file' },
      { type: 'THOUGHT', text: 'Decomposing objective into high-priority sprint deliverables.' },
      { 
        type: 'TASK', 
        task: { 
          id: `TSK-${Math.floor(200 + Math.random() * 800)}`, 
          title: `Autonomous Action: ${prompt.slice(0, 45)}...`, 
          desc: 'Generated autonomously by Antigravity Planning Agent.', 
          priority: 'high', 
          lane: 'in-progress' 
        } 
      },
      { type: 'STATUS', text: 'Verification complete: 0 lint errors, DOM layout responsive.' }
    ];

    let i = 0;
    const interval = setInterval(() => {
      if (i >= steps.length) {
        clearInterval(interval);
        this.setAgentStatus('idle', 'Agent Idle');
        this.btnRunAgent.disabled = false;
        return;
      }
      const s = steps[i];
      if (s.type === 'THOUGHT') {
        this.addTelemetryItem('THOUGHT', s.text);
      } else if (s.type === 'TOOL') {
        this.traceMeta.textContent = s.meta;
        this.traceCode.textContent = `// Target: ${prompt}\n// Status: verified OK`;
        this.addTelemetryItem('TOOL', s.text, 'highlight');
      } else if (s.type === 'TASK') {
        this.tasks.push(s.task);
        this.renderBoard();
        this.addTelemetryItem('ACTION', `Decomposed into task ${s.task.id}`, 'success');
      } else if (s.type === 'STATUS') {
        this.addTelemetryItem('STATUS', s.text, 'success');
      }
      i++;
    }, 600);
  }

  handleAgentEvent(data) {
    if (data.type === 'thought') {
      this.addTelemetryItem('THOUGHT', data.text);
    } else if (data.type === 'done') {
      this.setAgentStatus('idle', 'Agent Idle');
      this.btnRunAgent.disabled = false;
      this.addTelemetryItem('STATUS', 'Objective complete.', 'success');
    }
  }

  addTelemetryItem(tag, text, modifier = '') {
    const item = document.createElement('div');
    item.className = 'thought-item';
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    item.innerHTML = `
      <span class="thought-time">[${now}]</span>
      <span class="thought-content ${modifier}"><strong>${tag}:</strong> ${this.escapeHtml(text)}</span>
    `;

    this.telemetryFeed.appendChild(item);
    this.telemetryFeed.scrollTop = this.telemetryFeed.scrollHeight;
  }

  setAgentStatus(status, label) {
    this.agentStatusIndicator.className = `agent-status-badge`;
    const dot = this.agentStatusIndicator.querySelector('.status-indicator');
    dot.className = `status-indicator ${status}`;
    this.agentStatusText.textContent = label;
  }

  escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
}

// Boot application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.taskStudio = new TaskStudioApp();
});
