<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">成绩录入</h2><p class="section-desc">记录运动员比赛和训练成绩</p></div>
      <button class="btn-primary text-sm" @click="openAdd">+ 录入成绩</button>
    </div>

    <div class="flex flex-wrap gap-3 mb-4">
      <select v-model="filterEvent" class="input-base max-w-[180px]">
        <option value="">全部项目</option>
        <option v-for="e in events" :key="e.id" :value="String(e.id)">{{ e.name }}</option>
      </select>
      <select v-model="filterAthlete" class="input-base max-w-[180px]">
        <option value="">全部运动员</option>
        <option v-for="a in athletes" :key="a.id" :value="String(a.id)">{{ a.name }}</option>
      </select>
    </div>

    <div class="card-base overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead><tr><th>运动员</th><th>项目</th><th>成绩</th><th class="hidden sm:table-cell">是否正式</th><th class="hidden md:table-cell">备注</th><th class="hidden lg:table-cell">时间</th><th class="text-right">操作</th></tr></thead>
          <tbody>
            <tr v-for="s in scores" :key="s.id">
              <td class="font-medium">{{ s.athlete_name || s.athlete_id }}</td>
              <td>{{ s.event_name || s.event_id }}</td>
              <td class="font-semibold text-accent">{{ s.performance }}</td>
              <td class="hidden sm:table-cell"><span :class="s.is_official ? 'badge-success' : 'badge-primary'">{{ s.is_official ? '正式' : '训练' }}</span></td>
              <td class="hidden md:table-cell text-muted-foreground">{{ s.remark || '—' }}</td>
              <td class="hidden lg:table-cell text-muted-foreground text-xs">{{ s.recorded_at?.slice(0, 10) }}</td>
              <td class="text-right">
                <button class="btn-ghost text-xs px-2 py-1" @click="openEdit(s)">编辑</button>
                <button class="btn-ghost text-xs px-2 py-1 text-destructive" @click="handleDelete(s)">删除</button>
              </td>
            </tr>
            <tr v-if="!scores.length"><td colspan="7" class="text-center text-muted-foreground py-8">暂无成绩记录</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <h3 class="text-lg font-bold text-foreground mb-4">{{ editingId ? '编辑成绩' : '录入成绩' }}</h3>
          <form @submit.prevent="handleSave" class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">运动员 *</label>
                <select v-model="form.athlete_id" class="input-base" required>
                  <option value="">请选择</option>
                  <option v-for="a in athletes" :key="a.id" :value="a.id">{{ a.name }}</option>
                </select>
              </div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">项目 *</label>
                <select v-model="form.event_id" class="input-base" required>
                  <option value="">请选择</option>
                  <option v-for="e in events" :key="e.id" :value="e.id">{{ e.name }}</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">成绩 *</label><input v-model.number="form.performance" type="number" step="0.01" class="input-base" required /></div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">类型</label>
                <select v-model="form.is_official" class="input-base">
                  <option :value="true">正式比赛</option>
                  <option :value="false">训练成绩</option>
                </select>
              </div>
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
import { scoreApi, eventApi, athleteApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Score, Event, Athlete } from '@/types'

const appStore = useAppStore()
const scores = ref<Score[]>([])
const events = ref<Event[]>([])
const athletes = ref<Athlete[]>([])
const filterEvent = ref('')
const filterAthlete = ref('')
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ athlete_id: '' as string | number, event_id: '' as string | number, performance: 0, is_official: true, remark: '' })

async function loadScores() {
  try {
    const p: Record<string, string> = {}
    if (filterEvent.value) p.event_id = filterEvent.value
    if (filterAthlete.value) p.athlete_id = filterAthlete.value
    scores.value = (await scoreApi.list(p)).data || []
  } catch { scores.value = [] }
}

async function loadMeta() {
  const [eRes, aRes] = await Promise.allSettled([eventApi.list(), athleteApi.list()])
  if (eRes.status === 'fulfilled') events.value = eRes.value.data || []
  if (aRes.status === 'fulfilled') athletes.value = aRes.value.data || []
}

function openAdd() {
  editingId.value = null
  Object.assign(form, { athlete_id: '', event_id: '', performance: 0, is_official: true, remark: '' })
  showModal.value = true
}

function openEdit(s: Score) {
  editingId.value = s.id
  Object.assign(form, { athlete_id: s.athlete_id, event_id: s.event_id, performance: s.performance, is_official: s.is_official, remark: s.remark })
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const data = { athlete_id: Number(form.athlete_id), event_id: Number(form.event_id), performance: form.performance, is_official: form.is_official, remark: form.remark }
    if (editingId.value) { await scoreApi.update(editingId.value, data); appStore.showToast('成绩已更新', 'success') }
    else { await scoreApi.create(data); appStore.showToast('成绩已录入', 'success') }
    showModal.value = false; await loadScores()
  } catch { appStore.showToast('操作失败', 'error') } finally { saving.value = false }
}

async function handleDelete(s: Score) {
  if (!confirm('确认删除？')) return
  try { await scoreApi.delete(s.id); appStore.showToast('已删除', 'success'); await loadScores() } catch { appStore.showToast('删除失败', 'error') }
}

watch([filterEvent, filterAthlete], loadScores)
onMounted(() => { loadMeta(); loadScores() })
</script>
