<template>
  <div class="athlete-layout">
    <!-- Mobile bottom nav -->
    <nav class="athlete-bottom-nav">
      <RouterLink v-for="item in navItems" :key="item.path" :to="item.path" class="athlete-nav-item" active-class="active" :class="{ active: item.exact ? $route.path === item.path : $route.path.startsWith(item.path) }">
        <div class="nav-icon-wrap">
          <span v-html="item.icon" />
          <span v-if="item.badge && unreadCount > 0" class="nav-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </div>
        <span class="nav-label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <!-- Desktop sidebar -->
    <aside class="athlete-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-brand">
          <div class="sidebar-logo-icon">
            <svg class="sidebar-logo-svg" viewBox="0 0 40 40" fill="none">
              <path d="M12 28 L18 14 L22 22 L28 12" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="sidebar-brand-title">Athletics</p>
            <p class="sidebar-brand-sub">运动员中心</p>
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <RouterLink v-for="item in sideItems" :key="item.path" :to="item.path" class="sidebar-link" active-class="active" :class="{ active: item.exact ? $route.path === item.path : false }">
          <span v-html="item.icon" />
          <span class="sidebar-link-text">{{ item.label }}</span>
          <span v-if="item.badge && unreadCount > 0" class="sidebar-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <button class="sidebar-link sidebar-link-full" @click="appStore.openSettings">
          <svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          <span>个人设置</span>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="athlete-main">
      <!-- Mobile top bar -->
      <header class="athlete-topbar">
        <div class="topbar-left">
          <div class="topbar-logo-wrap">
            <svg class="topbar-logo-svg" viewBox="0 0 40 40" fill="none"><path d="M12 28 L18 14 L22 22 L28 12" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <span class="topbar-title">Athletics</span>
        </div>
        <div class="topbar-right">
          <RouterLink to="/athlete/notifications" class="topbar-btn">
            <svg class="topbar-action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
            <span v-if="unreadCount > 0" class="topbar-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
          </RouterLink>
          <button class="topbar-btn" @click="appStore.openSettings">
            <svg class="topbar-action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          </button>
        </div>
      </header>

      <main class="athlete-content scrollbar-thin">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { notificationApi } from '@/api'

const appStore = useAppStore()
const authStore = useAuthStore()
const route = useRoute()
const unreadCount = ref(0)

const iconHome = '<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1"/></svg>'
const iconChart = '<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>'
const iconClip = '<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>'
const iconBell = '<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>'
const iconQR = '<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>'
const iconStar = '<svg class="sidebar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>'

const navItems = [
  { path: '/athlete', label: '首页', icon: iconHome, exact: true, badge: false },
  { path: '/athlete/scores', label: '成绩', icon: iconChart, exact: false, badge: false },
  { path: '/athlete/notifications', label: '通知', icon: iconBell, exact: false, badge: true },
  { path: '/athlete/attendance', label: '考勤', icon: iconClip, exact: false, badge: false },
  { path: '/athlete/checkin', label: '签到', icon: iconQR, exact: false, badge: false },
]

const sideItems = [
  { path: '/athlete', label: '我的主页', icon: iconHome, exact: true, badge: false },
  { path: '/athlete/scores', label: '我的成绩', icon: iconChart, exact: false, badge: false },
  { path: '/athlete/attendance', label: '我的考勤', icon: iconClip, exact: false, badge: false },
  { path: '/athlete/ratings', label: '我的评分', icon: iconStar, exact: false, badge: false },
  { path: '/athlete/notifications', label: '通知中心', icon: iconBell, exact: false, badge: true },
  { path: '/athlete/checkin', label: '扫码签到', icon: iconQR, exact: false, badge: false },
]

async function fetchUnreadCount() {
  try {
    const res = await notificationApi.getUnreadCount()
    unreadCount.value = res.data?.unread_count || 0
  } catch { /* ignore */ }
}

onMounted(() => {
  if (authStore.isAthlete && !authStore.athlete) {
    authStore.fetchAthleteProfile()
  }
  fetchUnreadCount()
  setInterval(fetchUnreadCount, 60000)
})

void route
</script>

<style scoped>
/* ===== Layout shell ===== */
.athlete-layout {
  display: flex;
  min-height: 100vh;
  background: hsl(var(--background));
}

/* ===== Sidebar (desktop only) ===== */
.athlete-sidebar {
  display: none;              /* hidden on mobile */
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 220px;
  background: hsl(var(--sidebar));
  z-index: 40;
  flex-direction: column;
}
@media (min-width: 640px) {
  .athlete-sidebar {
    display: flex;            /* show on desktop */
  }
}

.sidebar-header {
  padding: 1.25rem 1rem;
  border-bottom: 1px solid hsl(var(--border) / 0.15);
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}
.sidebar-logo-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: hsl(var(--accent) / 0.15);
  color: hsl(var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.sidebar-logo-svg {
  width: 20px;
  height: 20px;
}
.sidebar-brand-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: hsl(210 40% 98%);
}
.sidebar-brand-sub {
  font-size: 0.625rem;
  font-weight: 500;
  color: hsl(210 30% 60%);
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  font-weight: 500;
  color: hsl(var(--muted-foreground));
  transition: all 0.15s ease;
  cursor: pointer;
  border: none;
  background: none;
  text-align: left;
  text-decoration: none;
}
.sidebar-link:hover {
  background: hsl(var(--accent) / 0.08);
  color: hsl(var(--foreground));
}
.sidebar-link.active {
  background: hsl(var(--accent) / 0.12);
  color: hsl(var(--accent));
  font-weight: 600;
}
.sidebar-link-full {
  width: 100%;
}
.sidebar-link-text {
  flex: 1;
}

.sidebar-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 0.5rem;
  border-top: 1px solid hsl(var(--border) / 0.15);
}

.sidebar-badge {
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0 0.375rem;
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  border-radius: 99px;
  background: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
}

/* ===== Main content area ===== */
.athlete-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
@media (min-width: 640px) {
  .athlete-main {
    margin-left: 220px;
  }
}

/* ===== Top bar (mobile only) ===== */
.athlete-topbar {
  display: flex;              /* visible on mobile */
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  position: sticky;
  top: 0;
  z-index: 30;
}
@media (min-width: 640px) {
  .athlete-topbar {
    display: none;            /* hidden on desktop */
  }
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.topbar-logo-wrap {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: hsl(var(--accent) / 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
.topbar-logo-svg {
  width: 16px;
  height: 16px;
  color: hsl(var(--accent));
}
.topbar-title {
  font-weight: 700;
  font-size: 0.875rem;
  color: hsl(var(--foreground));
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.topbar-btn {
  position: relative;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  color: hsl(var(--muted-foreground));
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  text-decoration: none;
}
.topbar-btn:hover {
  background: hsl(var(--muted) / 0.5);
  color: hsl(var(--foreground));
}
.topbar-action-icon {
  width: 20px;
  height: 20px;
}
.topbar-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 0.5625rem;
  font-weight: 700;
  padding: 0 0.25rem;
  min-width: 14px;
  height: 14px;
  line-height: 14px;
  text-align: center;
  border-radius: 99px;
  background: hsl(var(--destructive));
  color: white;
}

/* ===== Content area ===== */
.athlete-content {
  flex: 1;
  padding: 1rem;
  padding-bottom: 5rem;
  overflow-y: auto;
}
@media (min-width: 640px) {
  .athlete-content {
    padding: 1.5rem;
    padding-bottom: 1.5rem;
  }
}

/* ===== Bottom nav (mobile only) ===== */
.athlete-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;              /* visible on mobile */
  justify-content: space-around;
  padding: 0.5rem 0 calc(0.5rem + env(safe-area-inset-bottom, 0px));
  background: hsl(var(--card));
  border-top: 1px solid hsl(var(--border));
  backdrop-filter: blur(12px);
}
@media (min-width: 640px) {
  .athlete-bottom-nav {
    display: none;            /* hidden on desktop */
  }
}

.athlete-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.25rem 0.5rem;
  color: hsl(var(--muted-foreground));
  transition: color 0.15s ease;
  border-radius: var(--radius-sm);
  text-decoration: none;
}
.athlete-nav-item.active {
  color: hsl(var(--accent));
}
.nav-label {
  font-size: 0.625rem;
  margin-top: 0.125rem;
}

.nav-icon-wrap {
  position: relative;
  display: inline-flex;
}
.nav-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  font-size: 0.5625rem;
  font-weight: 700;
  padding: 0 0.25rem;
  min-width: 14px;
  height: 14px;
  line-height: 14px;
  text-align: center;
  border-radius: 99px;
  background: hsl(var(--destructive));
  color: white;
}

/* ===== Page transitions ===== */
.page-enter-active { animation: fade-in 0.25s cubic-bezier(0.4, 0, 0.2, 1) forwards; }
.page-leave-active { animation: fade-in 0.15s cubic-bezier(0.4, 0, 0.2, 1) reverse forwards; }
</style>
