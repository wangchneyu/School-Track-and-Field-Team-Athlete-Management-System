<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">扫码签到</h2><p class="section-desc">扫描或输入签到码完成签到</p></div>
    </div>

    <div class="max-w-md mx-auto">
      <!-- Status message -->
      <div v-if="checkinResult" :class="['mb-4 p-4 rounded-lg text-sm font-medium', checkinResult.success ? 'bg-success/10 text-success' : 'bg-destructive/10 text-destructive']">
        {{ checkinResult.message }}
      </div>

      <!-- Manual token input -->
      <div class="card-base p-6">
        <div class="w-16 h-16 mx-auto rounded-full bg-accent/10 flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>
        </div>
        <h3 class="text-center font-semibold text-foreground mb-4">输入签到码</h3>
        <p class="text-center text-sm text-muted-foreground mb-4">请向教练获取签到码，输入后完成签到</p>
        <form @submit.prevent="handleCheckin" class="space-y-3">
          <input v-model="token" type="text" placeholder="请输入签到码" class="input-base text-center text-lg tracking-wider" />
          <button type="submit" class="btn-primary w-full" :disabled="loading || !token.trim()">
            {{ loading ? '签到中...' : '确认签到' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { attendanceApi } from '@/api'

const token = ref('')
const loading = ref(false)
const checkinResult = ref<{ success: boolean; message: string } | null>(null)

async function handleCheckin() {
  if (!token.value.trim()) return
  loading.value = true
  checkinResult.value = null
  try {
    await attendanceApi.qrCheckin({ token: token.value.trim() })
    checkinResult.value = { success: true, message: '签到成功！' }
    token.value = ''
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '签到失败，请检查签到码'
    checkinResult.value = { success: false, message: msg }
  } finally {
    loading.value = false
  }
}
</script>
