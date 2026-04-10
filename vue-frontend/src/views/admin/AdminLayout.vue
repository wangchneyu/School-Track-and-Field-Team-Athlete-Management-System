<template>
  <div class="admin-layout">
    <!-- Mobile overlay -->
    <div v-if="appStore.sidebarOpen" class="sidebar-overlay lg:hidden" @click="appStore.toggleSidebar" />

    <!-- Sidebar -->
    <aside :class="['admin-sidebar scrollbar-thin', { open: appStore.sidebarOpen }]">
      <div class="sidebar-header">
        <div class="flex items-center gap-2.5">
          <div class="sidebar-logo-icon">
            <svg class="w-5 h-5" viewBox="0 0 40 40" fill="none">
              <path d="M12 28 L18 14 L22 22 L28 12" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="text-sm font-bold" style="color: hsl(210 40% 98%)">Athletics</p>
            <p class="text-[10px] font-medium" style="color: hsl(210 30% 60%)">管理后台</p>
          </div>
        </div>
        <button class="lg:hidden btn-ghost p-1.5 rounded-md" style="color: hsl(210 30% 70%)" @click="appStore.toggleSidebar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <div class="sidebar-section-label">概览</div>
        <RouterLink to="/admin" class="sidebar-link" active-class="active" :class="{ active: $route.path === '/admin' }" @click="closeMobileSidebar">
          <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1"/></svg>
          <span>仪表盘</span>
        </RouterLink>

        <div class="sidebar-section-label">管理</div>
        <RouterLink v-for="item in navItems" :key="item.path" :to="item.path" class="sidebar-link" active-class="active" @click="closeMobileSidebar">
          <component :is="item.icon" />
          <span class="flex-1">{{ item.label }}</span>
          <span v-if="item.badge && unreadCount > 0" class="sidebar-notif-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <button class="sidebar-link w-full" @click="appStore.openSettings">
          <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          <span>个人设置</span>
        </button>
      </div>
    </aside>

    <!-- Main content area -->
    <div class="admin-main">
      <!-- Top bar -->
      <header class="admin-topbar">
        <button class="lg:hidden btn-ghost p-2 rounded-md" @click="appStore.toggleSidebar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <div class="flex-1" />
        <div class="flex items-center gap-2">
          <!-- Notification bell -->
          <RouterLink to="/admin/notifications" class="btn-ghost p-2 rounded-md relative">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
            <span v-if="unreadCount > 0" class="topbar-notif-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
          </RouterLink>
          <button class="btn-ghost p-2 rounded-md relative" @click="appStore.openSettings">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          </button>
        </div>
      </header>

      <!-- Page content -->
      <main class="admin-content scrollbar-thin">
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
import { h, ref, onMounted } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { notificationApi } from '@/api'

const appStore = useAppStore()
const route = useRoute()
const unreadCount = ref(0)

function closeMobileSidebar() {
  if (window.innerWidth < 1024) appStore.sidebarOpen = false
}

async function fetchUnreadCount() {
  try {
    const res = await notificationApi.getUnreadCount()
    unreadCount.value = res.data?.unread_count || 0
  } catch { /* ignore */ }
}

// SVG icon components
const IconUsers = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>' })
const IconCalendar = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>' })
const IconClipboard = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>' })
const IconChart = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>' })
const IconTrophy = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 3h14l-1.5 6H6.5L5 3zM12 9v6m-3 0h6m-6 3h6M8 21h8"/>' })
const IconFlag = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2z"/>' })
const IconStar = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>' })
const IconBook = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>' })
const IconBell = () => h('svg', { class: 'w-[18px] h-[18px]', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', innerHTML: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>' })

const navItems = [
  { path: '/admin/athletes', label: '运动员管理', icon: IconUsers, badge: false },
  { path: '/admin/training', label: '训练管理', icon: IconCalendar, badge: false },
  { path: '/admin/attendance', label: '考勤管理', icon: IconClipboard, badge: false },
  { path: '/admin/scores', label: '成绩录入', icon: IconChart, badge: false },
  { path: '/admin/rankings', label: '排名查看', icon: IconTrophy, badge: false },
  { path: '/admin/events', label: '项目管理', icon: IconFlag, badge: false },
  { path: '/admin/ratings', label: '评分管理', icon: IconStar, badge: false },
  { path: '/admin/content', label: '训练内容', icon: IconBook, badge: false },
  { path: '/admin/notifications', label: '通知管理', icon: IconBell, badge: true },
]

onMounted(() => {
  fetchUnreadCount()
  setInterval(fetchUnreadCount, 60000)
})

void route
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: hsl(var(--background));
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: hsl(220 65% 10% / 0.5);
  backdrop-filter: blur(2px);
}

.admin-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  background: hsl(var(--sidebar));
  z-index: 50;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
}

@media (max-width: 1023px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }
  .admin-sidebar.open {
    transform: translateX(0);
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid hsl(0 0% 100% / 0.06);
}

.sidebar-logo-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: hsl(var(--accent) / 0.15);
  color: hsl(var(--accent));
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem;
}

.sidebar-section-label {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: hsl(210 20% 45%);
  padding: 0.75rem 0.75rem 0.375rem;
}

.sidebar-footer {
  padding: 0.75rem;
  border-top: 1px solid hsl(0 0% 100% / 0.06);
}

.sidebar-notif-badge {
  font-size: 0.6rem;
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

.admin-main {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

@media (max-width: 1023px) {
  .admin-main {
    margin-left: 0;
  }
}

.admin-topbar {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  position: sticky;
  top: 0;
  z-index: 30;
}

.topbar-notif-badge {
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

.admin-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

@media (max-width: 640px) {
  .admin-content {
    padding: 1rem;
  }
}

/* Page transition */
.page-enter-active {
  animation: fade-in 0.25s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
.page-leave-active {
  animation: fade-in 0.15s cubic-bezier(0.4, 0, 0.2, 1) reverse forwards;
}
</style>
