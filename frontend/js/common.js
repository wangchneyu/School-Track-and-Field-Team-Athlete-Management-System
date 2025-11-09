const CommonUI = (() => {
  const API_BASE = '/api/v1';
  const TOKEN_KEY = 'athletics_token';
  const ROLE_KEY = 'athletics_role';

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getRole() {
    return localStorage.getItem(ROLE_KEY);
  }

  function saveAuth(token, role) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(ROLE_KEY, role);
  }

  function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
  }

  function redirectToLogin(nextUrl) {
    const target = nextUrl
      ? `/static/index.html?redirect=${encodeURIComponent(nextUrl)}`
      : '/static/index.html';
    window.location.href = target;
  }

  function buildConfig(options = {}) {
    const {
      method = 'GET',
      body,
      headers = {},
      json = true,
    } = options;
    const config = {
      method,
      headers: {
        Accept: 'application/json',
        ...headers,
      },
    };
    if (body !== undefined && body !== null) {
      if (json && !(body instanceof FormData) && typeof body !== 'string') {
        config.body = JSON.stringify(body);
        config.headers['Content-Type'] = 'application/json';
      } else {
        config.body = body;
      }
    }
    return config;
  }

  async function parseResponse(response, expectJson = true) {
    if (response.status === 204) {
      return null;
    }
    if (!response.ok) {
      let detail = '请求失败';
      try {
        const data = await response.json();
        detail = data.detail || JSON.stringify(data);
      } catch (error) {
        detail = response.statusText || detail;
      }
      throw new Error(detail);
    }
    if (!expectJson) {
      return response.text();
    }
    return response.json();
  }

  async function authFetch(path, options = {}) {
    const token = getToken();
    if (!token) {
      redirectToLogin(window.location.pathname + window.location.search);
      throw new Error('未登录');
    }
    const config = buildConfig(options);
    config.headers.Authorization = `Bearer ${token}`;
    const response = await fetch(`${API_BASE}${path}`, config);
    if (response.status === 401) {
      clearAuth();
      redirectToLogin(window.location.pathname + window.location.search);
      throw new Error('请重新登录');
    }
    return parseResponse(response, options.expectJson ?? true);
  }

  async function publicFetch(path, options = {}) {
    const config = buildConfig(options);
    const response = await fetch(`${API_BASE}${path}`, config);
    if (response.status === 404) {
      return null;
    }
    return parseResponse(response, options.expectJson ?? true);
  }

  function ensureRole(requiredRole) {
    const token = getToken();
    if (!token) {
      redirectToLogin();
      return null;
    }
    const role = getRole();
    if (requiredRole && role !== requiredRole) {
      window.location.href = role === 'admin' ? '/static/admin.html' : '/static/athlete.html';
      return null;
    }
    return { token, role };
  }

  function logout() {
    clearAuth();
    redirectToLogin();
  }

  function setStatus(element, message, type = 'info') {
    if (!element) return;
    element.textContent = message;
    element.className = `alert alert-${type}`;
  }

  function clearStatus(element) {
    if (!element) return;
    element.textContent = '';
    element.className = '';
  }

  async function fetchFeaturedEvent() {
    try {
      return await publicFetch('/featured-event');
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  function startCountdown(targetDate, displayEl) {
    if (!displayEl || !targetDate) return;
    function format(seconds) {
      const d = Math.floor(seconds / 86400);
      const h = Math.floor((seconds % 86400) / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = seconds % 60;
      return `${d}天 ${h}小时 ${m}分 ${s}秒`;
    }
    function update() {
      const diff = Math.max(0, Math.floor((targetDate - Date.now()) / 1000));
      displayEl.textContent = diff > 0 ? format(diff) : '已开始';
    }
    update();
    const intervalId = setInterval(update, 1000);
    displayEl.dataset.countdownId = String(intervalId);
  }

  async function renderCountdown(containerSelector = '[data-countdown]') {
    const widgets = document.querySelectorAll(containerSelector);
    if (!widgets.length) {
      return;
    }
    const event = await fetchFeaturedEvent();
    widgets.forEach((widget) => {
      const nameEl = widget.querySelector('[data-event-name]');
      const timeEl = widget.querySelector('[data-event-time]');
      const countdownEl = widget.querySelector('[data-event-countdown]');
      if (!event) {
        if (nameEl) nameEl.textContent = '暂无安排';
        if (timeEl) timeEl.textContent = '管理员可在后台设置';
        if (countdownEl) countdownEl.textContent = '--';
        return;
      }
      const timeText = new Date(event.start_time).toLocaleString();
      if (nameEl) nameEl.textContent = `${event.name}${event.location ? ' @ ' + event.location : ''}`;
      if (timeEl) timeEl.textContent = `开赛时间：${timeText}`;
      if (countdownEl) {
        const existing = countdownEl.dataset.countdownId;
        if (existing) {
          clearInterval(Number(existing));
        }
        startCountdown(new Date(event.start_time).getTime(), countdownEl);
      }
    });
  }

  return {
    API_BASE,
    saveAuth,
    getRole,
    getToken,
    ensureRole,
    logout,
    authFetch,
    publicFetch,
    setStatus,
    clearStatus,
    fetchFeaturedEvent,
    renderCountdown,
  };
})();

window.CommonUI = CommonUI;
