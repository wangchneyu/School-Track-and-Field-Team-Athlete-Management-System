function toLocalInputValue(isoString) {
  if (!isoString) return '';
  const date = new Date(isoString);
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60000);
  return local.toISOString().slice(0, 16);
}

async function populateFeaturedEventForm() {
  const form = document.getElementById('eventForm');
  const message = document.getElementById('eventMessage');
  try {
    const event = await CommonUI.fetchFeaturedEvent();
    if (!event) {
      form.reset();
      return;
    }
    form.name.value = event.name || '';
    form.start_time.value = toLocalInputValue(event.start_time);
    form.location.value = event.location || '';
    form.description.value = event.description || '';
  } catch (error) {
    CommonUI.setStatus(message, error.message, 'error');
  }
}

function bindEventForm() {
  const form = document.getElementById('eventForm');
  const message = document.getElementById('eventMessage');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    CommonUI.clearStatus(message);
    const payload = {
      name: form.name.value.trim(),
      start_time: new Date(form.start_time.value).toISOString(),
      location: form.location.value.trim(),
      description: form.description.value.trim(),
    };
    if (!payload.name || !form.start_time.value) {
      CommonUI.setStatus(message, '请填写完整信息', 'error');
      return;
    }
    try {
      await CommonUI.authFetch('/featured-event', {
        method: 'PUT',
        body: payload,
      });
      CommonUI.setStatus(message, '赛事信息已更新', 'info');
      CommonUI.renderCountdown();
    } catch (error) {
      CommonUI.setStatus(message, error.message || '更新失败', 'error');
    }
  });
}

async function loadAttendanceStats() {
  const tbody = document.querySelector('#attendanceTable tbody');
  try {
    const stats = await CommonUI.authFetch('/stats/attendance');
    if (!stats.length) {
      tbody.innerHTML = '<tr><td colspan="5">暂无数据</td></tr>';
      return;
    }
    tbody.innerHTML = stats
      .map(
        (row) => `
        <tr>
          <td>${row.name}</td>
          <td>${row.group || '—'}</td>
          <td>${row.recorded_sessions}</td>
          <td>${row.attended_sessions}</td>
          <td>
            <div class="progress-bar"><span style="width:${row.attendance_rate * 100}%"></span></div>
            ${(row.attendance_rate * 100).toFixed(0)}%
          </td>
        </tr>`
      )
      .join('');
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="5">加载失败：${error.message}</td></tr>`;
  }
}

async function loadEventStats() {
  const container = document.getElementById('eventDistribution');
  try {
    const stats = await CommonUI.authFetch('/stats/events');
    if (!stats.length) {
      container.innerHTML = '<p>暂无数据</p>';
      return;
    }
    container.innerHTML = stats
      .map(
        (row) => `
        <div class="stat-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <strong>${row.event}</strong>
            <span>${row.athletes} 人</span>
          </div>
          <div class="progress-bar" style="margin-top:0.5rem">
            <span style="width:${row.percentage * 100}%"></span>
          </div>
        </div>`
      )
      .join('');
  } catch (error) {
    container.innerHTML = `<p class="status-bad">加载失败：${error.message}</p>`;
  }
}

function bindPasswordForm() {
  const form = document.getElementById('passwordForm');
  const message = document.getElementById('passwordMessage');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const oldPassword = form.oldPassword.value.trim();
    const newPassword = form.newPassword.value.trim();
    if (!oldPassword || !newPassword) {
      CommonUI.setStatus(message, '请输入完整信息', 'error');
      return;
    }
    try {
      await CommonUI.authFetch('/auth/change-password', {
        method: 'POST',
        body: { old_password: oldPassword, new_password: newPassword },
      });
      CommonUI.setStatus(message, '密码更新成功', 'info');
      form.reset();
    } catch (error) {
      CommonUI.setStatus(message, error.message || '更新失败', 'error');
    }
  });
}

async function loadSessionsForQr() {
  const select = document.getElementById('qrSessionSelect');
  if (!select) return;
  select.innerHTML = '<option value="">加载中...</option>';
  try {
    const sessions = await CommonUI.authFetch('/sessions');
    if (!sessions.length) {
      select.innerHTML = '<option value="">暂无场次</option>';
      return;
    }
    select.innerHTML = sessions
      .map(
        (session) =>
          `<option value="${session.id}">${session.date} ${session.start_time || ''} ${session.location || ''}</option>`
      )
      .join('');
  } catch (error) {
    select.innerHTML = `<option value="">加载失败：${error.message}</option>`;
  }
}

async function ensureQrLibrary() {
  if (window.QRCode) return;
  await new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = '/static/js/lib/qrcode.min.js';
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function renderQrPreview(data) {
  const preview = document.getElementById('qrPreview');
  const message = document.getElementById('qrMessage');
  if (!preview) return;
  preview.innerHTML = '';
  const info = document.createElement('div');
  info.innerHTML = `
    <p><strong>签到地点：</strong>${data.session_location || '未设置'}</p>
    <p><strong>签到时间：</strong>${data.session_start || '未设置'}</p>
    <p><strong>有效期至：</strong>${new Date(data.expires_at).toLocaleString()}</p>
    <p><strong>备注：</strong>${data.note || '—'}</p>
  `;
  const qrBox = document.createElement('div');
  qrBox.id = 'qrCanvas';
  preview.appendChild(info);
  preview.appendChild(qrBox);
  await ensureQrLibrary();
  const ctor = window.QRCode && (window.QRCode.QRCode || window.QRCode);
  if (typeof ctor !== 'function') {
    CommonUI.setStatus(message, '二维码库加载失败', 'error');
    return;
  }
  new ctor(qrBox, {
    text: data.qr_url,
    width: 200,
    height: 200,
  });
}

function bindQrForm() {
  const form = document.getElementById('qrForm');
  const message = document.getElementById('qrMessage');
  if (!form) return;
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    CommonUI.clearStatus(message);
    const sessionId = form.querySelector('#qrSessionSelect').value;
    const expire = Number(form.expire.value) || 15;
    const limit = Number(form.limit.value) || 0;
    const note = form.note.value.trim();
    if (!sessionId) {
      CommonUI.setStatus(message, '请选择训练场次', 'error');
      return;
    }
    try {
      const data = await CommonUI.authFetch(`/sessions/${sessionId}/qr`, {
        method: 'POST',
        body: { expire_minutes: expire, note, use_limit: limit },
      });
      CommonUI.setStatus(message, '二维码已生成', 'info');
      await renderQrPreview(data);
    } catch (error) {
      CommonUI.setStatus(message, error.message || '生成失败', 'error');
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  if (!CommonUI.ensureRole('admin')) return;
  document.getElementById('logoutBtn').addEventListener('click', CommonUI.logout);
  CommonUI.renderCountdown();
  populateFeaturedEventForm();
  bindEventForm();
  loadAttendanceStats();
  loadEventStats();
  bindPasswordForm();
  loadSessionsForQr();
  bindQrForm();
});
