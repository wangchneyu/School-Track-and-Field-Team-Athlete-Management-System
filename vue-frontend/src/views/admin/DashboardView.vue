<template>
  <div>
    <!-- Hero banner / photo carousel -->
    <div class="hero-carousel card-base overflow-hidden mb-6">
      <div class="hero-slides" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
        <div v-for="(img, i) in slides" :key="i" class="hero-slide">
          <img :src="img.src" :alt="img.alt" class="hero-img" />
          <div class="hero-caption">
            <span class="badge-accent">{{ img.tag }}</span>
            <h3 class="hero-caption-title">{{ img.title }}</h3>
          </div>
        </div>
      </div>
      <!-- Dots -->
      <div class="hero-dots">
        <button v-for="(_, i) in slides" :key="i" :class="['hero-dot', { active: i === currentSlide }]" @click="currentSlide = i" />
      </div>
      <!-- Arrows -->
      <button class="hero-arrow hero-arrow-left" @click="prevSlide">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <button class="hero-arrow hero-arrow-right" @click="nextSlide">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      </button>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="stat in statsCards" :key="stat.label" class="stats-card animate-fade-in" :style="{ animationDelay: stat.delay }">
        <div class="flex items-center gap-3">
          <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', stat.iconBg]">
            <span v-html="stat.icon" />
          </div>
          <div>
            <div class="stats-value">{{ stat.value }}</div>
            <div class="stats-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured event + quick actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <!-- Featured event -->
      <div class="lg:col-span-2 card-base p-5">
        <div class="section-header mb-4">
          <h3 class="text-base font-bold text-foreground">近期重要赛事</h3>
          <RouterLink to="/admin/events" class="text-xs font-medium text-accent hover:underline">管理赛事 →</RouterLink>
        </div>
        <div v-if="featured" class="flex items-start gap-4">
          <div class="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-foreground">{{ featured.name }}</p>
            <p class="text-sm text-muted-foreground mt-0.5">{{ featured.location }}</p>
            <p class="text-xs text-muted-foreground mt-1">{{ featured.description }}</p>
            <div v-if="featured.countdown_days != null" class="mt-3 badge-accent">
              距离开赛还有 {{ Math.ceil(featured.countdown_days) }} 天
            </div>
          </div>
        </div>
        <p v-else class="text-sm text-muted-foreground">暂无近期赛事</p>
      </div>

      <!-- Quick actions -->
      <div class="card-base p-5">
        <h3 class="text-base font-bold text-foreground mb-4">快捷操作</h3>
        <div class="space-y-2">
          <RouterLink v-for="action in quickActions" :key="action.path" :to="action.path" class="flex items-center gap-3 p-2.5 rounded-md hover:bg-muted transition-colors">
            <div :class="['w-8 h-8 rounded-md flex items-center justify-center text-accent-foreground', action.bg]">
              <span v-html="action.icon" />
            </div>
            <span class="text-sm font-medium text-foreground">{{ action.label }}</span>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Attendance stats -->
    <div class="card-base p-5">
      <div class="section-header mb-4">
        <h3 class="text-base font-bold text-foreground">出勤率概览</h3>
        <RouterLink to="/admin/attendance" class="text-xs font-medium text-accent hover:underline">详细数据 →</RouterLink>
      </div>
      <div v-if="attendanceStats.length" class="space-y-3">
        <div v-for="stat in attendanceStats.slice(0, 8)" :key="stat.athlete_id" class="flex items-center gap-3">
          <span class="text-sm font-medium text-foreground w-20 truncate">{{ stat.name }}</span>
          <div class="flex-1 h-2 bg-muted rounded-full overflow-hidden">
            <div class="h-full rounded-full transition-all duration-500" :style="{ width: stat.rate + '%', background: stat.rate >= 80 ? 'hsl(var(--success))' : stat.rate >= 60 ? 'hsl(var(--warning))' : 'hsl(var(--destructive))' }" />
          </div>
          <span class="text-xs font-semibold text-muted-foreground w-12 text-right">{{ stat.rate }}%</span>
        </div>
      </div>
      <p v-else class="text-sm text-muted-foreground">暂无出勤数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { featuredEventApi, statsApi, athleteApi, sessionApi } from '@/api'
import type { FeaturedEvent } from '@/types'

const currentSlide = ref(0)
let slideTimer = 0

const slides = [
  { src: '/images/hero-banner.png', alt: '田径队训练', tag: '精彩瞬间', title: '日常训练风采' },
  { src: '/images/activity-1.png', alt: '跳高训练', tag: '专项训练', title: '跳高技术提升训练' },
  { src: '/images/activity-2.png', alt: '接力赛', tag: '团队协作', title: '接力队配合训练' },
  { src: '/images/activity-3.png', alt: '团队合影', tag: '团队风采', title: '赛后团队合影' },
]

function nextSlide() { currentSlide.value = (currentSlide.value + 1) % slides.length }
function prevSlide() { currentSlide.value = (currentSlide.value - 1 + slides.length) % slides.length }

const athleteCount = ref(0)
const sessionCount = ref(0)
const featured = ref<FeaturedEvent | null>(null)
const attendanceStats = ref<Array<{ athlete_id: number; name: string; rate: number }>>([])

const statsCards = ref([
  { label: '运动员', value: '—', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>', iconBg: 'bg-primary/10 text-primary', delay: '0ms' },
  { label: '训练课次', value: '—', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>', iconBg: 'bg-accent/10 text-accent', delay: '100ms' },
  { label: '平均出勤率', value: '—', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>', iconBg: 'bg-success/10 text-success', delay: '200ms' },
  { label: '距比赛', value: '—', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>', iconBg: 'bg-warning/10 text-warning', delay: '300ms' },
])

const quickActions = [
  { path: '/admin/athletes', label: '添加运动员', bg: 'bg-primary', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6"/></svg>' },
  { path: '/admin/training', label: '安排训练', bg: 'bg-accent', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>' },
  { path: '/admin/scores', label: '录入成绩', bg: 'bg-success', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6m6 0V9a2 2 0 012-2h2a2 2 0 012 2v10"/></svg>' },
  { path: '/admin/attendance', label: '考勤管理', bg: 'bg-warning', icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2"/></svg>' },
]

async function loadDashboard() {
  try {
    const [athleteRes, sessionRes, featuredRes, statsRes] = await Promise.allSettled([
      athleteApi.list(),
      sessionApi.list(),
      featuredEventApi.get(),
      statsApi.attendance(),
    ])

    if (athleteRes.status === 'fulfilled') {
      const list = athleteRes.value.data
      athleteCount.value = Array.isArray(list) ? list.length : 0
      statsCards.value[0].value = String(athleteCount.value)
    }
    if (sessionRes.status === 'fulfilled') {
      const list = sessionRes.value.data
      sessionCount.value = Array.isArray(list) ? list.length : 0
      statsCards.value[1].value = String(sessionCount.value)
    }
    if (featuredRes.status === 'fulfilled' && featuredRes.value.data) {
      featured.value = featuredRes.value.data
      if (featured.value?.countdown_days != null) {
        statsCards.value[3].value = Math.ceil(featured.value.countdown_days) + '天'
      }
    }
    if (statsRes.status === 'fulfilled') {
      const data = statsRes.value.data
      if (Array.isArray(data)) {
        attendanceStats.value = data
        const avg = data.length > 0 ? Math.round(data.reduce((s: number, a: { rate: number }) => s + a.rate, 0) / data.length) : 0
        statsCards.value[2].value = avg + '%'
      }
    }
  } catch {
    // dashboard load errors are non-critical
  }
}

onMounted(() => {
  loadDashboard()
  slideTimer = window.setInterval(nextSlide, 5000)
})

onUnmounted(() => {
  clearInterval(slideTimer)
})
</script>

<style scoped>
.hero-carousel {
  position: relative;
  height: 220px;
  border-radius: var(--radius-lg);
}
@media (min-width: 768px) {
  .hero-carousel { height: 280px; }
}

.hero-slides {
  display: flex;
  height: 100%;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.hero-slide {
  min-width: 100%;
  position: relative;
}

.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1.25rem;
  background: linear-gradient(0deg, hsl(220 65% 10% / 0.7) 0%, transparent 100%);
}

.hero-caption-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: hsl(210 40% 98%);
  margin-top: 0.375rem;
}

.hero-dots {
  position: absolute;
  bottom: 0.75rem;
  right: 1rem;
  display: flex;
  gap: 0.375rem;
}

.hero-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: hsl(0 0% 100% / 0.4);
  transition: var(--transition-fast);
}
.hero-dot.active {
  width: 18px;
  border-radius: 3px;
  background: hsl(var(--accent));
}

.hero-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: hsl(0 0% 100% / 0.2);
  backdrop-filter: blur(4px);
  color: hsl(210 40% 98%);
  transition: var(--transition-fast);
  opacity: 0;
}
.hero-carousel:hover .hero-arrow {
  opacity: 1;
}
.hero-arrow:hover {
  background: hsl(0 0% 100% / 0.35);
}
.hero-arrow-left { left: 0.75rem; }
.hero-arrow-right { right: 0.75rem; }
</style>
