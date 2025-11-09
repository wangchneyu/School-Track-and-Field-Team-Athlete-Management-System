let athleteProfile = null;
let eventMap = {};
let cachedScores = [];
let scoreChart = null;

async function ensureChartLibrary() {
  if (window.Chart) return;
  await new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function loadEvents() {
  try {
    const events = await CommonUI.publicFetch('/events');
    events.forEach((evt) => {
      eventMap[evt.id] = evt;
    });
  } catch (error) {
    console.warn('加载项目列表失败', error);
  }
}

async function loadAthleteProfile() {
  const container = document.getElementById('profileCard');
  try {
    const athlete = await CommonUI.authFetch('/athletes/me');
    athleteProfile = athlete;
    container.innerHTML = `
      <p><strong>姓名：</strong>${athlete.name}</p>
      <p><strong>学号：</strong>${athlete.student_id}</p>
      <p><strong>训练组：</strong>${athlete.group || '—'}</p>
      <p><strong>主项：</strong>${athlete.main_event || '—'}</p>
      <p><strong>联系电话：</strong>${athlete.phone || '—'}</p>
    `;
  } catch (error) {
    container.innerHTML = `<p class="status-bad">加载个人信息失败：${error.message}</p>`;
  }
}

function renderAttendanceTable(records) {
  const tbody = document.querySelector('#attendanceTable tbody');
  if (!records.length) {
    tbody.innerHTML = '<tr><td colspan="5">暂无考勤记录</td></tr>';
    return;
  }
  tbody.innerHTML = records
    .map(
      (item) => `
      <tr>
        <td>${new Date(item.created_at).toLocaleString()}</td>
        <td>${item.session_id}</td>
        <td>${item.status}</td>
        <td>${item.method || 'manual'}</td>
        <td>${item.remark || '—'}</td>
      </tr>`
    )
    .join('');
}

async function loadAttendanceHistory(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.startDate) params.append('start_date', filters.startDate);
    if (filters.endDate) params.append('end_date', filters.endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    const records = await CommonUI.authFetch(`/attendance/me${query}`);
    renderAttendanceTable(records);
  } catch (error) {
    const tbody = document.querySelector('#attendanceTable tbody');
    tbody.innerHTML = `<tr><td colspan="5">加载失败：${error.message}</td></tr>`;
  }
}

function bindAttendanceFilter() {
  const form = document.getElementById('attendanceFilter');
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const startDate = form.startDate.value || null;
    const endDate = form.endDate.value || null;
    loadAttendanceHistory({ startDate, endDate });
  });
}

function renderList(listId, items, renderItem, emptyText) {
  const listEl = document.getElementById(listId);
  if (!items.length) {
    listEl.innerHTML = `<li>${emptyText}</li>`;
    return;
  }
  listEl.innerHTML = items.map(renderItem).join('');
}

async function loadScoreHistory() {
  try {
    const scores = await CommonUI.authFetch('/scores/me');
    cachedScores = scores;
    renderList(
      'scoreList',
      scores.slice(0, 5),
      (item) => `
        <li>
          <strong>${eventMap[item.event_id]?.name || `项目ID ${item.event_id}`}</strong>
          <br/>成绩：${item.performance}  (${item.is_official ? '正式' : '测试'})
          <br/>时间：${new Date(item.recorded_at).toLocaleString()}
        </li>
      `,
      '暂无成绩记录'
    );
    populateTrendSelect();
    updateScoreChart();
  } catch (error) {
    renderList('scoreList', [], () => '', `加载失败：${error.message}`);
  }
}

function populateTrendSelect() {
  const select = document.getElementById('trendEventSelect');
  if (!select) return;
  const uniqueEventIds = [...new Set(cachedScores.map((item) => item.event_id))];
  if (!uniqueEventIds.length) {
    select.innerHTML = '<option value="">暂无数据</option>';
    return;
  }
  select.innerHTML = uniqueEventIds
    .map((eventId) => {
      const evt = eventMap[eventId];
      return `<option value="${eventId}">${evt ? evt.name : `项目${eventId}`}</option>`;
    })
    .join('');
}

async function updateScoreChart() {
  if (!cachedScores.length) return;
  const select = document.getElementById('trendEventSelect');
  const eventId = Number(select.value || cachedScores[0].event_id);
  const eventInfo = eventMap[eventId];
  const data = cachedScores
    .filter((item) => item.event_id === eventId)
    .sort((a, b) => new Date(a.recorded_at) - new Date(b.recorded_at));
  if (!data.length) {
    if (scoreChart) {
      scoreChart.destroy();
      scoreChart = null;
    }
    return;
  }
  const labels = data.map((item) => new Date(item.recorded_at).toLocaleDateString());
  const values = data.map((item) => item.performance);

  await ensureChartLibrary();
  const ctx = document.getElementById('scoreTrendChart').getContext('2d');
  const dataset = {
    label: eventInfo ? `${eventInfo.name} 成绩` : '成绩走势',
    data: values,
    borderColor: '#1f5eff',
    backgroundColor: 'rgba(31,94,255,0.15)',
    tension: 0.3,
    fill: true,
  };
  const options = {
    scales: {
      y: {
        reverse: eventInfo?.type === 'time',
        title: { display: true, text: '成绩' },
      },
    },
  };
  if (scoreChart) {
    scoreChart.data.labels = labels;
    scoreChart.data.datasets = [dataset];
    scoreChart.options = options;
    scoreChart.update();
  } else {
    scoreChart = new window.Chart(ctx, {
      type: 'line',
      data: { labels, datasets: [dataset] },
      options,
    });
  }
}

function bindTrendSelect() {
  const select = document.getElementById('trendEventSelect');
  if (!select) return;
  select.addEventListener('change', updateScoreChart);
}

function populateRankingSelect() {
  const select = document.getElementById('rankingEventSelect');
  if (!select) return;
  const options = Object.values(eventMap);
  select.innerHTML = options
    .map((evt) => `<option value="${evt.id}">${evt.name}</option>`)
    .join('');
}

async function refreshRanking() {
  const select = document.getElementById('rankingEventSelect');
  const listEl = document.getElementById('rankingList');
  if (!select || !select.value) {
    listEl.innerHTML = '<li>请选择项目</li>';
    return;
  }
  try {
    const rankings = await CommonUI.authFetch(`/rankings/${select.value}`);
    if (!rankings.length) {
      listEl.innerHTML = '<li>暂无排行榜数据</li>';
      return;
    }
    listEl.innerHTML = rankings
      .map((row) => {
        const isMe = row.athlete_id === athleteProfile?.id;
        return `
          <li style="${isMe ? 'background:#dbeafe;border-radius:8px;padding:0.4rem;' : ''}">
            第 ${row.rank} 名 - ${row.name} (${row.group || '—'}) | 成绩：${row.best_performance}
          </li>
        `;
      })
      .join('');
  } catch (error) {
    listEl.innerHTML = `<li>加载失败：${error.message}</li>`;
  }
}

function bindRankingSelect() {
  const select = document.getElementById('rankingEventSelect');
  if (!select) return;
  select.addEventListener('change', refreshRanking);
}

async function loadRatingHistory() {
  try {
    const ratings = await CommonUI.authFetch('/ratings/me');
    renderList(
      'ratingList',
      ratings.slice(0, 5),
      (item) => `
        <li>
          <strong>${item.date}</strong> - 态度 ${item.attitude} / 出勤 ${item.attendance} / 表现 ${item.performance}
          <br/>教练评语：${item.comment || '—'}
        </li>
      `,
      '暂无评分记录'
    );
  } catch (error) {
    renderList('ratingList', [], () => '', `加载失败：${error.message}`);
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

document.addEventListener('DOMContentLoaded', async () => {
  if (!CommonUI.ensureRole('athlete')) return;
  document.getElementById('logoutBtn').addEventListener('click', CommonUI.logout);
  CommonUI.renderCountdown();
  bindPasswordForm();
  bindAttendanceFilter();
  bindTrendSelect();
  bindRankingSelect();
  await loadEvents();
  await loadAthleteProfile();
  await loadAttendanceHistory();
  await loadScoreHistory();
  populateRankingSelect();
  await refreshRanking();
  await loadRatingHistory();
});
