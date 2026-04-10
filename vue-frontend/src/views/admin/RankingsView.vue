<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">排名查看</h2><p class="section-desc">按项目查看运动员排名</p></div>
    </div>

    <div class="flex flex-wrap gap-3 mb-4">
      <select v-model="selectedEvent" class="input-base max-w-[200px]">
        <option value="">选择项目</option>
        <option v-for="e in events" :key="e.id" :value="String(e.id)">{{ e.name }}</option>
      </select>
    </div>

    <div v-if="rankings.length" class="card-base overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead><tr><th>排名</th><th>运动员</th><th>分组</th><th>最佳成绩</th></tr></thead>
          <tbody>
            <tr v-for="r in rankings" :key="r.rank">
              <td>
                <span v-if="r.rank <= 3" :class="['inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold text-accent-foreground', r.rank === 1 ? 'bg-[#FFD700]' : r.rank === 2 ? 'bg-[#C0C0C0]' : 'bg-[#CD7F32]']">
                  {{ r.rank }}
                </span>
                <span v-else class="text-muted-foreground font-medium">{{ r.rank }}</span>
              </td>
              <td class="font-medium">{{ r.name }}</td>
              <td class="text-muted-foreground">{{ r.group || '—' }}</td>
              <td class="font-semibold text-accent">{{ r.best_performance }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else-if="selectedEvent" class="card-base p-8 text-center text-muted-foreground">该项目暂无排名数据</div>
    <div v-else class="card-base p-8 text-center text-muted-foreground">请选择一个项目查看排名</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { rankingApi, eventApi } from '@/api'
import type { Event, Ranking } from '@/types'

const events = ref<Event[]>([])
const rankings = ref<Ranking[]>([])
const selectedEvent = ref('')

async function loadEvents() {
  try { events.value = (await eventApi.list()).data || [] } catch { events.value = [] }
}

async function loadRankings() {
  if (!selectedEvent.value) { rankings.value = []; return }
  try { rankings.value = (await rankingApi.get(Number(selectedEvent.value))).data || [] } catch { rankings.value = [] }
}

watch(selectedEvent, loadRankings)
onMounted(loadEvents)
</script>
