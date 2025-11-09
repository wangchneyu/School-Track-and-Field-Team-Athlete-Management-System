<template>
  <div>
    <!-- Profile card -->
    <div class="card-base p-5 mb-6 animate-fade-in">
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
          <svg class="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0"/></svg>
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="text-lg font-bold text-foreground">{{ profile?.name || '加载中...' }}</h2>
          <p class="text-sm text-muted-foreground">{{ profile?.student_id }} · {{ profile?.group || '未分组' }}</p>
          <div class="flex gap-2 mt-1.5">
            <span class="badge-primary">{{ profile?.gender }}</span>
            <span v-if="profile?.main_event" class="badge-accent">{{ profile.main_event }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="stats-card animate-fade-in" style="animation-delay: 100ms">
        <div class="stats-value text-accent">{{ myScoresCount }}</div>
        <div class="stats-label">成绩记录</div>
      </div>
      <div class="stats-card animate-fade-in" style="animation-delay: 200ms">
        <div class="stats-value" style="color: hsl(var(--success))">{{ attendanceRate }}%</div>
        <div class="stats-label">出勤率</div>
      </div>
      <div class="stats-card animate-fade-in" style="animation-delay: 300ms">
        <div class="stats-value text-primary">{{ ratingsCount }}</div>
        <div class="stats-label">评分次数</div>
      </div>
      <div class="stats-card animate-fade-in" style="animation-delay: 400ms">
        <div class="stats-value" style="color: hsl(var(--warning))">{{ avgRating }}</div>
        <div class="stats-label">平均得分</div>
      </div>
    </div>

    <!-- Recent scores -->
    <div class="card-base p-5 mb-6 animate-fade-in" style="animation-delay: 300ms">
      <div class="section-header mb-4">
        <h3 class="text-base font-bold text-foreground">最近成绩</h3>
        <RouterLink to="/athlete/scores" class="text-xs font-medium text-accent hover:underline">查看全部 →</RouterLink>
      </div>
      <div v-if="recentScores.length" class="space-y-3">
        <div v-for="s in recentScores" :key="s.id" class="flex items-center justify-between py-2 border-b border-border last:border-0">
          <div>
            <p class="text-sm font-medium text-foreground">{{ s.event_name || '项目' + s.event_id }}</p>
            <p class="text-xs text-muted-foreground">{{ s.recorded_at?.slice(0, 10) }}</p>
          </div>
          <span class="text-lg font-bold text-accent">{{ s.performance }}</span>
        </div>
      </div>
      <p v-else class="text-sm text-muted-foreground">暂无成绩记录</p>
    </div>

    <!-- Recent ratings -->
    <div class="card-base p-5 animate-fade-in" style="animation-delay: 400ms">
      <div class="section-header mb-4">
        <h3 class="text-base font-bold text-foreground">最近评分</h3>
        <RouterLink to="/athlete/ratings" class="text-xs font-medium text-accent hover:underline">查看全部 →</RouterLink>
      </div>
      <div v-if="recentRatings.length" class="space-y-3">
        <div v-for="r in recentRatings" :key="r.id" class="py-2 border-b border-border last:border-0">
          <div class="flex items-center justify-between mb-1">
            <p class="text-sm font-medium text-foreground">{{ r.date }}</p>
            <span class="text-sm font-bold text-accent">{{ Math.round((r.attitude + r.attendance + r.performance) / 3) }}分</span>
          </div>
          <div class="flex gap-3">
            <span class="text-xs text-muted-foreground">态度: {{ r.attitude }}</span>
            <span class="text-xs text-muted-foreground">出勤: {{ r.attendance }}</span>
            <span class="text-xs text-muted-foreground">表现: {{ r.performance }}</span>
          </div>
          <p v-if="r.comment" class="text-xs text-muted-foreground mt-1 italic">"{{ r.comment }}"</p>
        </div>
      </div>
      <p v-else class="text-sm text-muted-foreground">暂无评分记录</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { scoreApi, attendanceApi, ratingApi } from '@/api'
import type { Score, Attendance, Rating } from '@/types'

const authStore = useAuthStore()
const profile = computed(() => authStore.athlete)
const myScores = ref<Score[]>([])
const myAttendance = ref<Attendance[]>([])
const myRatings = ref<Rating[]>([])

const myScoresCount = computed(() => myScores.value.length)
const recentScores = computed(() => myScores.value.slice(0, 5))
const recentRatings = computed(() => myRatings.value.slice(0, 3))
const ratingsCount = computed(() => myRatings.value.length)
const avgRating = computed(() => {
  if (!myRatings.value.length) return '—'
  const avg = myRatings.value.reduce((s, r) => s + (r.attitude + r.attendance + r.performance) / 3, 0) / myRatings.value.length
  return Math.round(avg)
})
const attendanceRate = computed(() => {
  if (!myAttendance.value.length) return '—'
  const present = myAttendance.value.filter(a => a.status === 'present' || a.status === 'late').length
  return Math.round((present / myAttendance.value.length) * 100)
})

onMounted(async () => {
  if (!authStore.athlete) await authStore.fetchAthleteProfile()
  const [sRes, aRes, rRes] = await Promise.allSettled([scoreApi.getMe(), attendanceApi.getMe(), ratingApi.getMe()])
  if (sRes.status === 'fulfilled') myScores.value = sRes.value.data || []
  if (aRes.status === 'fulfilled') myAttendance.value = aRes.value.data || []
  if (rRes.status === 'fulfilled') myRatings.value = rRes.value.data || []
})
</script>
