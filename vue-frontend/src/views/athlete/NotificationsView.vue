<template>
  <div>
    <!-- Header -->
    <div class="section-header">
      <div>
        <h2 class="section-title">通知中心</h2>
        <p class="section-desc">查看训练安排和团队公告</p>
      </div>
      <button v-if="notifications.length && hasUnread" class="btn-secondary text-xs" @click="markAllRead">
        <svg class="w-3.5 h-3.5 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        全部已读
      </button>
    </div>

    <!-- Filter tabs -->
    <div class="filter-tabs mb-5 animate-fade-in">
      <button v-for="tab in tabs" :key="tab.value" :class="['filter-tab', { active: activeTab === tab.value }]" @click="activeTab = tab.value">
        {{ tab.label }}
        <span v-if="tab.count > 0" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Notifications list -->
    <div v-if="filteredNotifications.length" class="space-y-3">
      <div v-for="(n, i) in filteredNotifications" :key="n.id" class="notif-card animate-fade-in" :class="{ unread: !n.is_read }" :style="{ animationDelay: i * 50 + 'ms' }" @click="toggleExpand(n)">
        <!-- Header -->
        <div class="notif-card-header">
          <div class="notif-card-icon" :class="'type-' + n.type">
            <svg v-if="n.type === 'training'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <svg v-else-if="n.type === 'announcement'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/></svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <p class="text-sm font-semibold text-foreground truncate">{{ n.title }}</p>
              <span class="notif-priority" :class="'priority-' + n.priority">{{ priorityLabel(n.priority) }}</span>
            </div>
            <p class="text-[11px] text-muted-foreground mt-0.5">{{ formatDateTime(n.created_at) }}</p>
          </div>
          <div class="flex items-center gap-2">
            <div v-if="!n.is_read" class="unread-indicator" />
            <svg :class="['w-4 h-4 text-muted-foreground transition-transform', { 'rotate-180': expandedId === n.id }]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </div>
        </div>

        <!-- Expanded content -->
        <Transition name="expand">
          <div v-if="expandedId === n.id" class="notif-card-body">
            <p class="text-sm text-foreground leading-relaxed whitespace-pre-wrap">{{ n.content }}</p>

            <!-- Session info for training -->
            <div v-if="n.session_id" class="session-info-card">
              <div class="session-info-row" v-if="n.session_date">
                <svg class="w-3.5 h-3.5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                <span>{{ n.session_date }}</span>
              </div>
              <div class="session-info-row" v-if="n.session_time">
                <svg class="w-3.5 h-3.5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                <span>{{ n.session_time }}</span>
              </div>
              <div class="session-info-row" v-if="n.session_location">
                <svg class="w-3.5 h-3.5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                <span>{{ n.session_location }}</span>
              </div>
            </div>

            <div class="notif-card-footer">
              <span class="text-[11px] text-muted-foreground">由 {{ n.creator_name || '管理员' }} 发布</span>
              <span v-if="n.is_read" class="read-badge">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                已读
              </span>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state animate-fade-in">
      <div class="empty-icon-wrap">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
      </div>
      <p class="text-sm font-medium text-foreground mt-3">暂无通知</p>
      <p class="text-xs text-muted-foreground mt-1">新通知将在这里显示</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { notificationApi } from '@/api'
import type { Notification } from '@/types'

const notifications = ref<Notification[]>([])
const activeTab = ref('all')
const expandedId = ref<number | null>(null)
const loading = ref(false)

const tabs = computed(() => {
  const all = notifications.value
  const training = all.filter(n => n.type === 'training')
  const announcement = all.filter(n => n.type === 'announcement')
  const general = all.filter(n => n.type === 'general')
  const unread = all.filter(n => !n.is_read)
  return [
    { label: '全部', value: 'all', count: 0 },
    { label: '训练', value: 'training', count: training.length },
    { label: '公告', value: 'announcement', count: announcement.length },
    { label: '未读', value: 'unread', count: unread.length },
  ]
})

const hasUnread = computed(() => notifications.value.some(n => !n.is_read))

const filteredNotifications = computed(() => {
  if (activeTab.value === 'all') return notifications.value
  if (activeTab.value === 'unread') return notifications.value.filter(n => !n.is_read)
  return notifications.value.filter(n => n.type === activeTab.value)
})

function priorityLabel(p: string) {
  const map: Record<string, string> = { low: '普通', normal: '一般', high: '重要', urgent: '紧急' }
  return map[p] || p
}

function formatDateTime(d: string) {
  if (!d) return ''
  const dt = new Date(d)
  const now = new Date()
  const diff = now.getTime() - dt.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 172800000) return '昨天'
  return d.slice(0, 16).replace('T', ' ')
}

async function toggleExpand(n: Notification) {
  if (expandedId.value === n.id) {
    expandedId.value = null
    return
  }
  expandedId.value = n.id
  if (!n.is_read) {
    try {
      await notificationApi.markAsRead(n.id)
      n.is_read = true
    } catch { /* ignore */ }
  }
}

async function markAllRead() {
  try {
    await notificationApi.markAllRead()
    notifications.value.forEach(n => { n.is_read = true })
  } catch { /* ignore */ }
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await notificationApi.list({ limit: '100' })
    notifications.value = res.data || []
  } catch { /* ignore */ }
  loading.value = false
})
</script>

<style scoped>
/* Filter tabs */
.filter-tabs {
  display: flex;
  gap: 0.375rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}
.filter-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.4375rem 0.875rem;
  border-radius: 99px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: hsl(var(--muted-foreground));
  background: hsl(var(--muted) / 0.5);
  border: 1px solid transparent;
  transition: var(--transition-fast);
  white-space: nowrap;
  cursor: pointer;
}
.filter-tab:hover {
  background: hsl(var(--muted));
}
.filter-tab.active {
  background: hsl(var(--accent) / 0.1);
  color: hsl(var(--accent));
  border-color: hsl(var(--accent) / 0.2);
}
.tab-count {
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0 0.375rem;
  border-radius: 99px;
  background: hsl(var(--muted-foreground) / 0.15);
  min-width: 18px;
  text-align: center;
}
.filter-tab.active .tab-count {
  background: hsl(var(--accent) / 0.2);
}

/* Notification cards */
.notif-card {
  border-radius: var(--radius-md);
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  box-shadow: var(--shadow-card);
  overflow: hidden;
  cursor: pointer;
  transition: var(--transition-smooth);
}
.notif-card:hover {
  box-shadow: var(--shadow-card-hover);
}
.notif-card.unread {
  border-left: 3px solid hsl(var(--accent));
}
.notif-card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
}
.notif-card-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.notif-card-icon.type-training { background: hsl(var(--accent) / 0.12); color: hsl(var(--accent)); }
.notif-card-icon.type-announcement { background: hsl(var(--primary) / 0.12); color: hsl(var(--primary-light)); }
.notif-card-icon.type-general { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }

.notif-priority {
  font-size: 0.6rem;
  font-weight: 600;
  padding: 0.0625rem 0.375rem;
  border-radius: 4px;
  flex-shrink: 0;
}
.priority-low { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }
.priority-normal { background: hsl(var(--primary) / 0.1); color: hsl(var(--primary-light)); }
.priority-high { background: hsl(var(--warning) / 0.15); color: hsl(var(--warning)); }
.priority-urgent { background: hsl(var(--destructive) / 0.15); color: hsl(var(--destructive)); }

.unread-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: hsl(var(--accent));
  animation: pulse-soft 2s ease-in-out infinite;
}

/* Expanded body */
.notif-card-body {
  padding: 0 1rem 1rem;
  border-top: 1px solid hsl(var(--border));
  margin-top: 0;
  padding-top: 0.875rem;
}
.session-info-card {
  margin-top: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  background: hsl(var(--accent) / 0.04);
  border: 1px solid hsl(var(--accent) / 0.1);
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.session-info-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: hsl(var(--foreground));
}
.notif-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.75rem;
  padding-top: 0.625rem;
  border-top: 1px solid hsl(var(--border));
}
.read-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 500;
  color: hsl(var(--success));
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}
.empty-icon-wrap {
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
  padding-top: 0;
  padding-bottom: 0;
}
.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
