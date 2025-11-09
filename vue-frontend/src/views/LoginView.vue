<template>
  <div class="login-page">
    <!-- Animated background -->
    <canvas ref="canvasRef" class="login-canvas" />
    <div class="login-overlay" />

    <!-- Content -->
    <div class="login-container">
      <!-- Left: branding -->
      <div class="login-branding animate-fade-in">
        <div class="login-logo">
          <svg class="w-10 h-10" viewBox="0 0 40 40" fill="none">
            <circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="2" opacity="0.3"/>
            <path d="M12 28 L18 14 L22 22 L28 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="login-logo-text">Athletics</span>
        </div>
        <h1 class="login-heading">
          校田径队<br/>
          <span class="gradient-text">管理系统</span>
        </h1>
        <p class="login-subtitle">训练 · 考勤 · 成绩 · 一站式管理</p>
      </div>

      <!-- Right: form -->
      <div class="login-card animate-slide-up animation-delay-200">
        <h2 class="text-xl font-bold text-foreground mb-1">欢迎登录</h2>
        <p class="text-sm text-muted-foreground mb-6">请输入您的账号和密码</p>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="text-sm font-medium text-foreground mb-1.5 block">用户名</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名或学号"
              class="input-base"
              autocomplete="username"
            />
          </div>

          <div>
            <label class="text-sm font-medium text-foreground mb-1.5 block">密码</label>
            <input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              class="input-base"
              autocomplete="current-password"
            />
          </div>

          <button
            type="submit"
            class="btn-primary w-full text-sm flex items-center justify-center gap-2"
            :disabled="loading"
          >
            <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>

        <p v-if="error" class="text-sm text-destructive mt-3 text-center">{{ error }}</p>

        <!-- Countdown -->
        <div v-if="featuredEvent" class="mt-6 pt-5 border-t border-border">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span class="text-xs font-semibold text-accent uppercase tracking-wider">即将来临</span>
          </div>
          <p class="text-sm font-semibold text-foreground">{{ featuredEvent.name }}</p>
          <p class="text-xs text-muted-foreground mt-0.5">{{ featuredEvent.location }}</p>
          <div class="flex gap-2 mt-3">
            <div class="countdown-block">
              <span class="countdown-num">{{ countdown.days }}</span>
              <span class="countdown-label">天</span>
            </div>
            <div class="countdown-block">
              <span class="countdown-num">{{ countdown.hours }}</span>
              <span class="countdown-label">时</span>
            </div>
            <div class="countdown-block">
              <span class="countdown-num">{{ countdown.mins }}</span>
              <span class="countdown-label">分</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { featuredEventApi } from '@/api'
import type { FeaturedEvent } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const canvasRef = ref<HTMLCanvasElement | null>(null)
const featuredEvent = ref<FeaturedEvent | null>(null)
const countdown = reactive({ days: '00', hours: '00', mins: '00' })

let animationId = 0
let countdownTimer = 0

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const data = await authStore.login(username.value, password.value)
    router.push(data.role === 'admin' ? '/admin' : '/athlete')
  } catch {
    error.value = '用户名或密码错误'
  } finally {
    loading.value = false
  }
}

// ---- Featured event countdown ----
async function loadFeaturedEvent() {
  try {
    const res = await featuredEventApi.get()
    featuredEvent.value = res.data
    startCountdown()
  } catch {
    // no featured event
  }
}

function startCountdown() {
  function tick() {
    if (!featuredEvent.value?.start_time) return
    const diff = new Date(featuredEvent.value.start_time).getTime() - Date.now()
    if (diff <= 0) {
      countdown.days = '00'
      countdown.hours = '00'
      countdown.mins = '00'
      return
    }
    const d = Math.floor(diff / 86400000)
    const h = Math.floor((diff % 86400000) / 3600000)
    const m = Math.floor((diff % 3600000) / 60000)
    countdown.days = String(d).padStart(2, '0')
    countdown.hours = String(h).padStart(2, '0')
    countdown.mins = String(m).padStart(2, '0')
  }
  tick()
  countdownTimer = window.setInterval(tick, 60000)
}

// ---- Particle canvas animation ----
function initCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  let w = (canvas.width = window.innerWidth)
  let h = (canvas.height = window.innerHeight)

  interface Particle {
    x: number; y: number; vx: number; vy: number; r: number; a: number
  }

  const particles: Particle[] = []
  const count = Math.min(80, Math.floor((w * h) / 15000))

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      r: Math.random() * 2 + 1,
      a: Math.random() * 0.5 + 0.2,
    })
  }

  function draw() {
    ctx!.clearRect(0, 0, w, h)

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]
      p.x += p.vx
      p.y += p.vy
      if (p.x < 0 || p.x > w) p.vx *= -1
      if (p.y < 0 || p.y > h) p.vy *= -1

      ctx!.beginPath()
      ctx!.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx!.fillStyle = `rgba(249, 115, 22, ${p.a})`
      ctx!.fill()

      // Connect nearby particles
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j]
        const dx = p.x - p2.x
        const dy = p.y - p2.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 150) {
          ctx!.beginPath()
          ctx!.moveTo(p.x, p.y)
          ctx!.lineTo(p2.x, p2.y)
          ctx!.strokeStyle = `rgba(249, 115, 22, ${0.1 * (1 - dist / 150)})`
          ctx!.lineWidth = 0.5
          ctx!.stroke()
        }
      }
    }
    animationId = requestAnimationFrame(draw)
  }

  const handleResize = () => {
    w = canvas.width = window.innerWidth
    h = canvas.height = window.innerHeight
  }
  window.addEventListener('resize', handleResize)
  draw()
}

onMounted(() => {
  initCanvas()
  loadFeaturedEvent()
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  clearInterval(countdownTimer)
})
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: var(--gradient-hero);
}

.login-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.login-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  background:
    radial-gradient(ellipse at 30% 50%, hsl(24 95% 53% / 0.08) 0%, transparent 60%),
    radial-gradient(ellipse at 70% 30%, hsl(220 65% 30% / 0.15) 0%, transparent 50%);
}

.login-container {
  position: relative;
  z-index: 3;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4rem;
  padding: 2rem;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    gap: 2rem;
    padding: 2rem 1.5rem;
  }
}

.login-branding {
  color: hsl(var(--primary-foreground));
  max-width: 320px;
}

.login-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: hsl(var(--accent));
  margin-bottom: 1.5rem;
}

.login-logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.login-heading {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1.15;
  color: hsl(210 40% 98%);
}

@media (max-width: 768px) {
  .login-heading {
    font-size: 1.75rem;
  }
}

.login-subtitle {
  margin-top: 1rem;
  color: hsl(210 30% 70%);
  font-size: 0.95rem;
  letter-spacing: 0.1em;
}

.countdown-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  background: hsl(var(--accent) / 0.08);
  min-width: 3rem;
}

.countdown-num {
  font-size: 1.25rem;
  font-weight: 700;
  color: hsl(var(--accent));
  font-variant-numeric: tabular-nums;
}

.countdown-label {
  font-size: 0.65rem;
  color: hsl(var(--muted-foreground));
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
