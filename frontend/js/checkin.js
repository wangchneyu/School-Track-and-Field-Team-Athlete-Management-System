document.addEventListener('DOMContentLoaded', () => {
  const infoEl = document.getElementById('qrInfo');
  const messageEl = document.getElementById('checkinMessage');
  const btn = document.getElementById('checkinBtn');
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');

  if (!token) {
    infoEl.textContent = '缺少签到令牌，请通过二维码访问。';
    btn.disabled = true;
    return;
  }

  async function loadInfo() {
    try {
      const data = await CommonUI.publicFetch(`/attendance/qr-checkin/${token}`);
      if (!data) {
        throw new Error('二维码已失效');
      }
      infoEl.innerHTML = `
        <p><strong>签到地点：</strong>${data.session_location || '未设置'}</p>
        <p><strong>签到时间：</strong>${data.session_start || '未设置'}</p>
        <p><strong>有效期至：</strong>${new Date(data.expires_at).toLocaleString()}</p>
        <p><strong>备注：</strong>${data.note || '—'}</p>
      `;
    } catch (error) {
      infoEl.textContent = error.message || '无法加载签到信息';
      btn.disabled = true;
    }
  }

  async function submitCheckin() {
    CommonUI.clearStatus(messageEl);
    const auth = CommonUI.ensureRole('athlete');
    if (!auth) {
      return;
    }
    btn.disabled = true;
    try {
      const attendance = await CommonUI.authFetch('/attendance/qr-checkin', {
        method: 'POST',
        body: { token, device_info: navigator.userAgent },
      });
      CommonUI.setStatus(
        messageEl,
        `签到成功：${new Date(attendance.created_at).toLocaleString()}`,
        'info',
      );
    } catch (error) {
      btn.disabled = false;
      CommonUI.setStatus(messageEl, error.message || '签到失败', 'error');
    }
  }

  btn.addEventListener('click', submitCheckin);
  loadInfo();
});
