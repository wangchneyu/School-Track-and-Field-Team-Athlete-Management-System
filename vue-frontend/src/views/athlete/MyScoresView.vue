<template>
  <div>
    <div class="section-header"><div><h2 class="section-title">我的成绩</h2><p class="section-desc">查看所有比赛和训练成绩</p></div></div>
    <div class="card-base overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead><tr><th>项目</th><th>成绩</th><th>类型</th><th class="hidden sm:table-cell">备注</th><th>日期</th></tr></thead>
          <tbody>
            <tr v-for="s in scores" :key="s.id">
              <td class="font-medium">{{ s.event_name || s.event_id }}</td>
              <td class="font-bold text-accent">{{ s.performance }}</td>
              <td><span :class="s.is_official ? 'badge-success' : 'badge-primary'">{{ s.is_official ? '正式' : '训练' }}</span></td>
              <td class="hidden sm:table-cell text-muted-foreground">{{ s.remark || '—' }}</td>
              <td class="text-muted-foreground text-xs">{{ s.recorded_at?.slice(0, 10) }}</td>
            </tr>
            <tr v-if="!scores.length"><td colspan="5" class="text-center text-muted-foreground py-8">暂无成绩记录</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { scoreApi } from '@/api'
import type { Score } from '@/types'

const scores = ref<Score[]>([])

onMounted(async () => {
  try { scores.value = (await scoreApi.getMe()).data || [] } catch { scores.value = [] }
})
</script>
