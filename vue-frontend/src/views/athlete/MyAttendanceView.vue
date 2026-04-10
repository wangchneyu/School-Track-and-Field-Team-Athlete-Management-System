<template>
  <div>
    <div class="section-header"><div><h2 class="section-title">我的考勤</h2><p class="section-desc">查看训练出勤记录</p></div></div>

    <!-- Stats summary -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      <div class="stats-card"><div class="stats-value">{{ total }}</div><div class="stats-label">总次数</div></div>
      <div class="stats-card"><div class="stats-value" style="color: hsl(var(--success))">{{ presentCount }}</div><div class="stats-label">出勤</div></div>
      <div class="stats-card"><div class="stats-value" style="color: hsl(var(--warning))">{{ lateCount }}</div><div class="stats-label">迟到</div></div>
      <div class="stats-card"><div class="stats-value" style="color: hsl(var(--destructive))">{{ absentCount }}</div><div class="stats-label">缺勤</div></div>
    </div>

    <div class="card-base overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead><tr><th>日期</th><th>状态</th><th>方式</th><th class="hidden sm:table-cell">备注</th></tr></thead>
          <tbody>
            <tr v-for="a in records" :key="a.id">
              <td class="text-foreground">{{ a.session_date || a.session_id }}</td>
              <td><span :class="statusBadge(a.status)">{{ statusText(a.status) }}</span></td>
              <td class="text-muted-foreground">{{ a.method === 'qr' ? '扫码' : '手动' }}</td>
              <td class="hidden sm:table-cell text-muted-foreground">{{ a.remark || '—' }}</td>
            </tr>
            <tr v-if="!records.length"><td colspan="4" class="text-center text-muted-foreground py-8">暂无考勤记录</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { attendanceApi } from '@/api'
import type { Attendance } from '@/types'

const records = ref<Attendance[]>([])
const total = computed(() => records.value.length)
const presentCount = computed(() => records.value.filter(r => r.status === 'present').length)
const lateCount = computed(() => records.value.filter(r => r.status === 'late').length)
const absentCount = computed(() => records.value.filter(r => r.status === 'absent').length)

function statusBadge(s: string) { return { present: 'badge-success', late: 'badge-warning', absent: 'badge-destructive', leave: 'badge-primary' }[s] || 'badge-primary' }
function statusText(s: string) { return { present: '出勤', late: '迟到', absent: '缺勤', leave: '请假' }[s] || s }

onMounted(async () => {
  try { records.value = (await attendanceApi.getMe()).data || [] } catch { records.value = [] }
})
</script>
