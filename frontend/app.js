/**
 * StudiesAPI Frontend — app.js
 * Connects to FastAPI backend at http://127.0.0.1:8000
 */

/* ═══════════════════════════════════════════
   CONFIG
═══════════════════════════════════════════ */
const API_BASE = 'http://127.0.0.1:8000/api/v1';

/* ═══════════════════════════════════════════
   STATE
═══════════════════════════════════════════ */
const state = {
  token: localStorage.getItem('studies_token') || null,
  user: JSON.parse(localStorage.getItem('studies_user') || 'null'),
  currentView: 'dashboard',
  sessions: [],
  stats: null,
  sessionsPage: 0,
  sessionsLimit: 10,
  sessionsHasMore: false,
  editingSessionId: null,
  pendingDeleteFn: null,
};

/* ═══════════════════════════════════════════
   API HELPERS
═══════════════════════════════════════════ */
async function apiRequest(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth && state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = data.detail
      ? (Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : data.detail)
      : `Erro ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

/* ═══════════════════════════════════════════
   AUTH
═══════════════════════════════════════════ */
function saveAuth(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem('studies_token', token);
  localStorage.setItem('studies_user', JSON.stringify(user));
}

function clearAuth() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('studies_token');
  localStorage.removeItem('studies_user');
}

async function fetchCurrentUser() {
  // We use the users list endpoint (search by id not directly exposed without auth guard)
  // We'll rely on stored user from state; if token invalid, requests will fail
  return state.user;
}

/* ═══════════════════════════════════════════
   TOAST NOTIFICATIONS
═══════════════════════════════════════════ */
function toast(msg, type = 'info') {
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `
    <span class="toast-icon">${icons[type]}</span>
    <span class="toast-msg">${msg}</span>
  `;
  container.appendChild(el);

  setTimeout(() => {
    el.classList.add('removing');
    setTimeout(() => el.remove(), 280);
  }, 3500);
}

/* ═══════════════════════════════════════════
   SPINNER HELPERS
═══════════════════════════════════════════ */
function setLoading(btn, loading) {
  const text = btn.querySelector('.btn-text');
  const spinner = btn.querySelector('.btn-spinner');
  if (!text || !spinner) return;
  btn.disabled = loading;
  text.classList.toggle('hidden', loading);
  spinner.classList.toggle('hidden', !loading);
}

/* ═══════════════════════════════════════════
   SCREEN SWITCHING
═══════════════════════════════════════════ */
function showAuthScreen() {
  document.getElementById('auth-screen').classList.remove('hidden');
  document.getElementById('app-screen').classList.add('hidden');
}

function showAppScreen() {
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('app-screen').classList.remove('hidden');
  updateSidebarUser();
  switchView('dashboard');
  loadDashboard();
}

function switchView(view) {
  state.currentView = view;

  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const viewEl = document.getElementById(`view-${view}`);
  const navEl = document.getElementById(`nav-${view}`);
  if (viewEl) viewEl.classList.add('active');
  if (navEl) navEl.classList.add('active');

  const titles = { dashboard: 'Dashboard', sessions: 'Sessões de Estudo', profile: 'Perfil' };
  document.getElementById('topbar-title').textContent = titles[view] || 'StudiesAPI';

  // Load data for each view
  if (view === 'dashboard') loadDashboard();
  else if (view === 'sessions') { state.sessionsPage = 0; loadSessions(); }
  else if (view === 'profile') loadProfile();

  closeSidebar();
}

/* ═══════════════════════════════════════════
   USER INFO IN SIDEBAR
═══════════════════════════════════════════ */
function updateSidebarUser() {
  const user = state.user;
  if (!user) return;
  const initials = (user.username || user.email || 'U').charAt(0).toUpperCase();
  document.getElementById('sidebar-avatar').textContent = initials;
  document.getElementById('sidebar-username').textContent = user.username || 'Usuário';
  document.getElementById('sidebar-email').textContent = user.email || '';
}

/* ═══════════════════════════════════════════
   SIDEBAR MOBILE
═══════════════════════════════════════════ */
function openSidebar() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('sidebar-overlay').classList.remove('hidden');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.add('hidden');
}

/* ═══════════════════════════════════════════
   AUTH FORMS
═══════════════════════════════════════════ */
function switchToLogin() {
  document.getElementById('login-form-wrapper').classList.add('active');
  document.getElementById('register-form-wrapper').classList.remove('active');
}
function switchToRegister() {
  document.getElementById('register-form-wrapper').classList.add('active');
  document.getElementById('login-form-wrapper').classList.remove('active');
}

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('login-error');
  errEl.classList.add('hidden');

  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  setLoading(btn, true);
  try {
    const data = await apiRequest('/auth/token', {
      method: 'POST',
      body: { email, password },
      auth: false,
    });

    // Fetch users to find current user (simple approach — list self)
    // Store minimal user info from what we know
    const tempUser = { email };
    saveAuth(data.access_token, tempUser);

    // Now try to get the real user info
    try {
      const users = await apiRequest(`/users/?search=${encodeURIComponent(email)}`);
      const found = users.users.find(u => u.email === email);
      if (found) {
        saveAuth(data.access_token, found);
      }
    } catch (_) { /* silent */ }

    toast('Login realizado com sucesso!', 'success');
    showAppScreen();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    setLoading(btn, false);
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const btn = document.getElementById('register-btn');
  const errEl = document.getElementById('register-error');
  const successEl = document.getElementById('register-success');
  errEl.classList.add('hidden');
  successEl.classList.add('hidden');

  const username = document.getElementById('reg-username').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;

  if (username.length < 6) {
    errEl.textContent = 'O usuário deve ter no mínimo 6 caracteres.';
    errEl.classList.remove('hidden');
    return;
  }
  if (password.length < 8) {
    errEl.textContent = 'A senha deve ter no mínimo 8 caracteres.';
    errEl.classList.remove('hidden');
    return;
  }

  setLoading(btn, true);
  try {
    await apiRequest('/users/', {
      method: 'POST',
      body: { username, email, password },
      auth: false,
    });

    successEl.textContent = 'Conta criada! Redirecionando para o login...';
    successEl.classList.remove('hidden');
    document.getElementById('register-form').reset();

    setTimeout(() => {
      switchToLogin();
      document.getElementById('login-email').value = email;
    }, 1500);
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    setLoading(btn, false);
  }
}

/* ═══════════════════════════════════════════
   DASHBOARD
═══════════════════════════════════════════ */
async function loadDashboard() {
  await Promise.all([loadStats(), loadRecentSessions()]);
}

async function loadStats() {
  try {
    const s = await apiRequest('/stats/');
    state.stats = s;
    document.getElementById('stat-total-sessions').textContent = s.total_sessions ?? 0;
    document.getElementById('stat-total-minutes').textContent = s.total_minutes ?? 0;
    document.getElementById('stat-top-topic').textContent = s.most_studied_topic || '—';
    document.getElementById('stat-total-hours').textContent =
      s.total_minutes ? (s.total_minutes / 60).toFixed(1) + 'h' : '0h';

    // Remove loading state
    ['stat-sessions','stat-time','stat-topic','stat-hours'].forEach(id => {
      document.getElementById(id)?.classList.remove('loading-card');
    });
  } catch (err) {
    console.error('Stats error:', err);
  }
}

async function loadRecentSessions() {
  try {
    const data = await apiRequest('/sessions/sessions?limit=5&offset=0');
    const sessions = data.sessions || [];
    state.sessions = sessions;

    const tbody = document.getElementById('recent-sessions-body');
    if (sessions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="table-empty">Nenhuma sessão encontrada. Crie sua primeira sessão!</td></tr>`;
      document.getElementById('topic-chart').innerHTML = `<p class="chart-empty">Nenhum dado disponível ainda.</p>`;
      return;
    }

    tbody.innerHTML = sessions.map(s => `
      <tr>
        <td class="table-topic">${escapeHtml(s.topic)}</td>
        <td><span class="table-badge">${s.duration_minutes} min</span></td>
        <td>${formatDate(s.date)}</td>
        <td style="color:var(--text-muted);font-size:12.5px;">${escapeHtml(s.notes || '—')}</td>
      </tr>
    `).join('');

    renderTopicChart(sessions);
  } catch (err) {
    console.error('Recent sessions error:', err);
  }
}

function renderTopicChart(sessions) {
  // Group by topic, sum minutes
  const topicMap = {};
  sessions.forEach(s => {
    topicMap[s.topic] = (topicMap[s.topic] || 0) + s.duration_minutes;
  });

  const sorted = Object.entries(topicMap).sort((a, b) => b[1] - a[1]).slice(0, 8);
  const max = sorted[0]?.[1] || 1;

  const chart = document.getElementById('topic-chart');
  if (sorted.length === 0) {
    chart.innerHTML = `<p class="chart-empty">Nenhum dado disponível.</p>`;
    return;
  }

  chart.innerHTML = sorted.map(([topic, minutes], i) => `
    <div class="chart-bar-row" style="animation-delay:${i * 0.06}s">
      <span class="chart-bar-label">${escapeHtml(topic)}</span>
      <div class="chart-bar-track">
        <div class="chart-bar-fill" style="width:${(minutes / max) * 100}%;animation-delay:${i * 0.06}s"></div>
      </div>
      <span class="chart-bar-value">${minutes} min</span>
    </div>
  `).join('');
}

/* ═══════════════════════════════════════════
   SESSIONS
═══════════════════════════════════════════ */
async function loadSessions(search = '') {
  const tbody = document.getElementById('sessions-body');
  tbody.innerHTML = `<tr><td colspan="6" class="table-empty">Carregando...</td></tr>`;

  const offset = state.sessionsPage * state.sessionsLimit;
  const searchParam = search ? `&search=${encodeURIComponent(search)}` : '';

  try {
    const data = await apiRequest(
      `/sessions/sessions?offset=${offset}&limit=${state.sessionsLimit}${searchParam}`
    );
    const sessions = data.sessions || [];
    state.sessions = sessions;
    state.sessionsHasMore = sessions.length === state.sessionsLimit;

    if (sessions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="table-empty">Nenhuma sessão encontrada.</td></tr>`;
    } else {
      tbody.innerHTML = sessions.map((s, i) => `
        <tr style="animation-delay:${i * 0.04}s">
          <td style="color:var(--text-muted);font-size:12px;">${s.id}</td>
          <td class="table-topic">${escapeHtml(s.topic)}</td>
          <td><span class="table-badge">${s.duration_minutes} min</span></td>
          <td>${formatDate(s.date)}</td>
          <td style="color:var(--text-muted);font-size:12.5px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(s.notes || '—')}</td>
          <td>
            <div class="table-actions">
              <button class="action-btn action-btn-edit" onclick="openEditSession(${s.id})" title="Editar">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
              <button class="action-btn action-btn-delete" onclick="confirmDeleteSession(${s.id})" title="Excluir">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
              </button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    // Pagination
    document.getElementById('pagination-info').textContent = `Página ${state.sessionsPage + 1}`;
    document.getElementById('prev-page-btn').disabled = state.sessionsPage === 0;
    document.getElementById('next-page-btn').disabled = !state.sessionsHasMore;

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="table-empty">Erro: ${err.message}</td></tr>`;
  }
}

/* ── SESSION MODAL ── */
function openCreateSession() {
  state.editingSessionId = null;
  document.getElementById('session-modal-title').textContent = 'Nova Sessão';
  document.getElementById('session-form-submit').querySelector('.btn-text').textContent = 'Criar';
  document.getElementById('session-form').reset();
  document.getElementById('s-date').value = todayStr();
  document.getElementById('notes-counter').textContent = '0/120';
  document.getElementById('session-form-error').classList.add('hidden');
  showModal('session-modal-overlay');
}

async function openEditSession(id) {
  state.editingSessionId = id;
  document.getElementById('session-modal-title').textContent = 'Editar Sessão';
  document.getElementById('session-form-submit').querySelector('.btn-text').textContent = 'Salvar';
  document.getElementById('session-form-error').classList.add('hidden');

  try {
    const s = await apiRequest(`/sessions/sessions/${id}`);
    document.getElementById('s-topic').value = s.topic || '';
    document.getElementById('s-duration').value = s.duration_minutes || '';
    document.getElementById('s-date').value = s.date || '';
    document.getElementById('s-notes').value = s.notes || '';
    const notes = document.getElementById('s-notes').value;
    document.getElementById('notes-counter').textContent = `${notes.length}/120`;
    showModal('session-modal-overlay');
  } catch (err) {
    toast(`Erro ao carregar sessão: ${err.message}`, 'error');
  }
}

async function handleSessionForm(e) {
  e.preventDefault();
  const btn = document.getElementById('session-form-submit');
  const errEl = document.getElementById('session-form-error');
  errEl.classList.add('hidden');

  const topic = document.getElementById('s-topic').value.trim();
  const duration_minutes = parseInt(document.getElementById('s-duration').value);
  const date = document.getElementById('s-date').value;
  const notes = document.getElementById('s-notes').value.trim() || null;

  if (!topic || !duration_minutes || !date) {
    errEl.textContent = 'Preencha todos os campos obrigatórios.';
    errEl.classList.remove('hidden');
    return;
  }

  setLoading(btn, true);
  try {
    if (state.editingSessionId) {
      await apiRequest(`/sessions/sessions/${state.editingSessionId}`, {
        method: 'PUT',
        body: { topic, duration_minutes, date, notes },
      });
      toast('Sessão atualizada!', 'success');
    } else {
      await apiRequest('/sessions/session', {
        method: 'POST',
        body: { topic, duration_minutes, date, notes },
      });
      toast('Sessão criada!', 'success');
    }

    hideModal('session-modal-overlay');
    loadSessions(document.getElementById('session-search').value.trim());
    if (state.currentView === 'dashboard') loadDashboard();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    setLoading(btn, false);
  }
}

function confirmDeleteSession(id) {
  document.getElementById('confirm-modal-message').textContent =
    `Tem certeza que deseja excluir a sessão #${id}? Esta ação é irreversível.`;
  state.pendingDeleteFn = () => deleteSession(id);
  showModal('confirm-modal-overlay');
}

async function deleteSession(id) {
  const btn = document.getElementById('confirm-ok-btn');
  setLoading(btn, true);
  try {
    await apiRequest(`/sessions/sessions/${id}`, { method: 'DELETE' });
    toast('Sessão excluída!', 'success');
    hideModal('confirm-modal-overlay');
    loadSessions(document.getElementById('session-search').value.trim());
    if (state.currentView === 'dashboard') loadDashboard();
  } catch (err) {
    toast(`Erro: ${err.message}`, 'error');
  } finally {
    setLoading(btn, false);
  }
}

/* ═══════════════════════════════════════════
   PROFILE
═══════════════════════════════════════════ */
function loadProfile() {
  const user = state.user;
  if (!user) return;

  const initials = (user.username || user.email || 'U').charAt(0).toUpperCase();
  document.getElementById('profile-avatar-big').textContent = initials;
  document.getElementById('profile-name').textContent = user.username || '—';
  document.getElementById('profile-email-display').textContent = user.email || '—';

  // Pre-fill form with current values
  document.getElementById('upd-username').value = user.username || '';
  document.getElementById('upd-email').value = user.email || '';
  document.getElementById('upd-password').value = '';
}

async function handleUpdateProfile(e) {
  e.preventDefault();
  const btn = document.getElementById('update-profile-btn');
  const errEl = document.getElementById('profile-update-error');
  const successEl = document.getElementById('profile-update-success');
  errEl.classList.add('hidden');
  successEl.classList.add('hidden');

  const user = state.user;
  if (!user?.id) {
    errEl.textContent = 'Sessão expirada. Faça login novamente.';
    errEl.classList.remove('hidden');
    return;
  }

  const username = document.getElementById('upd-username').value.trim();
  const email = document.getElementById('upd-email').value.trim();
  const password = document.getElementById('upd-password').value;

  const body = {};
  if (username && username !== user.username) body.username = username;
  if (email && email !== user.email) body.email = email;
  if (password) {
    if (password.length < 8) {
      errEl.textContent = 'A senha deve ter no mínimo 8 caracteres.';
      errEl.classList.remove('hidden');
      return;
    }
    body.password = password;
  }

  if (Object.keys(body).length === 0) {
    errEl.textContent = 'Nenhuma alteração detectada.';
    errEl.classList.remove('hidden');
    return;
  }

  setLoading(btn, true);
  try {
    const updated = await apiRequest(`/users/${user.id}`, {
      method: 'PUT',
      body,
    });
    saveAuth(state.token, updated);
    updateSidebarUser();
    loadProfile();
    successEl.textContent = 'Perfil atualizado com sucesso!';
    successEl.classList.remove('hidden');
    document.getElementById('upd-password').value = '';
    toast('Perfil atualizado!', 'success');
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    setLoading(btn, false);
  }
}

async function handleDeleteAccount() {
  const user = state.user;
  if (!user?.id) return;

  document.getElementById('confirm-modal-message').textContent =
    'Tem certeza que deseja excluir sua conta? Todos os seus dados e sessões serão apagados permanentemente.';
  state.pendingDeleteFn = async () => {
    const btn = document.getElementById('confirm-ok-btn');
    setLoading(btn, true);
    try {
      await apiRequest(`/users/${user.id}`, { method: 'DELETE' });
      hideModal('confirm-modal-overlay');
      clearAuth();
      toast('Conta excluída. Até logo!', 'info');
      setTimeout(() => showAuthScreen(), 1000);
    } catch (err) {
      toast(`Erro: ${err.message}`, 'error');
    } finally {
      setLoading(btn, false);
    }
  };
  showModal('confirm-modal-overlay');
}

/* ═══════════════════════════════════════════
   MODAL HELPERS
═══════════════════════════════════════════ */
function showModal(id) {
  document.getElementById(id).classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function hideModal(id) {
  document.getElementById(id).classList.add('hidden');
  document.body.style.overflow = '';
}

/* ═══════════════════════════════════════════
   UTILS
═══════════════════════════════════════════ */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
  } catch {
    return dateStr;
  }
}

function todayStr() {
  const d = new Date();
  return d.toISOString().split('T')[0];
}

/* ═══════════════════════════════════════════
   TOGGLE PASSWORD VISIBILITY
═══════════════════════════════════════════ */
function initTogglePasswords() {
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      const input = document.getElementById(targetId);
      if (!input) return;
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';

      const svgPath = btn.querySelector('path');
      // Simple visual toggle via opacity
      btn.style.opacity = isPassword ? '1' : '0.5';
    });
  });
}

/* ═══════════════════════════════════════════
   LOGOUT
═══════════════════════════════════════════ */
function logout() {
  clearAuth();
  showAuthScreen();
  switchToLogin();
  toast('Sessão encerrada.', 'info');
}

/* ═══════════════════════════════════════════
   INIT & EVENT LISTENERS
═══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  initTogglePasswords();

  // ── INITIAL SCREEN ──
  if (state.token && state.user) {
    showAppScreen();
  } else {
    showAuthScreen();
  }

  // ── AUTH FORMS ──
  document.getElementById('go-to-register').addEventListener('click', switchToRegister);
  document.getElementById('go-to-login').addEventListener('click', switchToLogin);
  document.getElementById('login-form').addEventListener('submit', handleLogin);
  document.getElementById('register-form').addEventListener('submit', handleRegister);

  // ── SIDEBAR NAVIGATION ──
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => switchView(btn.dataset.view));
  });

  document.getElementById('sidebar-toggle').addEventListener('click', openSidebar);
  document.getElementById('sidebar-close').addEventListener('click', closeSidebar);
  document.getElementById('sidebar-overlay').addEventListener('click', closeSidebar);

  // ── TOPBAR NEW SESSION ──
  document.getElementById('topbar-new-session-btn').addEventListener('click', () => {
    switchView('sessions');
    setTimeout(openCreateSession, 100);
  });

  // ── LOGOUT ──
  document.getElementById('logout-btn').addEventListener('click', logout);

  // ── DASHBOARD ──
  document.getElementById('view-all-sessions-btn').addEventListener('click', () => switchView('sessions'));

  // ── SESSIONS ──
  document.getElementById('new-session-btn').addEventListener('click', openCreateSession);

  document.getElementById('session-search-btn').addEventListener('click', () => {
    state.sessionsPage = 0;
    loadSessions(document.getElementById('session-search').value.trim());
  });

  document.getElementById('session-clear-btn').addEventListener('click', () => {
    document.getElementById('session-search').value = '';
    state.sessionsPage = 0;
    loadSessions();
  });

  document.getElementById('session-search').addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      state.sessionsPage = 0;
      loadSessions(document.getElementById('session-search').value.trim());
    }
  });

  document.getElementById('prev-page-btn').addEventListener('click', () => {
    if (state.sessionsPage > 0) {
      state.sessionsPage--;
      loadSessions(document.getElementById('session-search').value.trim());
    }
  });

  document.getElementById('next-page-btn').addEventListener('click', () => {
    if (state.sessionsHasMore) {
      state.sessionsPage++;
      loadSessions(document.getElementById('session-search').value.trim());
    }
  });

  // ── SESSION MODAL ──
  document.getElementById('session-form').addEventListener('submit', handleSessionForm);

  document.getElementById('session-modal-close').addEventListener('click', () =>
    hideModal('session-modal-overlay'));
  document.getElementById('session-modal-cancel').addEventListener('click', () =>
    hideModal('session-modal-overlay'));
  document.getElementById('session-modal-overlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) hideModal('session-modal-overlay');
  });

  // Notes character counter
  document.getElementById('s-notes').addEventListener('input', e => {
    document.getElementById('notes-counter').textContent = `${e.target.value.length}/120`;
  });

  // ── CONFIRM MODAL ──
  document.getElementById('confirm-modal-close').addEventListener('click', () =>
    hideModal('confirm-modal-overlay'));
  document.getElementById('confirm-cancel-btn').addEventListener('click', () =>
    hideModal('confirm-modal-overlay'));
  document.getElementById('confirm-modal-overlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) hideModal('confirm-modal-overlay');
  });
  document.getElementById('confirm-ok-btn').addEventListener('click', () => {
    if (state.pendingDeleteFn) {
      state.pendingDeleteFn();
      state.pendingDeleteFn = null;
    }
  });

  // ── PROFILE ──
  document.getElementById('update-profile-form').addEventListener('submit', handleUpdateProfile);
  document.getElementById('delete-account-btn').addEventListener('click', handleDeleteAccount);

  // ── KEYBOARD: ESC closes modal ──
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      hideModal('session-modal-overlay');
      hideModal('confirm-modal-overlay');
    }
  });

  // ── TOKEN REFRESH: refresh silently every 20 min ──
  setInterval(async () => {
    if (!state.token) return;
    try {
      const data = await apiRequest('/auth/refresh_token', { method: 'POST' });
      state.token = data.access_token;
      localStorage.setItem('studies_token', data.access_token);
    } catch (_) {
      // Expired — let natural 401 errors handle it
    }
  }, 20 * 60 * 1000);
});
