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

    <!-- Modal -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { sessionApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { TrainingSession } from '@/types'

const appStore = useAppStore()
const sessions = ref<TrainingSession[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ date: '', start_time: '', end_time: '', location: '', description: '' })

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

async function generateQR(s: TrainingSession) {
  try { await sessionApi.generateQR(s.id, {}); appStore.showToast('二维码已生成', 'success') } catch { appStore.showToast('生成失败', 'error') }
}

onMounted(loadSessions)
</script>
