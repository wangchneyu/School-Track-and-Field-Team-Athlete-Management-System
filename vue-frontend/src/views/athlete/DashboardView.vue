<template>
  <div>
    <!-- Welcome hero -->
    <div class="welcome-hero animate-fade-in">
      <div class="welcome-hero-bg" />
      <div class="welcome-hero-content">
        <div class="flex items-center gap-4">
          <div class="avatar-ring">
            <div class="avatar-inner">
              <span class="avatar-text">{{ profile?.name?.charAt(0) || '?' }}</span>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="welcome-name">{{ greeting }}，{{ profile?.name || '运动员' }}</h1>
            <p class="welcome-sub">{{ profile?.student_id }} · {{ profile?.group || '未分组' }} · {{ profile?.main_event || '' }}</p>
          </div>
        </div>
        <div class="welcome-badges">
          <span class="hero-badge">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            {{ profile?.gender }}
          </span>
          <span v-if="profile?.main_event" class="hero-badge hero-badge-accent">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            {{ profile.main_event }}
          </span>
        </div>
      </div>
    </div>

    <!-- Today's training notification -->
    <div v-if="todayTraining.length" class="training-alert animate-fade-in" style="animation-delay: 100ms">
      <div class="training-alert-header">
        <div class="training-alert-icon">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
        </div>
        <h3 class="training-alert-title">今日训练通知</h3>
        <span class="training-alert-badge">{{ todayTraining.length }}条</span>
      </div>
      <div class="training-alert-list">
        <div v-for="notif in todayTraining" :key="notif.id" class="training-alert-item" @click="handleNotifClick(notif)">
          <div class="training-alert-item-dot" :class="{ read: notif.is_read }" />
          <div class="flex-1 min-w-0">
            <p class="training-alert-item-title">{{ notif.title }}</p>
            <p class="training-alert-item-meta">
              <span v-if="notif.session_time">
                <svg class="w-3 h-3 inline mr-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                {{ notif.session_time }}
              </span>
              <span v-if="notif.session_location">
                <svg class="w-3 h-3 inline mr-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                {{ notif.session_location }}
              </span>
            </p>
          </div>
          <div class="training-alert-item-priority" :class="'priority-' + notif.priority">
            {{ priorityLabel(notif.priority) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Quick stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
      <div v-for="(stat, i) in statsCards" :key="stat.label" class="stat-card animate-fade-in" :style="{ animationDelay: (i * 80 + 150) + 'ms' }">
        <div class="stat-icon-wrap" :style="{ background: stat.bg }">
          <span v-html="stat.icon" />
        </div>
        <div class="stat-info">
          <span class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Two-column layout -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
      <!-- Recent scores -->
      <div class="card-base p-5 animate-fade-in" style="animation-delay: 350ms">
        <div class="section-header mb-4">
          <h3 class="section-title-sm">
            <svg class="w-4 h-4 text-accent inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            最近成绩
          </h3>
          <RouterLink to="/athlete/scores" class="text-xs font-medium text-accent hover:underline">查看全部 →</RouterLink>
        </div>
        <div v-if="recentScores.length" class="space-y-2">
          <div v-for="s in recentScores" :key="s.id" class="score-item">
            <div class="score-item-left">
              <div class="score-event-badge" :class="s.is_official ? 'official' : 'training'">
                {{ s.is_official ? '赛' : '训' }}
              </div>
              <div>
                <p class="text-sm font-medium text-foreground">{{ s.event_name || '项目' + s.event_id }}</p>
                <p class="text-[11px] text-muted-foreground">{{ formatDate(s.recorded_at) }}</p>
              </div>
            </div>
            <span class="score-value">{{ s.performance }}</span>
          </div>
        </div>
        <div v-else class="empty-state">
          <svg class="w-10 h-10 text-muted-foreground/30 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6m6 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0h6"/></svg>
          <p class="text-sm text-muted-foreground">暂无成绩记录</p>
        </div>
      </div>

      <!-- Recent ratings -->
      <div class="card-base p-5 animate-fade-in" style="animation-delay: 400ms">
        <div class="section-header mb-4">
          <h3 class="section-title-sm">
            <svg class="w-4 h-4 text-accent inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
            最近评分
          </h3>
          <RouterLink to="/athlete/ratings" class="text-xs font-medium text-accent hover:underline">查看全部 →</RouterLink>
        </div>
        <div v-if="recentRatings.length" class="space-y-3">
          <div v-for="r in recentRatings" :key="r.id" class="rating-item">
            <div class="rating-item-header">
              <p class="text-sm font-medium text-foreground">{{ r.date }}</p>
              <span class="rating-avg">{{ Math.round((r.attitude + r.attendance + r.performance) / 3) }}</span>
            </div>
            <div class="rating-bars">
              <div class="rating-bar-item">
                <span class="rating-bar-label">态度</span>
                <div class="rating-bar-track"><div class="rating-bar-fill" :style="{ width: r.attitude * 10 + '%' }" /></div>
                <span class="rating-bar-value">{{ r.attitude }}</span>
              </div>
              <div class="rating-bar-item">
                <span class="rating-bar-label">出勤</span>
                <div class="rating-bar-track"><div class="rating-bar-fill fill-success" :style="{ width: r.attendance * 10 + '%' }" /></div>
                <span class="rating-bar-value">{{ r.attendance }}</span>
              </div>
              <div class="rating-bar-item">
                <span class="rating-bar-label">表现</span>
                <div class="rating-bar-track"><div class="rating-bar-fill fill-warning" :style="{ width: r.performance * 10 + '%' }" /></div>
                <span class="rating-bar-value">{{ r.performance }}</span>
              </div>
            </div>
            <p v-if="r.comment" class="text-xs text-muted-foreground mt-2 italic leading-relaxed">"{{ r.comment }}"</p>
          </div>
        </div>
        <div v-else class="empty-state">
          <svg class="w-10 h-10 text-muted-foreground/30 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
          <p class="text-sm text-muted-foreground">暂无评分记录</p>
        </div>
      </div>
    </div>

    <!-- Recent notifications -->
    <div class="card-base p-5 animate-fade-in" style="animation-delay: 450ms">
      <div class="section-header mb-4">
        <h3 class="section-title-sm">
          <svg class="w-4 h-4 text-accent inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
          最新通知
        </h3>
        <RouterLink to="/athlete/notifications" class="text-xs font-medium text-accent hover:underline">全部通知 →</RouterLink>
      </div>
      <div v-if="recentNotifications.length" class="space-y-2">
        <div v-for="n in recentNotifications" :key="n.id" class="notif-item" :class="{ unread: !n.is_read }" @click="handleNotifClick(n)">
          <div class="notif-type-icon" :class="'type-' + n.type">
            <svg v-if="n.type === 'training'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <svg v-else-if="n.type === 'announcement'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"/></svg>
            <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-foreground truncate">{{ n.title }}</p>
            <p class="text-[11px] text-muted-foreground">{{ formatDateTime(n.created_at) }}</p>
          </div>
          <div v-if="!n.is_read" class="notif-unread-dot" />
        </div>
      </div>
      <div v-else class="empty-state">
        <p class="text-sm text-muted-foreground">暂无通知</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { scoreApi, attendanceApi, ratingApi, notificationApi } from '@/api'
import type { Score, Attendance, Rating, Notification } from '@/types'

const authStore = useAuthStore()
const profile = computed(() => authStore.athlete)
const myScores = ref<Score[]>([])
const myAttendance = ref<Attendance[]>([])
const myRatings = ref<Rating[]>([])
const todayTraining = ref<Notification[]>([])
const recentNotifications = ref<Notification[]>([])

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const myScoresCount = computed(() => myScores.value.length)
const recentScores = computed(() => myScores.value.slice(0, 5))
const recentRatings = computed(() => myRatings.value.slice(0, 3))
const ratingsCount = computed(() => myRatings.value.length)

const avgRating = computed(() => {
  if (!myRatings.value.length) return '—'
  const avg = myRatings.value.reduce((s, r) => s + (r.attitude + r.attendance + r.performance) / 3, 0) / myRatings.value.length
  return Math.round(avg * 10) / 10
})

const attendanceRate = computed(() => {
  if (!myAttendance.value.length) return '—'
  const present = myAttendance.value.filter(a => a.status === 'present' || a.status === 'late').length
  return Math.round((present / myAttendance.value.length) * 100)
})

const statsCards = computed(() => [
  {
    label: '成绩记录',
    value: myScoresCount.value,
    icon: '<svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>',
    bg: 'hsl(var(--accent) / 0.12)',
    color: 'hsl(var(--accent))',
  },
  {
    label: '出勤率',
    value: attendanceRate.value + (attendanceRate.value !== '—' ? '%' : ''),
    icon: '<svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    bg: 'hsl(var(--success) / 0.12)',
    color: 'hsl(var(--success))',
  },
  {
    label: '评分次数',
    value: ratingsCount.value,
    icon: '<svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>',
    bg: 'hsl(var(--primary) / 0.12)',
    color: 'hsl(var(--primary))',
  },
  {
    label: '平均得分',
    value: avgRating.value,
    icon: '<svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>',
    bg: 'hsl(var(--warning) / 0.12)',
    color: 'hsl(var(--warning))',
  },
])

function formatDate(d: string) {
  if (!d) return ''
  return d.slice(0, 10)
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
  return d.slice(0, 10)
}

function priorityLabel(p: string) {
  const map: Record<string, string> = { low: '普通', normal: '一般', high: '重要', urgent: '紧急' }
  return map[p] || p
}

async function handleNotifClick(n: Notification) {
  if (!n.is_read) {
    try {
      await notificationApi.markAsRead(n.id)
      n.is_read = true
    } catch { /* ignore */ }
  }
}

onMounted(async () => {
  if (!authStore.athlete) await authStore.fetchAthleteProfile()
  const [sRes, aRes, rRes, tRes, nRes] = await Promise.allSettled([
    scoreApi.getMe(),
    attendanceApi.getMe(),
    ratingApi.getMe(),
    notificationApi.getTodayTraining(),
    notificationApi.list({ limit: '5' }),
  ])
  if (sRes.status === 'fulfilled') myScores.value = sRes.value.data || []
  if (aRes.status === 'fulfilled') myAttendance.value = aRes.value.data || []
  if (rRes.status === 'fulfilled') myRatings.value = rRes.value.data || []
  if (tRes.status === 'fulfilled') todayTraining.value = tRes.value.data || []
  if (nRes.status === 'fulfilled') recentNotifications.value = nRes.value.data || []
})
</script>

<style scoped>
/* Welcome hero */
.welcome-hero {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 1.25rem;
  padding: 1.5rem;
}
.welcome-hero-bg {
  position: absolute;
  inset: 0;
  background: var(--gradient-hero);
  opacity: 0.95;
}
.welcome-hero-content {
  position: relative;
  z-index: 1;
}

.avatar-ring {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  padding: 2px;
  background: linear-gradient(135deg, hsl(var(--accent)), hsl(var(--accent-light)));
  flex-shrink: 0;
}
.avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: hsl(var(--sidebar));
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: hsl(var(--accent));
}

.welcome-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: hsl(210 40% 98%);
  margin-bottom: 0.25rem;
}
.welcome-sub {
  font-size: 0.75rem;
  color: hsl(210 30% 65%);
}
.welcome-badges {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.625rem;
  border-radius: 99px;
  font-size: 0.7rem;
  font-weight: 500;
  background: hsl(0 0% 100% / 0.1);
  color: hsl(210 30% 80%);
}
.hero-badge-accent {
  background: hsl(var(--accent) / 0.2);
  color: hsl(var(--accent-light));
}

/* Training alert */
.training-alert {
  border-radius: var(--radius-lg);
  border: 1px solid hsl(var(--accent) / 0.2);
  background: hsl(var(--accent) / 0.04);
  margin-bottom: 1.25rem;
  overflow: hidden;
}
.training-alert-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.875rem 1rem;
  border-bottom: 1px solid hsl(var(--accent) / 0.1);
}
.training-alert-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: hsl(var(--accent) / 0.15);
  color: hsl(var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse-soft 2s ease-in-out infinite;
}
.training-alert-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
  color: hsl(var(--foreground));
}
.training-alert-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  border-radius: 99px;
  background: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
}
.training-alert-list {
  padding: 0.5rem;
}
.training-alert-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.5rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-fast);
}
.training-alert-item:hover {
  background: hsl(var(--accent) / 0.06);
}
.training-alert-item-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: hsl(var(--accent));
  flex-shrink: 0;
}
.training-alert-item-dot.read {
  background: hsl(var(--muted-foreground) / 0.3);
}
.training-alert-item-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: hsl(var(--foreground));
}
.training-alert-item-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.6875rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.125rem;
}
.training-alert-item-priority {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  flex-shrink: 0;
}
.priority-low { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }
.priority-normal { background: hsl(var(--primary) / 0.1); color: hsl(var(--primary)); }
.priority-high { background: hsl(var(--warning) / 0.15); color: hsl(var(--warning)); }
.priority-urgent { background: hsl(var(--destructive) / 0.15); color: hsl(var(--destructive)); }

/* Stats cards */
.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: var(--radius-md);
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  box-shadow: var(--shadow-card);
  transition: var(--transition-smooth);
}
.stat-card:hover {
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-1px);
}
.stat-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.2;
}
.stat-label {
  font-size: 0.6875rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.125rem;
}

/* Score items */
.score-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid hsl(var(--border));
}
.score-item:last-child { border-bottom: none; }
.score-item-left {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}
.score-event-badge {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 700;
  flex-shrink: 0;
}
.score-event-badge.official {
  background: hsl(var(--accent) / 0.12);
  color: hsl(var(--accent));
}
.score-event-badge.training {
  background: hsl(var(--primary) / 0.1);
  color: hsl(var(--primary-light));
}
.score-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: hsl(var(--accent));
}

/* Rating items */
.rating-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid hsl(var(--border));
}
.rating-item:last-child { border-bottom: none; }
.rating-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.rating-avg {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: hsl(var(--accent) / 0.12);
  color: hsl(var(--accent));
  font-size: 0.8125rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.rating-bars { display: flex; flex-direction: column; gap: 0.375rem; }
.rating-bar-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.rating-bar-label {
  font-size: 0.6875rem;
  color: hsl(var(--muted-foreground));
  width: 28px;
  flex-shrink: 0;
}
.rating-bar-track {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: hsl(var(--muted));
  overflow: hidden;
}
.rating-bar-fill {
  height: 100%;
  border-radius: 3px;
  background: hsl(var(--accent));
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.rating-bar-fill.fill-success { background: hsl(var(--success)); }
.rating-bar-fill.fill-warning { background: hsl(var(--warning)); }
.rating-bar-value {
  font-size: 0.6875rem;
  font-weight: 600;
  color: hsl(var(--foreground));
  width: 16px;
  text-align: right;
  flex-shrink: 0;
}

/* Notification items */
.notif-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.375rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-fast);
}
.notif-item:hover { background: hsl(var(--muted) / 0.5); }
.notif-item.unread { background: hsl(var(--accent) / 0.03); }
.notif-type-icon {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.notif-type-icon.type-training { background: hsl(var(--accent) / 0.12); color: hsl(var(--accent)); }
.notif-type-icon.type-announcement { background: hsl(var(--primary) / 0.12); color: hsl(var(--primary-light)); }
.notif-type-icon.type-general { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }
.notif-unread-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: hsl(var(--accent));
  flex-shrink: 0;
}

/* Section title */
.section-title-sm {
  font-size: 0.875rem;
  font-weight: 700;
  color: hsl(var(--foreground));
  display: flex;
  align-items: center;
}

/* Empty state */
.empty-state {
  padding: 1.5rem 0;
  text-align: center;
}
</style>
