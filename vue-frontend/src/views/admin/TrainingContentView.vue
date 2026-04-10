<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">训练内容</h2><p class="section-desc">管理训练计划和内容</p></div>
      <button class="btn-primary text-sm" @click="openAdd">+ 新增内容</button>
    </div>

    <div class="flex flex-wrap gap-3 mb-4">
      <select v-model="filterCat" class="input-base max-w-[160px]">
        <option value="">全部类别</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filterIntensity" class="input-base max-w-[140px]">
        <option value="">全部强度</option>
        <option value="low">低</option>
        <option value="medium">中</option>
        <option value="high">高</option>
      </select>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="c in contents" :key="c.id" class="card-base p-5">
        <div class="flex items-start justify-between mb-2">
          <h4 class="font-semibold text-foreground">{{ c.title }}</h4>
          <div class="flex gap-1 flex-shrink-0">
            <button class="btn-ghost text-xs px-2 py-1" @click="openEdit(c)">编辑</button>
            <button class="btn-ghost text-xs px-2 py-1 text-destructive" @click="handleDelete(c)">删除</button>
          </div>
        </div>
        <p class="text-sm text-muted-foreground line-clamp-3">{{ c.content }}</p>
        <div class="flex flex-wrap gap-2 mt-3">
          <span v-if="c.category" class="badge-primary">{{ c.category }}</span>
          <span v-if="c.target_group" class="badge-accent">{{ c.target_group }}</span>
          <span :class="{'badge-success': c.intensity === 'low', 'badge-warning': c.intensity === 'medium', 'badge-destructive': c.intensity === 'high'}">
            {{ { low: '低强度', medium: '中强度', high: '高强度' }[c.intensity] }}
          </span>
          <span class="badge-primary">{{ c.duration }}分钟</span>
        </div>
      </div>
      <div v-if="!contents.length" class="col-span-full text-center py-12 text-muted-foreground">暂无训练内容</div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content max-w-xl">
          <h3 class="text-lg font-bold text-foreground mb-4">{{ editingId ? '编辑内容' : '新增内容' }}</h3>
          <form @submit.prevent="handleSave" class="space-y-3">
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">标题 *</label><input v-model="form.title" class="input-base" required /></div>
            <div><label class="text-xs font-medium text-muted-foreground mb-1 block">内容 *</label><textarea v-model="form.content" class="input-base" rows="4" required /></div>
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">类别</label><input v-model="form.category" class="input-base" placeholder="如：速度、力量" /></div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">目标分组</label><input v-model="form.target_group" class="input-base" placeholder="如：短跑组" /></div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">时长(分钟)</label><input v-model.number="form.duration" type="number" class="input-base" /></div>
              <div><label class="text-xs font-medium text-muted-foreground mb-1 block">强度</label>
                <select v-model="form.intensity" class="input-base"><option value="low">低</option><option value="medium">中</option><option value="high">高</option></select>
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
import { ref, onMounted, reactive, watch } from 'vue'
import { trainingContentApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { TrainingContent } from '@/types'

const appStore = useAppStore()
const contents = ref<TrainingContent[]>([])
const categories = ref<string[]>([])
const filterCat = ref('')
const filterIntensity = ref('')
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const form = reactive({ title: '', content: '', category: '', target_group: '', duration: 60, intensity: 'medium' })

async function loadContents() {
  try {
    const p: Record<string, string> = {}
    if (filterCat.value) p.category = filterCat.value
    if (filterIntensity.value) p.intensity = filterIntensity.value
    contents.value = (await trainingContentApi.list(p)).data || []
  } catch { contents.value = [] }
}

async function loadCategories() {
  try { categories.value = (await trainingContentApi.categories()).data || [] } catch { categories.value = [] }
}

function openAdd() { editingId.value = null; Object.assign(form, { title: '', content: '', category: '', target_group: '', duration: 60, intensity: 'medium' }); showModal.value = true }
function openEdit(c: TrainingContent) { editingId.value = c.id; Object.assign(form, { title: c.title, content: c.content, category: c.category, target_group: c.target_group, duration: c.duration, intensity: c.intensity }); showModal.value = true }

async function handleSave() {
  saving.value = true
  try {
    if (editingId.value) { await trainingContentApi.update(editingId.value, { ...form }); appStore.showToast('已更新', 'success') }
    else { await trainingContentApi.create({ ...form }); appStore.showToast('已添加', 'success') }
    showModal.value = false; await loadContents()
  } catch { appStore.showToast('操作失败', 'error') } finally { saving.value = false }
}

async function handleDelete(c: TrainingContent) {
  if (!confirm('确认删除？')) return
  try { await trainingContentApi.delete(c.id); appStore.showToast('已删除', 'success'); await loadContents() } catch { appStore.showToast('删除失败', 'error') }
}

watch([filterCat, filterIntensity], loadContents)
onMounted(() => { loadCategories(); loadContents() })
</script>
