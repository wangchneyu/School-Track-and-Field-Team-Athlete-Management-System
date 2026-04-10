<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">考勤管理</h2><p class="section-desc">记录和查看训练出勤</p></div>
      <button class="btn-primary text-sm" @click="openAdd">+ 记录考勤</button>
    </div>

    <!-- Daily Attendance Summary Panel -->
    <div class="daily-panel card-base mb-4 p-4">
      <div class="daily-header">
        <div class="daily-title-row">
          <h3 class="daily-title">当日考勤统计</h3>
          <button class="daily-refresh-btn" :disabled="dailyLoading" @click="loadDailyStats">
            <svg class="daily-refresh-icon" :class="{ spinning: dailyLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          </button>
        </div>
        <div class="daily-date-picker">
          <input type="date" v-model="dailyDate" class="input-base text-sm max-w-[160px]" @change="loadDailyStats" />
        </div>
      </div>

      <div v-if="dailySummary" class="daily-content">
        <!-- Overall stats -->
        <div class="daily-stat-cards">
          <div class="daily-stat-card">
            <span class="daily-stat-val text-foreground">{{ dailySummary.total_sessions }}</span>
            <span class="daily-stat-lbl">训练课次</span>
          </div>
          <div class="daily-stat-card">
            <span class="daily-stat-val stat-present">{{ dailySummary.present_count }}</span>
            <span class="daily-stat-lbl">出勤</span>
          </div>
          <div class="daily-stat-card">
            <span class="daily-stat-val stat-late">{{ dailySummary.late_count }}</span>
            <span class="daily-stat-lbl">迟到</span>
          </div>
          <div class="daily-stat-card">
            <span class="daily-stat-val stat-absent">{{ dailySummary.absent_count }}</span>
            <span class="daily-stat-lbl">缺勤</span>
          </div>
          <div class="daily-stat-card">
            <span class="daily-stat-val stat-leave">{{ dailySummary.leave_count }}</span>
            <span class="daily-stat-lbl">请假</span>
          </div>
          <div class="daily-stat-card">
            <span class="daily-stat-val stat-unchecked">{{ dailySummary.unchecked_count }}</span>
            <span class="daily-stat-lbl">未签到</span>
          </div>
          <div class="daily-stat-card">
            <span class="daily-stat-val stat-rate">{{ Math.round(dailySummary.attendance_rate * 100) }}%</span>
            <span class="daily-stat-lbl">出勤率</span>
          </div>
        </div>

        <!-- Per-session breakdown -->
        <div v-for="sess in dailySummary.sessions" :key="sess.session_id" class="daily-session-block">
          <div class="daily-session-header" @click="toggleSession(sess.session_id)">
            <div class="daily-session-info">
              <span class="daily-session-time">{{ sess.start_time }} - {{ sess.end_time }}</span>
              <span v-if="sess.location" class="daily-session-loc">{{ sess.location }}</span>
            </div>
            <div class="daily-session-stats">
              <span class="badge-success text-xs">{{ sess.present_count }}</span>
              <span class="badge-warning text-xs">{{ sess.late_count }}</span>
              <span class="daily-session-rate">{{ Math.round(sess.attendance_rate * 100) }}%</span>
              <svg class="daily-expand-icon" :class="{ expanded: expandedSessions.has(sess.session_id) }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
          </div>
          <div v-if="expandedSessions.has(sess.session_id)" class="daily-session-athletes">
            <div class="daily-progress-bar">
              <div class="daily-progress-fill" :style="{ width: Math.round(sess.attendance_rate * 100) + '%' }" />
            </div>
            <div v-for="a in sess.athletes" :key="a.athlete_id" class="daily-athlete-row">
              <span class="daily-athlete-name">{{ a.name }}</span>
              <span class="daily-athlete-sid">{{ a.student_id }}</span>
              <span class="daily-athlete-grp">{{ a.group }}</span>
              <span :class="dailyStatusBadge(a.status)">{{ dailyStatusText(a.status) }}</span>
              <span class="daily-athlete-method">{{ a.method === 'qr' ? '扫码' : a.method === 'manual' ? '手动' : '—' }}</span>
              <span class="daily-athlete-time">{{ a.checkin_time ? formatTime(a.checkin_time) : '—' }}</span>
            </div>
            <div v-if="!sess.athletes.length" class="text-center text-muted-foreground text-xs py-3">暂无运动员数据</div>
          </div>
        </div>

        <div v-if="!dailySummary.sessions.length" class="text-center text-muted-foreground text-sm py-6">当日暂无训练安排</div>
      </div>

      <div v-else-if="dailyLoading" class="text-center text-muted-foreground text-sm py-6">加载中...</div>
      <div v-else class="text-center text-muted-foreground text-sm py-6">选择日期查看考勤统计</div>
    </div>

    <!-- Existing filter and table -->
    <div class="flex flex-wrap gap-3 mb-4">
      <select v-model="filterSession" class="input-base max-w-[200px]">
        <option value="">全部课次</option>
        <option v-for="s in sessions" :key="s.id" :value="String(s.id)">{{ s.date }} {{ s.start_time }}</option>
      </select>
    </div>

    <div class="card-base overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead><tr><th>运动员</th><th>训练日期</th><th>状态</th><th class="hidden sm:table-cell">方式</th><th class="hidden md:table-cell">备注</th><th class="text-right">操作</th></tr></thead>
          <tbody>
            <tr v-for="a in records" :key="a.id">
              <td class="font-medium">{{ a.athlete_name || a.athlete_id }}</td>
              <td class="text-muted-foreground">{{ a.session_date || a.session_id }}</td>
              <td>
                <span :class="statusBadge(a.status)">{{ statusText(a.status) }}</span>
              </td>
              <td class="hidden sm:table-cell text-muted-foreground">{{ a.method === 'qr' ? '扫码' : '手动' }}</td>
              <td class="hidden md:table-cell text-muted-foreground">{{ a.remark || '—' }}</td>
              <td class="text-right">
                <button class="btn-ghost text-xs px-2 py-1" @click="openEdit(a)">编辑</button>
                <button class="btn-ghost text-xs px-2 py-1 text-destructive" @click="handleDelete(a)">删除</button>
              </td>
            </tr>
            <tr v-if="!records.length"><td colspan="6" class="text-center text-muted-foreground py-8">暂无考勤记录</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <h3 class="text-lg font-bold text-foreground mb-4">{{ editingId ? '编辑考勤' : '记录考勤' }}</h3>
          <form @submit.prevent="handleSave" class="space-y-3">
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">训练课次 *</label>
              <select v-model="form.session_id" class="input-base" required>
                <option value="">请选择</option>
                <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} {{ s.start_time }}</option>
              </select>
            </div>
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">运动员 *</label>
              <select v-model="form.athlete_id" class="input-base" required>
                <option value="">请选择</option>
                <option v-for="a in athletes" :key="a.id" :value="a.id">{{ a.name }} ({{ a.student_id }})</option>
              </select>
            </div>
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">状态</label>
              <select v-model="form.status" class="input-base">
                <option value="present">出勤</option>
                <option value="late">迟到</option>
                <option value="absent">缺勤</option>
                <option value="leave">请假</option>
              </select>
            </div>
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">备注</label><input v-model="form.remark" class="input-base" /></div>
            <div class="flex gap-2 pt-2 justify-end">
              <button type="button" class="btn-secondary text-sm" @click="showModal = false">取消</button>
              <button type="submit" class="btn-primary text-sm" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import { attendanceApi, sessionApi, athleteApi, statsApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Attendance, TrainingSession, Athlete, DailyAttendanceSummary } from '@/types'

const appStore = useAppStore()
const records = ref<Attendance[]>([])
const sessions = ref<TrainingSession[]>([])
const athletes = ref<Athlete[]>([])
const filterSession = ref('')
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ session_id: '' as string | number, athlete_id: '' as string | number, status: 'present', remark: '' })

// Daily stats
const dailyDate = ref(new Date().toISOString().split('T')[0])
const dailySummary = ref<DailyAttendanceSummary | null>(null)
const dailyLoading = ref(false)
const expandedSessions = ref<Set<number>>(new Set())

function statusBadge(s: string) {
  return { present: 'badge-success', late: 'badge-warning', absent: 'badge-destructive', leave: 'badge-primary' }[s] || 'badge-primary'
}
function statusText(s: string) {
  return { present: '出勤', late: '迟到', absent: '缺勤', leave: '请假' }[s] || s
}

function dailyStatusBadge(s: string) {
  return {
    present: 'badge-success',
    late: 'badge-warning',
    absent: 'badge-destructive',
    leave: 'badge-primary',
    unchecked: 'daily-badge-muted',
  }[s] || 'daily-badge-muted'
}
function dailyStatusText(s: string) {
  return {
    present: '出勤',
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

function toggleSession(sessionId: number) {
  const s = new Set(expandedSessions.value)
  if (s.has(sessionId)) s.delete(sessionId)
  else s.add(sessionId)
  expandedSessions.value = s
}

async function loadDailyStats() {
  dailyLoading.value = true
  try {
    const res = await statsApi.dailyAttendance(dailyDate.value)
    dailySummary.value = res.data
    // Auto-expand all sessions
    const ids = new Set<number>()
    for (const sess of res.data.sessions || []) {
      ids.add(sess.session_id)
    }
    expandedSessions.value = ids
  } catch {
    dailySummary.value = null
  } finally {
    dailyLoading.value = false
  }
}

async function loadRecords() {
  try {
    const params: Record<string, string> = {}
    if (filterSession.value) params.session_id = filterSession.value
    const res = await attendanceApi.list(params)
    records.value = Array.isArray(res.data) ? res.data : []
  } catch { records.value = [] }
}

async function loadMeta() {
  const [sRes, aRes] = await Promise.allSettled([sessionApi.list(), athleteApi.list()])
  if (sRes.status === 'fulfilled') sessions.value = sRes.value.data || []
  if (aRes.status === 'fulfilled') athletes.value = aRes.value.data || []
}

function openAdd() {
  editingId.value = null
  Object.assign(form, { session_id: '', athlete_id: '', status: 'present', remark: '' })
  showModal.value = true
}

function openEdit(a: Attendance) {
  editingId.value = a.id
  Object.assign(form, { session_id: a.session_id, athlete_id: a.athlete_id, status: a.status, remark: a.remark })
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const data = { session_id: Number(form.session_id), athlete_id: Number(form.athlete_id), status: form.status, remark: form.remark }
    if (editingId.value) { await attendanceApi.update(editingId.value, data); appStore.showToast('已更新', 'success') }
    else { await attendanceApi.create(data); appStore.showToast('已记录', 'success') }
    showModal.value = false; await loadRecords(); await loadDailyStats()
  } catch { appStore.showToast('操作失败', 'error') } finally { saving.value = false }
}

async function handleDelete(a: Attendance) {
  if (!confirm('确认删除？')) return
  try { await attendanceApi.delete(a.id); appStore.showToast('已删除', 'success'); await loadRecords(); await loadDailyStats() } catch { appStore.showToast('删除失败', 'error') }
}

watch(filterSession, loadRecords)
onMounted(() => { loadMeta(); loadRecords(); loadDailyStats() })
</script>

<style scoped>
/* Daily Attendance Panel */
.daily-panel {
  border: 1px solid hsl(var(--border));
}
.daily-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.daily-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.daily-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: hsl(var(--foreground));
}
.daily-refresh-btn {
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
.daily-refresh-btn:hover { color: hsl(var(--accent)); }
.daily-refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.daily-refresh-icon {
  width: 16px;
  height: 16px;
}
.daily-refresh-icon.spinning {
  animation: daily-spin 0.8s linear infinite;
}
@keyframes daily-spin {
  to { transform: rotate(360deg); }
}

.daily-stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.daily-stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.625rem 0.375rem;
  border-radius: var(--radius-md);
  background: hsl(var(--muted) / 0.15);
  border: 1px solid hsl(var(--border));
}
.daily-stat-val {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.2;
}
.daily-stat-lbl {
  font-size: 0.6875rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.125rem;
}
.stat-present { color: hsl(var(--accent)); }
.stat-late { color: hsl(38 92% 50%); }
.stat-absent { color: hsl(var(--destructive)); }
.stat-leave { color: hsl(var(--primary)); }
.stat-unchecked { color: hsl(var(--muted-foreground)); }
.stat-rate { color: hsl(var(--accent)); }

/* Session blocks */
.daily-session-block {
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius-md);
  margin-bottom: 0.5rem;
  overflow: hidden;
}
.daily-session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  background: hsl(var(--muted) / 0.1);
  cursor: pointer;
  transition: background 0.15s ease;
}
.daily-session-header:hover {
  background: hsl(var(--muted) / 0.25);
}
.daily-session-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.daily-session-time {
  font-size: 0.8125rem;
  font-weight: 600;
  color: hsl(var(--foreground));
}
.daily-session-loc {
  font-size: 0.75rem;
  color: hsl(var(--muted-foreground));
}
.daily-session-stats {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}
.daily-session-rate {
  font-size: 0.75rem;
  font-weight: 600;
  color: hsl(var(--accent));
}
.daily-expand-icon {
  width: 16px;
  height: 16px;
  color: hsl(var(--muted-foreground));
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.daily-expand-icon.expanded {
  transform: rotate(180deg);
}

.daily-session-athletes {
  padding: 0.5rem 0.75rem;
}

.daily-progress-bar {
  height: 3px;
  border-radius: 2px;
  background: hsl(var(--muted) / 0.4);
  margin-bottom: 0.5rem;
  overflow: hidden;
}
.daily-progress-fill {
  height: 100%;
  border-radius: 2px;
  background: hsl(var(--accent));
  transition: width 0.5s ease;
}

.daily-athlete-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0;
  border-bottom: 1px solid hsl(var(--border) / 0.5);
  font-size: 0.75rem;
}
.daily-athlete-row:last-child {
  border-bottom: none;
}
.daily-athlete-name {
  font-weight: 600;
  color: hsl(var(--foreground));
  min-width: 56px;
}
.daily-athlete-sid {
  color: hsl(var(--muted-foreground));
  min-width: 56px;
}
.daily-athlete-grp {
  color: hsl(var(--muted-foreground));
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.daily-athlete-method {
  color: hsl(var(--muted-foreground));
  font-size: 0.6875rem;
  flex-shrink: 0;
}
.daily-athlete-time {
  color: hsl(var(--muted-foreground));
  font-size: 0.6875rem;
  flex-shrink: 0;
  min-width: 40px;
  text-align: right;
}

.daily-badge-muted {
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
</style>
