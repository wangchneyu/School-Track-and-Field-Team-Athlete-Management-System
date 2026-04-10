<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">训练管理</h2><p class="section-desc">安排和管理训练课程</p></div>
      <button class="btn-primary text-sm" @click="openAdd">+ 新建训练</button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="s in sessions" :key="s.id" class="card-base p-5 hover:shadow-card-hover">
        <div class="flex items-start justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
            <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          </div>
          <div class="flex gap-1">
            <button class="btn-ghost text-xs px-2 py-1" @click="openEdit(s)">编辑</button>
            <button class="btn-ghost text-xs px-2 py-1 text-destructive" @click="handleDelete(s)">删除</button>
          </div>
        </div>
        <p class="font-semibold text-foreground">{{ s.date }}</p>
        <p class="text-sm text-muted-foreground mt-1">{{ s.start_time }} - {{ s.end_time }}</p>
        <p v-if="s.location" class="text-sm text-muted-foreground mt-1">📍 {{ s.location }}</p>
        <p v-if="s.description" class="text-xs text-muted-foreground mt-2 line-clamp-2">{{ s.description }}</p>
        <button class="btn-ghost text-xs mt-3 text-accent" @click="generateQR(s)">生成签到二维码</button>
      </div>
      <div v-if="!sessions.length" class="col-span-full text-center py-12 text-muted-foreground">暂无训练安排</div>
    </div>

    <!-- Add/Edit Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <h3 class="text-lg font-bold text-foreground mb-4">{{ editingId ? '编辑训练' : '新建训练' }}</h3>
          <form @submit.prevent="handleSave" class="space-y-3">
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">日期 *</label><input v-model="form.date" type="date" class="input-base" required /></div>
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">开始时间</label><input v-model="form.start_time" type="time" class="input-base" /></div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">结束时间</label><input v-model="form.end_time" type="time" class="input-base" /></div>
            </div>
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">地点</label><input v-model="form.location" class="input-base" /></div>
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">描述</label><textarea v-model="form.description" class="input-base" rows="2" /></div>
            <div class="flex gap-2 pt-2 justify-end">
              <button type="button" class="btn-secondary text-sm" @click="showModal = false">取消</button>
              <button type="submit" class="btn-primary text-sm" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- QR Code Modal -->
    <Teleport to="body">
      <div v-if="showQRModal" class="modal-overlay" @click.self="showQRModal = false">
        <div class="modal-content qr-modal">
          <div class="qr-modal-header">
            <h3 class="qr-modal-title">签到二维码</h3>
            <button class="qr-close-btn" @click="showQRModal = false">
              <svg class="qr-close-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <div class="qr-session-info">
            <div class="qr-session-date">{{ qrSessionInfo.date }}</div>
            <div class="qr-session-time">{{ qrSessionInfo.time }}</div>
            <div v-if="qrSessionInfo.location" class="qr-session-location">{{ qrSessionInfo.location }}</div>
          </div>

          <div class="qr-code-container">
            <div v-if="qrLoading" class="qr-loading">
              <div class="qr-spinner" />
              <span>生成中...</span>
            </div>
            <canvas v-show="!qrLoading" ref="qrCanvas" class="qr-canvas" />
          </div>

          <div v-if="qrUrl" class="qr-url-section">
            <p class="qr-url-label">签到链接</p>
            <div class="qr-url-row">
              <input class="qr-url-input" :value="qrUrl" readonly @click="($event.target as HTMLInputElement)?.select()" />
              <button class="qr-copy-btn" @click="copyUrl">
                <svg class="qr-copy-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
              </button>
            </div>
          </div>

          <!-- Real-time attendance stats -->
          <div v-if="qrSessionStat" class="qr-attendance-section">
            <div class="qr-attendance-header">
              <span class="qr-attendance-title">实时签到统计</span>
              <button class="qr-refresh-btn" :disabled="statLoading" @click="refreshSessionStat">
                <svg class="qr-refresh-icon" :class="{ spinning: statLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              </button>
            </div>
            <div class="qr-stat-grid">
              <div class="qr-stat-item">
                <span class="qr-stat-num text-accent">{{ qrSessionStat.present_count }}</span>
                <span class="qr-stat-label">已签到</span>
              </div>
              <div class="qr-stat-item">
                <span class="qr-stat-num text-warning">{{ qrSessionStat.late_count }}</span>
                <span class="qr-stat-label">迟到</span>
              </div>
              <div class="qr-stat-item">
                <span class="qr-stat-num text-muted">{{ qrSessionStat.unchecked_count }}</span>
                <span class="qr-stat-label">未签到</span>
              </div>
              <div class="qr-stat-item">
                <span class="qr-stat-num">{{ Math.round(qrSessionStat.attendance_rate * 100) }}%</span>
                <span class="qr-stat-label">出勤率</span>
              </div>
            </div>
            <div class="qr-progress-bar">
              <div class="qr-progress-fill" :style="{ width: Math.round(qrSessionStat.attendance_rate * 100) + '%' }" />
            </div>
            <div class="qr-athlete-list">
              <div v-for="a in qrSessionStat.athletes" :key="a.athlete_id" class="qr-athlete-row">
                <span class="qr-athlete-name">{{ a.name }}</span>
                <span class="qr-athlete-group">{{ a.group }}</span>
                <span :class="checkinStatusBadge(a.status)">{{ checkinStatusText(a.status) }}</span>
                <span v-if="a.checkin_time" class="qr-athlete-time">{{ formatTime(a.checkin_time) }}</span>
              </div>
            </div>
          </div>

          <div class="qr-footer-hint">运动员扫描此二维码即可完成签到</div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, reactive, nextTick } from 'vue'
import QRCode from 'qrcode'
import { sessionApi, statsApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { TrainingSession, SessionAttendanceStat } from '@/types'

const appStore = useAppStore()
const sessions = ref<TrainingSession[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ date: '', start_time: '', end_time: '', location: '', description: '' })

// QR modal state
const showQRModal = ref(false)
const qrLoading = ref(false)
const qrUrl = ref('')
const qrCanvas = ref<HTMLCanvasElement | null>(null)
const qrSessionInfo = reactive({ date: '', time: '', location: '', sessionId: 0 })

// Attendance stats state
const qrSessionStat = ref<SessionAttendanceStat | null>(null)
const statLoading = ref(false)
let statPollingTimer: ReturnType<typeof setInterval> | null = null

async function loadSessions() {
  try { const res = await sessionApi.list(); sessions.value = Array.isArray(res.data) ? res.data : [] } catch { sessions.value = [] }
}

function openAdd() {
  editingId.value = null
  Object.assign(form, { date: '', start_time: '', end_time: '', location: '', description: '' })
  showModal.value = true
}

function openEdit(s: TrainingSession) {
  editingId.value = s.id
  Object.assign(form, { date: s.date, start_time: s.start_time, end_time: s.end_time, location: s.location, description: s.description })
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editingId.value) { await sessionApi.update(editingId.value, { ...form }); appStore.showToast('已更新', 'success') }
    else { await sessionApi.create({ ...form }); appStore.showToast('已创建', 'success') }
    showModal.value = false; await loadSessions()
  } catch { appStore.showToast('操作失败', 'error') } finally { saving.value = false }
}

async function handleDelete(s: TrainingSession) {
  if (!confirm('确认删除此训练？')) return
  try { await sessionApi.delete(s.id); appStore.showToast('已删除', 'success'); await loadSessions() } catch { appStore.showToast('删除失败', 'error') }
}

async function refreshSessionStat() {
  if (!qrSessionInfo.sessionId) return
  statLoading.value = true
  try {
    const res = await statsApi.sessionAttendance(qrSessionInfo.sessionId)
    qrSessionStat.value = res.data
  } catch { /* ignore */ }
  finally { statLoading.value = false }
}

function startStatPolling() {
  stopStatPolling()
  refreshSessionStat()
  statPollingTimer = setInterval(refreshSessionStat, 10000)
}

function stopStatPolling() {
  if (statPollingTimer) {
    clearInterval(statPollingTimer)
    statPollingTimer = null
  }
}

async function generateQR(s: TrainingSession) {
  // Set session info
  qrSessionInfo.date = s.date
  qrSessionInfo.time = `${s.start_time || ''} - ${s.end_time || ''}`
  qrSessionInfo.location = s.location || ''
  qrSessionInfo.sessionId = s.id
  qrUrl.value = ''
  qrLoading.value = true
  qrSessionStat.value = null
  showQRModal.value = true

  try {
    const res = await sessionApi.generateQR(s.id, {})
    const data = res.data
    const url = data.qr_url || `${window.location.origin}/checkin?token=${data.token}`
    qrUrl.value = url

    await nextTick()
    if (qrCanvas.value) {
      await QRCode.toCanvas(qrCanvas.value, url, {
        width: 240,
        margin: 2,
        color: {
          dark: '#1a1a2e',
          light: '#ffffff',
        },
      })
    }

    // Start polling attendance stats
    startStatPolling()
  } catch {
    appStore.showToast('二维码生成失败', 'error')
    showQRModal.value = false
  } finally {
    qrLoading.value = false
  }
}

function copyUrl() {
  if (qrUrl.value) {
    navigator.clipboard.writeText(qrUrl.value).then(() => {
      appStore.showToast('链接已复制', 'success')
    }).catch(() => {
      appStore.showToast('复制失败', 'error')
    })
  }
}

function checkinStatusBadge(s: string) {
  return {
    present: 'badge-success',
    late: 'badge-warning',
    absent: 'badge-destructive',
    leave: 'badge-primary',
    unchecked: 'badge-muted',
  }[s] || 'badge-muted'
}

function checkinStatusText(s: string) {
  return {
    present: '已签到',
    late: '迟到',
    absent: '缺勤',
    leave: '请假',
    unchecked: '未签到',
  }[s] || s
}

function formatTime(dt: string) {
  try {
    const d = new Date(dt)
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

onMounted(loadSessions)

onBeforeUnmount(() => {
  stopStatPolling()
})
</script>

<style scoped>
/* QR Modal */
.qr-modal {
  max-width: 420px;
  text-align: center;
  max-height: 90vh;
  overflow-y: auto;
}
.qr-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.qr-modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: hsl(var(--foreground));
}
.qr-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  border-radius: var(--radius-md);
  background: none;
  border: none;
  color: hsl(var(--muted-foreground));
  cursor: pointer;
  transition: all 0.15s ease;
}
.qr-close-btn:hover {
  background: hsl(var(--muted) / 0.5);
  color: hsl(var(--foreground));
}
.qr-close-icon {
  width: 20px;
  height: 20px;
}

.qr-session-info {
  padding: 0.75rem;
  border-radius: var(--radius-md);
  background: hsl(var(--accent) / 0.06);
  border: 1px solid hsl(var(--accent) / 0.12);
  margin-bottom: 1.25rem;
}
.qr-session-date {
  font-size: 0.9375rem;
  font-weight: 700;
  color: hsl(var(--foreground));
}
.qr-session-time {
  font-size: 0.8125rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.125rem;
}
.qr-session-location {
  font-size: 0.75rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.25rem;
}

.qr-code-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 260px;
  margin-bottom: 1rem;
}
.qr-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: hsl(var(--muted-foreground));
  font-size: 0.8125rem;
}
.qr-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid hsl(var(--border));
  border-top-color: hsl(var(--accent));
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.qr-canvas {
  border-radius: var(--radius-md);
  box-shadow: 0 2px 12px hsl(var(--foreground) / 0.08);
}

.qr-url-section {
  text-align: left;
  margin-bottom: 1rem;
}
.qr-url-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: hsl(var(--muted-foreground));
  margin-bottom: 0.375rem;
}
.qr-url-row {
  display: flex;
  gap: 0.375rem;
}
.qr-url-input {
  flex: 1;
  padding: 0.5rem 0.625rem;
  font-size: 0.6875rem;
  border-radius: var(--radius-sm);
  border: 1px solid hsl(var(--border));
  background: hsl(var(--muted) / 0.3);
  color: hsl(var(--foreground));
  cursor: text;
  min-width: 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
}
.qr-url-input:focus {
  outline: none;
  border-color: hsl(var(--accent));
}
.qr-copy-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  border: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  color: hsl(var(--muted-foreground));
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}
.qr-copy-btn:hover {
  background: hsl(var(--accent) / 0.1);
  color: hsl(var(--accent));
  border-color: hsl(var(--accent) / 0.3);
}
.qr-copy-icon {
  width: 16px;
  height: 16px;
}

/* Attendance Stats Section */
.qr-attendance-section {
  text-align: left;
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  background: hsl(var(--muted) / 0.15);
  border: 1px solid hsl(var(--border));
}
.qr-attendance-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.625rem;
}
.qr-attendance-title {
  font-size: 0.8125rem;
  font-weight: 700;
  color: hsl(var(--foreground));
}
.qr-refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border-radius: var(--radius-sm);
  border: none;
  background: none;
  color: hsl(var(--muted-foreground));
  cursor: pointer;
  transition: all 0.15s ease;
}
.qr-refresh-btn:hover {
  color: hsl(var(--accent));
}
.qr-refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.qr-refresh-icon {
  width: 16px;
  height: 16px;
}
.qr-refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

.qr-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.625rem;
}
.qr-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.375rem 0;
}
.qr-stat-num {
  font-size: 1.125rem;
  font-weight: 700;
  color: hsl(var(--foreground));
  line-height: 1.2;
}
.qr-stat-num.text-accent { color: hsl(var(--accent)); }
.qr-stat-num.text-warning { color: hsl(38 92% 50%); }
.qr-stat-num.text-muted { color: hsl(var(--muted-foreground)); }
.qr-stat-label {
  font-size: 0.625rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.125rem;
}

.qr-progress-bar {
  height: 4px;
  border-radius: 2px;
  background: hsl(var(--muted) / 0.5);
  margin-bottom: 0.75rem;
  overflow: hidden;
}
.qr-progress-fill {
  height: 100%;
  border-radius: 2px;
  background: hsl(var(--accent));
  transition: width 0.5s ease;
}

.qr-athlete-list {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.qr-athlete-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  border-radius: var(--radius-sm);
  background: hsl(var(--card));
  font-size: 0.75rem;
}
.qr-athlete-name {
  font-weight: 600;
  color: hsl(var(--foreground));
  min-width: 56px;
}
.qr-athlete-group {
  color: hsl(var(--muted-foreground));
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.qr-athlete-time {
  color: hsl(var(--muted-foreground));
  font-size: 0.6875rem;
  flex-shrink: 0;
}

/* Badge styles for attendance status */
.badge-muted {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  border-radius: 99px;
  font-size: 0.6875rem;
  font-weight: 600;
  background: hsl(var(--muted) / 0.5);
  color: hsl(var(--muted-foreground));
  flex-shrink: 0;
}

.qr-footer-hint {
  font-size: 0.6875rem;
  color: hsl(var(--muted-foreground));
  padding-top: 0.5rem;
  border-top: 1px solid hsl(var(--border));
}
</style>
