<template>
  <div>
    <div class="section-header">
      <div><h2 class="section-title">扫码签到</h2><p class="section-desc">扫描二维码或输入签到码完成签到</p></div>
    </div>

    <div class="checkin-container">
      <!-- Status message -->
      <div v-if="checkinResult" class="checkin-result" :class="checkinResult.success ? 'success' : 'error'">
        <div class="result-icon-wrap" :class="checkinResult.success ? 'success' : 'error'">
          <svg v-if="checkinResult.success" class="result-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
          <svg v-else class="result-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>
        </div>
        <p class="result-text">{{ checkinResult.message }}</p>
        <button v-if="checkinResult.success" class="result-dismiss" @click="checkinResult = null">继续签到</button>
      </div>

      <!-- Mode tabs -->
      <div v-if="!checkinResult?.success" class="mode-tabs">
        <button class="mode-tab" :class="{ active: mode === 'scan' }" @click="switchMode('scan')">
          <svg class="mode-tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>
          扫码签到
        </button>
        <button class="mode-tab" :class="{ active: mode === 'manual' }" @click="switchMode('manual')">
          <svg class="mode-tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
          手动输入
        </button>
      </div>

      <!-- Scan mode -->
      <div v-if="mode === 'scan' && !checkinResult?.success" class="scan-section">
        <div class="scan-card">
          <div class="camera-container">
            <video ref="videoEl" class="camera-video" playsinline />
            <div class="scan-overlay">
              <div class="scan-frame">
                <div class="scan-corner tl" /><div class="scan-corner tr" />
                <div class="scan-corner bl" /><div class="scan-corner br" />
                <div class="scan-line" />
              </div>
            </div>
            <div v-if="cameraLoading" class="camera-loading">
              <div class="camera-spinner" />
              <span>正在启动摄像头...</span>
            </div>
            <div v-if="cameraError" class="camera-error">
              <svg class="camera-error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
              <p class="camera-error-title">无法访问摄像头</p>
              <p class="camera-error-desc">{{ cameraError }}</p>
              <button class="camera-retry-btn" @click="startScanner">重试</button>
            </div>
          </div>
          <p class="scan-hint">将二维码放入框内，自动识别</p>
        </div>
      </div>

      <!-- Manual mode -->
      <div v-if="mode === 'manual' && !checkinResult?.success" class="manual-section">
        <div class="manual-card">
          <div class="manual-icon-wrap">
            <svg class="manual-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>
          </div>
          <h3 class="manual-title">输入签到码</h3>
          <p class="manual-desc">请向教练获取签到码，输入后完成签到</p>
          <form @submit.prevent="handleCheckin" class="manual-form">
            <input v-model="token" type="text" placeholder="请输入签到码" class="manual-input" />
            <button type="submit" class="manual-submit" :disabled="loading || !token.trim()">
              {{ loading ? '签到中...' : '确认签到' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import QrScanner from 'qr-scanner'
import { attendanceApi } from '@/api'

const token = ref('')
const loading = ref(false)
const checkinResult = ref<{ success: boolean; message: string } | null>(null)
const mode = ref<'scan' | 'manual'>('scan')
const videoEl = ref<HTMLVideoElement | null>(null)
const cameraLoading = ref(false)
const cameraError = ref('')

let qrScanner: QrScanner | null = null

function switchMode(m: 'scan' | 'manual') {
  mode.value = m
  checkinResult.value = null
  if (m === 'scan') {
    startScanner()
  } else {
    stopScanner()
  }
}

async function startScanner() {
  cameraError.value = ''
  cameraLoading.value = true

  // Wait for video element to be rendered
  await new Promise(r => setTimeout(r, 100))

  if (!videoEl.value) {
    cameraError.value = '视频元素未就绪'
    cameraLoading.value = false
    return
  }

  try {
    const hasCamera = await QrScanner.hasCamera()
    if (!hasCamera) {
      cameraError.value = '未检测到摄像头设备'
      cameraLoading.value = false
      return
    }

    qrScanner = new QrScanner(
      videoEl.value,
      (result) => {
        handleScanResult(result.data)
      },
      {
        preferredCamera: 'environment',
        highlightScanRegion: false,
        highlightCodeOutline: false,
        maxScansPerSecond: 3,
      }
    )

    await qrScanner.start()
    cameraLoading.value = false
  } catch (err) {
    cameraLoading.value = false
    if (err instanceof Error) {
      if (err.name === 'NotAllowedError') {
        cameraError.value = '请允许浏览器访问摄像头'
      } else if (err.name === 'NotFoundError') {
        cameraError.value = '未检测到摄像头设备'
      } else {
        cameraError.value = err.message || '摄像头启动失败'
      }
    } else {
      cameraError.value = '摄像头启动失败，请尝试手动输入'
    }
  }
}

function stopScanner() {
  if (qrScanner) {
    qrScanner.stop()
    qrScanner.destroy()
    qrScanner = null
  }
}

async function handleScanResult(data: string) {
  if (loading.value) return
  stopScanner()

  // Extract token from QR URL or use raw data
  let scannedToken = data
  try {
    const url = new URL(data)
    const t = url.searchParams.get('token')
    if (t) scannedToken = t
  } catch {
    // Not a URL, use raw data as token
  }

  token.value = scannedToken
  await handleCheckin()
}

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
    // Re-enable scanner after failed scan
    if (mode.value === 'scan') {
      setTimeout(() => {
        checkinResult.value = null
        startScanner()
      }, 2000)
    }
  } finally {
    loading.value = false
  }
}

watch(mode, (val) => {
  if (val === 'scan') {
    startScanner()
  }
})

onMounted(() => {
  if (mode.value === 'scan') {
    startScanner()
  }
})

onBeforeUnmount(() => {
  stopScanner()
})
</script>

<style scoped>
.checkin-container {
  max-width: 420px;
  margin: 0 auto;
}

/* Result */
.checkin-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1.5rem;
  border-radius: var(--radius-lg);
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  box-shadow: var(--shadow-card);
  text-align: center;
  margin-bottom: 1rem;
}
.result-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.result-icon-wrap.success { background: hsl(var(--success) / 0.12); color: hsl(var(--success)); }
.result-icon-wrap.error { background: hsl(var(--destructive) / 0.12); color: hsl(var(--destructive)); }
.result-icon { width: 28px; height: 28px; }
.result-text {
  font-size: 1rem;
  font-weight: 600;
  color: hsl(var(--foreground));
  margin-bottom: 1rem;
}
.result-dismiss {
  padding: 0.5rem 1.5rem;
  border-radius: var(--radius-md);
  border: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  color: hsl(var(--foreground));
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}
.result-dismiss:hover {
  background: hsl(var(--accent) / 0.08);
  border-color: hsl(var(--accent) / 0.3);
}

/* Mode tabs */
.mode-tabs {
  display: flex;
  gap: 0.375rem;
  padding: 0.25rem;
  background: hsl(var(--muted) / 0.5);
  border-radius: var(--radius-lg);
  margin-bottom: 1rem;
}
.mode-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--radius-md);
  border: none;
  background: none;
  font-size: 0.8125rem;
  font-weight: 500;
  color: hsl(var(--muted-foreground));
  cursor: pointer;
  transition: all 0.2s ease;
}
.mode-tab.active {
  background: hsl(var(--card));
  color: hsl(var(--accent));
  box-shadow: 0 1px 3px hsl(var(--foreground) / 0.06);
  font-weight: 600;
}
.mode-tab:hover:not(.active) {
  color: hsl(var(--foreground));
}
.mode-tab-icon {
  width: 16px;
  height: 16px;
}

/* Scan section */
.scan-section {
  animation: fade-in 0.2s ease;
}
.scan-card {
  border-radius: var(--radius-lg);
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: hsl(220 20% 8%);
  overflow: hidden;
}
.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Scan overlay */
.scan-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.scan-frame {
  width: 65%;
  aspect-ratio: 1;
  position: relative;
}
.scan-corner {
  position: absolute;
  width: 24px;
  height: 24px;
  border-color: hsl(var(--accent));
  border-style: solid;
  border-width: 0;
}
.scan-corner.tl { top: 0; left: 0; border-top-width: 3px; border-left-width: 3px; border-top-left-radius: 6px; }
.scan-corner.tr { top: 0; right: 0; border-top-width: 3px; border-right-width: 3px; border-top-right-radius: 6px; }
.scan-corner.bl { bottom: 0; left: 0; border-bottom-width: 3px; border-left-width: 3px; border-bottom-left-radius: 6px; }
.scan-corner.br { bottom: 0; right: 0; border-bottom-width: 3px; border-right-width: 3px; border-bottom-right-radius: 6px; }
.scan-line {
  position: absolute;
  left: 4px;
  right: 4px;
  height: 2px;
  background: linear-gradient(90deg, transparent, hsl(var(--accent)), transparent);
  animation: scan-move 2s ease-in-out infinite;
}
@keyframes scan-move {
  0%, 100% { top: 8px; }
  50% { top: calc(100% - 10px); }
}

/* Camera loading/error states */
.camera-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  background: hsl(220 20% 8%);
  color: hsl(210 20% 65%);
  font-size: 0.8125rem;
}
.camera-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid hsl(210 20% 25%);
  border-top-color: hsl(var(--accent));
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.camera-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: hsl(220 20% 8%);
  padding: 1.5rem;
  text-align: center;
}
.camera-error-icon {
  width: 40px;
  height: 40px;
  color: hsl(var(--muted-foreground));
  margin-bottom: 0.25rem;
}
.camera-error-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: hsl(210 20% 80%);
}
.camera-error-desc {
  font-size: 0.75rem;
  color: hsl(210 20% 55%);
  max-width: 260px;
}
.camera-retry-btn {
  margin-top: 0.5rem;
  padding: 0.375rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid hsl(var(--accent) / 0.3);
  background: hsl(var(--accent) / 0.1);
  color: hsl(var(--accent));
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}
.camera-retry-btn:hover {
  background: hsl(var(--accent) / 0.2);
}

.scan-hint {
  text-align: center;
  font-size: 0.75rem;
  color: hsl(var(--muted-foreground));
  padding: 0.75rem;
}

/* Manual section */
.manual-section {
  animation: fade-in 0.2s ease;
}
.manual-card {
  padding: 2rem 1.5rem;
  border-radius: var(--radius-lg);
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  box-shadow: var(--shadow-card);
  text-align: center;
}
.manual-icon-wrap {
  width: 56px;
  height: 56px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  background: hsl(var(--accent) / 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
.manual-icon {
  width: 28px;
  height: 28px;
  color: hsl(var(--accent));
}
.manual-title {
  font-size: 1rem;
  font-weight: 700;
  color: hsl(var(--foreground));
  margin-bottom: 0.375rem;
}
.manual-desc {
  font-size: 0.8125rem;
  color: hsl(var(--muted-foreground));
  margin-bottom: 1.25rem;
}
.manual-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.manual-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  color: hsl(var(--foreground));
  font-size: 1rem;
  text-align: center;
  letter-spacing: 0.1em;
  transition: border-color 0.15s ease;
}
.manual-input:focus {
  outline: none;
  border-color: hsl(var(--accent));
  box-shadow: 0 0 0 3px hsl(var(--accent) / 0.1);
}
.manual-input::placeholder {
  color: hsl(var(--muted-foreground));
  letter-spacing: normal;
}
.manual-submit {
  width: 100%;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: none;
  background: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.manual-submit:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}
.manual-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
