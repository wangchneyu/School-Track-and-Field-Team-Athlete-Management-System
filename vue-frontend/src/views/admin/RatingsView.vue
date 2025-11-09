<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">评分管理</h2><p class="section-desc">对运动员进行综合评分</p></div>
      <button class="btn-primary text-sm" @click="openAdd">+ 添加评分</button>
    </div>

    <div class="card-base overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead><tr><th>运动员</th><th>日期</th><th>训练态度</th><th>出勤</th><th>表现</th><th class="hidden md:table-cell">评语</th><th class="text-right">操作</th></tr></thead>
          <tbody>
            <tr v-for="r in ratings" :key="r.id">
              <td class="font-medium">{{ r.athlete_name || r.athlete_id }}</td>
              <td class="text-muted-foreground">{{ r.date }}</td>
              <td><span class="font-semibold" :style="{ color: scoreColor(r.attitude) }">{{ r.attitude }}</span></td>
              <td><span class="font-semibold" :style="{ color: scoreColor(r.attendance) }">{{ r.attendance }}</span></td>
              <td><span class="font-semibold" :style="{ color: scoreColor(r.performance) }">{{ r.performance }}</span></td>
              <td class="hidden md:table-cell text-muted-foreground text-xs">{{ r.comment || '—' }}</td>
              <td class="text-right">
                <button class="btn-ghost text-xs px-2 py-1" @click="openEdit(r)">编辑</button>
                <button class="btn-ghost text-xs px-2 py-1 text-destructive" @click="handleDelete(r)">删除</button>
              </td>
            </tr>
            <tr v-if="!ratings.length"><td colspan="7" class="text-center text-muted-foreground py-8">暂无评分记录</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <h3 class="text-lg font-bold text-foreground mb-4">{{ editingId ? '编辑评分' : '添加评分' }}</h3>
          <form @submit.prevent="handleSave" class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">运动员 *</label>
                <select v-model="form.athlete_id" class="input-base" required>
                  <option value="">请选择</option>
                  <option v-for="a in athletes" :key="a.id" :value="a.id">{{ a.name }}</option>
                </select>
              </div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">日期</label><input v-model="form.date" type="date" class="input-base" /></div>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">态度 (0-100)</label><input v-model.number="form.attitude" type="number" min="0" max="100" class="input-base" required /></div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">出勤 (0-100)</label><input v-model.number="form.attendance" type="number" min="0" max="100" class="input-base" required /></div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">表现 (0-100)</label><input v-model.number="form.performance" type="number" min="0" max="100" class="input-base" required /></div>
            </div>
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">评语</label><textarea v-model="form.comment" class="input-base" rows="2" /></div>
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
import { ratingApi, athleteApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Rating, Athlete } from '@/types'

const appStore = useAppStore()
const ratings = ref<Rating[]>([])
const athletes = ref<Athlete[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ athlete_id: '' as string | number, date: '', attitude: 80, attendance: 80, performance: 80, comment: '' })

function scoreColor(v: number) {
  if (v >= 80) return 'hsl(var(--success))'
  if (v >= 60) return 'hsl(var(--warning))'
  return 'hsl(var(--destructive))'
}

async function loadRatings() {
  try { ratings.value = (await ratingApi.list()).data || [] } catch { ratings.value = [] }
}

async function loadAthletes() {
  try { athletes.value = (await athleteApi.list()).data || [] } catch { athletes.value = [] }
}

function openAdd() { editingId.value = null; Object.assign(form, { athlete_id: '', date: new Date().toISOString().slice(0, 10), attitude: 80, attendance: 80, performance: 80, comment: '' }); showModal.value = true }
function openEdit(r: Rating) { editingId.value = r.id; Object.assign(form, { athlete_id: r.athlete_id, date: r.date, attitude: r.attitude, attendance: r.attendance, performance: r.performance, comment: r.comment }); showModal.value = true }

async function handleSave() {
  saving.value = true
  try {
    const data = { athlete_id: Number(form.athlete_id), date: form.date, attitude: form.attitude, attendance: form.attendance, performance: form.performance, comment: form.comment }
    if (editingId.value) { await ratingApi.update(editingId.value, data); appStore.showToast('已更新', 'success') }
    else { await ratingApi.create(data); appStore.showToast('已添加', 'success') }
    showModal.value = false; await loadRatings()
  } catch { appStore.showToast('操作失败', 'error') } finally { saving.value = false }
}

async function handleDelete(r: Rating) {
  if (!confirm('确认删除？')) return
  try { await ratingApi.delete(r.id); appStore.showToast('已删除', 'success'); await loadRatings() } catch { appStore.showToast('删除失败', 'error') }
}

onMounted(() => { loadAthletes(); loadRatings() })
</script>
