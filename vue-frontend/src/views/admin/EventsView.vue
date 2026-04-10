<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">项目管理</h2><p class="section-desc">管理田径比赛项目</p></div>
      <button class="btn-primary text-sm" @click="openAdd">+ 添加项目</button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="e in events" :key="e.id" class="card-base p-5">
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', e.type === 'time' ? 'bg-primary/10 text-primary' : 'bg-accent/10 text-accent']">
              <svg v-if="e.type === 'time'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
            </div>
            <div>
              <p class="font-semibold text-foreground">{{ e.name }}</p>
              <div class="flex gap-2 mt-1">
                <span :class="e.type === 'time' ? 'badge-primary' : 'badge-accent'">{{ e.type === 'time' ? '计时' : '计距' }}</span>
                <span class="badge-primary">{{ { all: '不限', male: '男子', female: '女子' }[e.gender_limit] || e.gender_limit }}</span>
              </div>
            </div>
          </div>
          <div class="flex gap-1">
            <button class="btn-ghost text-xs px-2 py-1" @click="openEdit(e)">编辑</button>
            <button class="btn-ghost text-xs px-2 py-1 text-destructive" @click="handleDelete(e)">删除</button>
          </div>
        </div>
      </div>
      <div v-if="!events.length" class="col-span-full text-center py-12 text-muted-foreground">暂无比赛项目</div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <h3 class="text-lg font-bold text-foreground mb-4">{{ editingId ? '编辑项目' : '添加项目' }}</h3>
          <form @submit.prevent="handleSave" class="space-y-3">
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">项目名称 *</label><input v-model="form.name" class="input-base" required /></div>
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">类型</label>
                <select v-model="form.type" class="input-base"><option value="time">计时</option><option value="distance">计距</option></select>
              </div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">性别限制</label>
                <select v-model="form.gender_limit" class="input-base"><option value="all">不限</option><option value="male">男子</option><option value="female">女子</option></select>
              </div>
            </div>
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
import { eventApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Event } from '@/types'

const appStore = useAppStore()
const events = ref<Event[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ name: '', type: 'time', gender_limit: 'all' })

async function loadEvents() {
  try { events.value = (await eventApi.list()).data || [] } catch { events.value = [] }
}

function openAdd() { editingId.value = null; Object.assign(form, { name: '', type: 'time', gender_limit: 'all' }); showModal.value = true }
function openEdit(e: Event) { editingId.value = e.id; Object.assign(form, { name: e.name, type: e.type, gender_limit: e.gender_limit }); showModal.value = true }

async function handleSave() {
  saving.value = true
  try {
    if (editingId.value) { await eventApi.update(editingId.value, { ...form }); appStore.showToast('已更新', 'success') }
    else { await eventApi.create({ ...form }); appStore.showToast('已添加', 'success') }
    showModal.value = false; await loadEvents()
  } catch { appStore.showToast('操作失败', 'error') } finally { saving.value = false }
}

async function handleDelete(e: Event) {
  if (!confirm(`确认删除项目 "${e.name}" 吗？`)) return
  try { await eventApi.delete(e.id); appStore.showToast('已删除', 'success'); await loadEvents() } catch { appStore.showToast('删除失败，可能存在关联成绩', 'error') }
}

onMounted(loadEvents)
</script>
