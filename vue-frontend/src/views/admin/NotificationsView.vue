<template>
  <div>
    <!-- Header -->
    <div class="section-header">
      <div>
        <h2 class="section-title">通知管理</h2>
        <p class="section-desc">发布训练通知和团队公告，查看已读状态</p>
      </div>
      <button class="btn-primary text-sm" @click="openCreateModal">
        <svg class="w-4 h-4 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6"/></svg>
        发布通知
      </button>
    </div>

    <!-- Notifications list -->
    <div v-if="notifications.length" class="space-y-3">
      <div v-for="(n, i) in notifications" :key="n.id" class="notif-admin-card animate-fade-in" :style="{ animationDelay: i * 40 + 'ms' }">
        <div class="notif-admin-header" @click="toggleExpand(n.id)">
          <div class="notif-admin-icon" :class="'type-' + n.type">
            <svg v-if="n.type === 'training'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <svg v-else-if="n.type === 'announcement'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/></svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <p class="text-sm font-semibold text-foreground">{{ n.title }}</p>
              <span class="notif-type-badge" :class="'type-' + n.type">{{ typeLabel(n.type) }}</span>
              <span class="notif-priority-badge" :class="'priority-' + n.priority">{{ priorityLabel(n.priority) }}</span>
            </div>
            <p class="text-[11px] text-muted-foreground mt-0.5">
              {{ formatDateTime(n.created_at) }}
              <span v-if="n.target_group"> · 目标: {{ n.target_group }}</span>
              <span v-else> · 全体成员</span>
            </p>
          </div>

          <!-- Read status bar -->
          <div class="read-status-bar">
            <div class="read-status-info">
              <span class="read-status-count">{{ n.read_count }}/{{ n.total_target }}</span>
              <span class="read-status-label">已读</span>
            </div>
            <div class="read-progress-track">
              <div class="read-progress-fill" :style="{ width: readRate(n) + '%' }" :class="readRate(n) >= 80 ? 'high' : readRate(n) >= 50 ? 'medium' : 'low'" />
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button class="btn-ghost p-1.5 rounded-md text-muted-foreground hover:text-destructive" @click.stop="deleteNotif(n.id)" title="删除">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
            <svg :class="['w-4 h-4 text-muted-foreground transition-transform', { 'rotate-180': expandedId === n.id }]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </div>
        </div>

        <!-- Expanded detail -->
        <Transition name="expand">
          <div v-if="expandedId === n.id" class="notif-admin-detail">
            <div class="notif-admin-content">
              <p class="text-sm text-foreground leading-relaxed whitespace-pre-wrap">{{ n.content }}</p>
            </div>

            <!-- Read status detail -->
            <div class="read-status-detail" v-if="readDetail">
              <h4 class="text-xs font-bold text-foreground mb-3 flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                已读/未读详情
              </h4>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- Read users -->
                <div>
                  <p class="text-[11px] font-semibold text-success mb-2 flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    已读 ({{ readDetail.read_users?.length || 0 }})
                  </p>
                  <div v-if="readDetail.read_users?.length" class="space-y-1">
                    <div v-for="u in readDetail.read_users" :key="u.user_id" class="read-user-item read">
                      <span class="text-xs font-medium">{{ u.username }}</span>
                      <span class="text-[10px] text-muted-foreground">{{ formatDateTime(u.read_at) }}</span>
                    </div>
                  </div>
                  <p v-else class="text-[11px] text-muted-foreground">暂无</p>
                </div>

                <!-- Unread users -->
                <div>
                  <p class="text-[11px] font-semibold text-destructive mb-2 flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    未读 ({{ readDetail.unread_users?.length || 0 }})
                  </p>
                  <div v-if="readDetail.unread_users?.length" class="space-y-1">
                    <div v-for="u in readDetail.unread_users" :key="u.user_id" class="read-user-item unread">
                      <span class="text-xs font-medium">{{ u.name || u.username }}</span>
                      <span class="text-[10px] text-muted-foreground">{{ u.username }}</span>
                    </div>
                  </div>
                  <p v-else class="text-[11px] text-muted-foreground">全部已读</p>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center py-4">
              <span class="text-xs text-muted-foreground">加载中...</span>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state animate-fade-in">
      <div class="empty-icon">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
      </div>
      <p class="text-sm font-medium text-foreground mt-3">暂无通知</p>
      <p class="text-xs text-muted-foreground mt-1">点击上方按钮发布第一条通知</p>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content max-w-xl">
        <h3 class="text-base font-bold text-foreground mb-4">发布通知</h3>

        <div class="space-y-4">
          <div>
            <label class="text-xs font-semibold text-foreground mb-1 block">标题</label>
            <input v-model="form.title" type="text" class="input-base" placeholder="输入通知标题" />
          </div>

          <div>
            <label class="text-xs font-semibold text-foreground mb-1 block">内容</label>
            <textarea v-model="form.content" class="input-base min-h-[100px] resize-y" placeholder="输入通知内容" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-semibold text-foreground mb-1 block">类型</label>
              <select v-model="form.type" class="input-base">
                <option value="training">训练通知</option>
                <option value="announcement">公告</option>
                <option value="general">一般通知</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-semibold text-foreground mb-1 block">优先级</label>
              <select v-model="form.priority" class="input-base">
                <option value="low">普通</option>
                <option value="normal">一般</option>
                <option value="high">重要</option>
                <option value="urgent">紧急</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-semibold text-foreground mb-1 block">目标分组</label>
              <select v-model="form.target_group" class="input-base">
                <option value="">全体成员</option>
                <option value="短跑组">短跑组</option>
                <option value="中长跑组">中长跑组</option>
                <option value="长跑组">长跑组</option>
                <option value="跳跃组">跳跃组</option>
                <option value="投掷组">投掷组</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-semibold text-foreground mb-1 block">关联训练课程</label>
              <select v-model="form.session_id" class="input-base">
                <option :value="null">无</option>
                <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.date }} {{ s.start_time }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button class="btn-secondary text-sm" @click="closeModal">取消</button>
          <button class="btn-primary text-sm" @click="submitNotif" :disabled="!form.title || !form.content">发布</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { notificationApi, sessionApi } from '@/api'
import { useAppStore } from '@/stores/app'
import type { Notification, NotificationDetail, TrainingSession } from '@/types'

const appStore = useAppStore()
const notifications = ref<Notification[]>([])
const sessions = ref<TrainingSession[]>([])
const expandedId = ref<number | null>(null)
const readDetail = ref<NotificationDetail | null>(null)
const showModal = ref(false)

const form = ref({
  title: '',
  content: '',
  type: 'training',
  priority: 'normal',
  target_group: '',
  session_id: null as number | null,
})

function typeLabel(t: string) {
  const map: Record<string, string> = { training: '训练', announcement: '公告', general: '通知' }
  return map[t] || t
}

function priorityLabel(p: string) {
  const map: Record<string, string> = { low: '普通', normal: '一般', high: '重要', urgent: '紧急' }
  return map[p] || p
}

function readRate(n: Notification) {
  return n.total_target > 0 ? Math.round((n.read_count / n.total_target) * 100) : 0
}

function formatDateTime(d: string) {
  if (!d) return ''
  const dt = new Date(d)
  const now = new Date()
  const diff = now.getTime() - dt.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.slice(0, 16).replace('T', ' ')
}

async function toggleExpand(id: number) {
  if (expandedId.value === id) {
    expandedId.value = null
    readDetail.value = null
    return
  }
  expandedId.value = id
  readDetail.value = null
  try {
    const res = await notificationApi.getReadStatus(id)
    readDetail.value = res.data
  } catch { /* ignore */ }
}

function openCreateModal() {
  form.value = { title: '', content: '', type: 'training', priority: 'normal', target_group: '', session_id: null }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

async function submitNotif() {
  try {
    const payload: Record<string, unknown> = {
      title: form.value.title,
      content: form.value.content,
      type: form.value.type,
      priority: form.value.priority,
      target_group: form.value.target_group,
    }
    if (form.value.session_id) {
      payload.session_id = form.value.session_id
    }
    await notificationApi.create(payload)
    appStore.showToast('通知发布成功', 'success')
    closeModal()
    await loadNotifications()
  } catch {
    appStore.showToast('发布失败', 'error')
  }
}

async function deleteNotif(id: number) {
  if (!confirm('确定删除该通知？')) return
  try {
    await notificationApi.delete(id)
    notifications.value = notifications.value.filter(n => n.id !== id)
    appStore.showToast('已删除', 'success')
  } catch {
    appStore.showToast('删除失败', 'error')
  }
}

async function loadNotifications() {
  try {
    const res = await notificationApi.list({ limit: '100', active_only: 'false' })
    notifications.value = res.data || []
  } catch { /* ignore */ }
}

onMounted(async () => {
  await Promise.allSettled([
    loadNotifications(),
    sessionApi.list().then(res => { sessions.value = res.data || [] }),
  ])
})
</script>

<style scoped>
/* Notification admin card */
.notif-admin-card {
  border-radius: var(--radius-md);
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  box-shadow: var(--shadow-card);
  overflow: hidden;
  transition: var(--transition-smooth);
}
.notif-admin-card:hover {
  box-shadow: var(--shadow-card-hover);
}

.notif-admin-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  cursor: pointer;
}

.notif-admin-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.notif-admin-icon.type-training { background: hsl(var(--accent) / 0.12); color: hsl(var(--accent)); }
.notif-admin-icon.type-announcement { background: hsl(var(--primary) / 0.12); color: hsl(var(--primary-light)); }
.notif-admin-icon.type-general { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }

/* Type & priority badges */
.notif-type-badge {
  font-size: 0.6rem;
  font-weight: 600;
  padding: 0.0625rem 0.375rem;
  border-radius: 4px;
}
.notif-type-badge.type-training { background: hsl(var(--accent) / 0.1); color: hsl(var(--accent)); }
.notif-type-badge.type-announcement { background: hsl(var(--primary) / 0.1); color: hsl(var(--primary-light)); }
.notif-type-badge.type-general { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }

.notif-priority-badge {
  font-size: 0.6rem;
  font-weight: 600;
  padding: 0.0625rem 0.375rem;
  border-radius: 4px;
}
.priority-low { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }
.priority-normal { background: hsl(var(--primary) / 0.08); color: hsl(var(--primary-light)); }
.priority-high { background: hsl(var(--warning) / 0.12); color: hsl(var(--warning)); }
.priority-urgent { background: hsl(var(--destructive) / 0.12); color: hsl(var(--destructive)); }

/* Read status bar */
.read-status-bar {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  min-width: 80px;
  flex-shrink: 0;
}
.read-status-info {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}
.read-status-count {
  font-size: 0.8125rem;
  font-weight: 700;
  color: hsl(var(--foreground));
}
.read-status-label {
  font-size: 0.625rem;
  color: hsl(var(--muted-foreground));
}
.read-progress-track {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: hsl(var(--muted));
  overflow: hidden;
}
.read-progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.read-progress-fill.high { background: hsl(var(--success)); }
.read-progress-fill.medium { background: hsl(var(--warning)); }
.read-progress-fill.low { background: hsl(var(--destructive)); }

/* Detail section */
.notif-admin-detail {
  padding: 0 1rem 1rem;
  border-top: 1px solid hsl(var(--border));
  padding-top: 0.875rem;
}
.notif-admin-content {
  margin-bottom: 1rem;
}

/* Read status detail */
.read-status-detail {
  padding: 1rem;
  border-radius: var(--radius-sm);
  background: hsl(var(--background));
  border: 1px solid hsl(var(--border));
}
.read-user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.375rem 0.5rem;
  border-radius: var(--radius-sm);
}
.read-user-item.read {
  background: hsl(var(--success) / 0.04);
}
.read-user-item.unread {
  background: hsl(var(--destructive) / 0.04);
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}
.empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: hsl(var(--muted));
  color: hsl(var(--muted-foreground) / 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

/* Expand transition */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}
.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 800px;
}
</style>
