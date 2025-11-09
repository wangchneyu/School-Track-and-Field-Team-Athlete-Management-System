<template>
  <div>
    <div class="section-header"><div><h2 class="section-title">我的评分</h2><p class="section-desc">查看教练评分和反馈</p></div></div>

    <div class="space-y-4">
      <div v-for="r in ratings" :key="r.id" class="card-base p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm font-medium text-foreground">{{ r.date }}</span>
          <span class="text-lg font-bold text-accent">{{ Math.round((r.attitude + r.attendance + r.performance) / 3) }}分</span>
        </div>
        <!-- Score bars -->
        <div class="space-y-2">
          <div v-for="item in [{ label: '训练态度', val: r.attitude }, { label: '出勤情况', val: r.attendance }, { label: '训练表现', val: r.performance }]" :key="item.label" class="flex items-center gap-3">
            <span class="text-xs text-muted-foreground w-16">{{ item.label }}</span>
            <div class="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500" :style="{ width: item.val + '%', background: item.val >= 80 ? 'hsl(var(--success))' : item.val >= 60 ? 'hsl(var(--warning))' : 'hsl(var(--destructive))' }" />
            </div>
            <span class="text-xs font-semibold text-muted-foreground w-8 text-right">{{ item.val }}</span>
          </div>
        </div>
        <p v-if="r.comment" class="text-sm text-muted-foreground mt-3 pt-3 border-t border-border italic">"{{ r.comment }}"</p>
      </div>
      <div v-if="!ratings.length" class="card-base p-8 text-center text-muted-foreground">暂无评分记录</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ratingApi } from '@/api'
import type { Rating } from '@/types'

const ratings = ref<Rating[]>([])

onMounted(async () => {
  try { ratings.value = (await ratingApi.getMe()).data || [] } catch { ratings.value = [] }
})
</script>
