<template>
  <div>
    <div class="section-header">
      <div>
        <h2 class="section-title">运动员管理</h2>
        <p class="section-desc">管理田径队所有运动员信息</p>
      </div>
      <button class="btn-primary text-sm" @click="openAdd">+ 添加运动员</button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3 mb-4">
      <input v-model="searchName" type="text" placeholder="搜索姓名..." class="input-base max-w-[200px]" />
      <select v-model="filterGroup" class="input-base max-w-[160px]">
        <option value="">全部分组</option>
        <option v-for="g in groups" :key="g" :value="g">{{ g }}</option>
      </select>
    </div>

    <!-- Table -->
    <div class="card-base overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead>
            <tr>
              <th>姓名</th>
              <th>学号</th>
              <th>性别</th>
              <th class="hidden sm:table-cell">分组</th>
              <th class="hidden md:table-cell">主项</th>
              <th class="hidden lg:table-cell">联系电话</th>
              <th class="text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filteredAthletes" :key="a.id">
              <td class="font-medium">{{ a.name }}</td>
              <td class="text-muted-foreground">{{ a.student_id }}</td>
              <td><span :class="a.gender === '男' ? 'badge-primary' : 'badge-accent'">{{ a.gender }}</span></td>
              <td class="hidden sm:table-cell text-muted-foreground">{{ a.group || '—' }}</td>
              <td class="hidden md:table-cell text-muted-foreground">{{ a.main_event || '—' }}</td>
              <td class="hidden lg:table-cell text-muted-foreground">{{ a.phone || '—' }}</td>
              <td class="text-right">
                <button class="btn-ghost text-xs px-2 py-1" @click="openEdit(a)">编辑</button>
                <button class="btn-ghost text-xs px-2 py-1 text-destructive" @click="handleDelete(a)">删除</button>
              </td>
            </tr>
            <tr v-if="!filteredAthletes.length">
              <td colspan="7" class="text-center text-muted-foreground py-8">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <h3 class="text-lg font-bold text-foreground mb-4">{{ editingId ? '编辑运动员' : '添加运动员' }}</h3>
          <form @submit.prevent="handleSave" class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">姓名 *</label>
                <input v-model="form.name" class="input-base" required />
              </div>
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">学号 *</label>
                <input v-model="form.student_id" class="input-base" required />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">性别 *</label>
                <select v-model="form.gender" class="input-base" required>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">分组</label>
                <input v-model="form.group" class="input-base" placeholder="如：短跑组" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">主项</label>
                <input v-model="form.main_event" class="input-base" placeholder="如：100米" />
              </div>
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">联系电话</label>
                <input v-model="form.phone" class="input-base" />
              </div>
            </div>
            <div v-if="!editingId" class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">登录用户名 *</label>
                <input v-model="form.username" class="input-base" required />
              </div>
              <div>
                <label class="text-xs font-medium text-muted-foreground mb-1 block">初始密码 *</label>
                <input v-model="form.password" class="input-base" required />
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
import { ref, computed, onMounted, reactive } from 'vue'
import { athleteApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Athlete } from '@/types'

const appStore = useAppStore()
const athletes = ref<Athlete[]>([])
const searchName = ref('')
const filterGroup = ref('')
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)

const form = reactive({
  name: '', student_id: '', gender: '男', group: '', main_event: '', phone: '',
  username: '', password: '',
})

const groups = computed(() => [...new Set(athletes.value.map(a => a.group).filter(Boolean))])

const filteredAthletes = computed(() => {
  return athletes.value.filter(a => {
    if (searchName.value && !a.name.includes(searchName.value)) return false
    if (filterGroup.value && a.group !== filterGroup.value) return false
    return true
  })
})

async function loadAthletes() {
  try {
    const res = await athleteApi.list()
    athletes.value = Array.isArray(res.data) ? res.data : []
  } catch { athletes.value = [] }
}

function openAdd() {
  editingId.value = null
  Object.assign(form, { name: '', student_id: '', gender: '男', group: '', main_event: '', phone: '', username: '', password: '' })
  showModal.value = true
}

function openEdit(a: Athlete) {
  editingId.value = a.id
  Object.assign(form, { name: a.name, student_id: a.student_id, gender: a.gender, group: a.group, main_event: a.main_event, phone: a.phone })
  showModal.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editingId.value) {
      await athleteApi.update(editingId.value, { name: form.name, student_id: form.student_id, gender: form.gender, group: form.group, main_event: form.main_event, phone: form.phone })
      appStore.showToast('运动员信息已更新', 'success')
    } else {
      await athleteApi.create({ name: form.name, student_id: form.student_id, gender: form.gender, group: form.group, main_event: form.main_event, phone: form.phone, username: form.username, password: form.password })
      appStore.showToast('运动员添加成功', 'success')
    }
    showModal.value = false
    await loadAthletes()
  } catch {
    appStore.showToast('操作失败，请检查输入', 'error')
  } finally { saving.value = false }
}

async function handleDelete(a: Athlete) {
  if (!confirm(`确认删除运动员 "${a.name}" 吗？此操作不可恢复。`)) return
  try {
    await athleteApi.delete(a.id)
    appStore.showToast('已删除', 'success')
    await loadAthletes()
  } catch { appStore.showToast('删除失败', 'error') }
}

onMounted(loadAthletes)
</script>
