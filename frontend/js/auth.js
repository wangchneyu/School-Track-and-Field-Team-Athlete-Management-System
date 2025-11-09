document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const modeButtons = document.querySelectorAll('[data-mode]');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const messageEl = document.getElementById('loginMessage');
  const search = new URLSearchParams(window.location.search);
  const redirectTo = search.get('redirect');
  let currentMode = 'athlete';

  if (CommonUI.getToken()) {
    const role = CommonUI.getRole();
    if (redirectTo && redirectTo.startsWith('/')) {
      window.location.href = redirectTo;
    } else {
      window.location.href = role === 'admin' ? '/static/admin.html' : '/static/athlete.html';
    }
    return;
  }

  CommonUI.renderCountdown();

  function updateMode(mode) {
    currentMode = mode;
    modeButtons.forEach((btn) => {
      btn.classList.toggle('btn-primary', btn.dataset.mode === mode);
      btn.classList.toggle('btn-outline', btn.dataset.mode !== mode);
    });
    usernameInput.placeholder = mode === 'athlete' ? '学号' : '管理员账号';
    document.getElementById('modeNote').textContent =
      mode === 'athlete'
        ? '运动员请使用学号登录，初始密码 123456。'
        : '管理员请使用分配的账号密码登录。';
  }

  modeButtons.forEach((btn) => {
    btn.addEventListener('click', () => updateMode(btn.dataset.mode));
  });
  updateMode('athlete');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    CommonUI.clearStatus(messageEl);
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    if (!username || !password) {
      CommonUI.setStatus(messageEl, '请输入完整的账号与密码', 'error');
      return;
    }
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);
    try {
      const response = await fetch(`${CommonUI.API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
      });
      if (!response.ok) {
        throw new Error('账号或密码错误');
      }
      const data = await response.json();
      CommonUI.saveAuth(data.access_token, data.role);
      if (redirectTo && redirectTo.startsWith('/')) {
        window.location.href = redirectTo;
      } else {
        window.location.href = data.role === 'admin' ? '/static/admin.html' : '/static/athlete.html';
      }
    } catch (error) {
      CommonUI.setStatus(messageEl, error.message || '登录失败', 'error');
    }
  });
});
