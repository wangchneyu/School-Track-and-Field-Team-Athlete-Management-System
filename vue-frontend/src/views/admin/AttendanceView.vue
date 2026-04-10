<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">考勤管理</h2><p class="section-desc">记录和查看训练出勤</p></div>
      <button class="btn-primary text-sm" @click="openAdd">+ 记录考勤</button>
    </div>

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
import { attendanceApi, sessionApi, athleteApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Attendance, TrainingSession, Athlete } from '@/types'

const appStore = useAppStore()
const records = ref<Attendance[]>([])
const sessions = ref<TrainingSession[]>([])
const athletes = ref<Athlete[]>([])
const filterSession = ref('')
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ session_id: '' as string | number, athlete_id: '' as string | number, status: 'present', remark: '' })

function statusBadge(s: string) {
  return { present: 'badge-success', late: 'badge-warning', absent: 'badge-destructive', leave: 'badge-primary' }[s] || 'badge-primary'
}
function statusText(s: string) {
  return { present: '出勤', late: '迟到', absent: '缺勤', leave: '请假' }[s] || s
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
    showModal.value = false; await loadRecords()
  } catch { appStore.showToast('操作失败', 'error') } finally { saving.value = false }
}

async function handleDelete(a: Attendance) {
  if (!confirm('确认删除？')) return
  try { await attendanceApi.delete(a.id); appStore.showToast('已删除', 'success'); await loadRecords() } catch { appStore.showToast('删除失败', 'error') }
}

watch(filterSession, loadRecords)
onMounted(() => { loadMeta(); loadRecords() })
</script>
