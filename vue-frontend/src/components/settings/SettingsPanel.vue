<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-bold text-foreground">个人设置</h2>
          <button class="btn-ghost p-2 rounded-md" @click="$emit('close')">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="space-y-6">
          <!-- Profile section -->
          <div class="flex items-center gap-4 pb-6 border-b border-border">
            <div class="w-14 h-14 rounded-full bg-accent/10 flex items-center justify-center">
              <svg class="w-7 h-7 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0"/>
              </svg>
            </div>
            <div>
              <p class="font-semibold text-foreground">{{ isAdmin ? '管理员' : athleteName }}</p>
              <p class="text-sm text-muted-foreground">{{ role === 'admin' ? '系统管理员' : '运动员' }}</p>
            </div>
          </div>

          <!-- Change password -->
          <div>
            <h3 class="text-sm font-semibold text-foreground mb-3">修改密码</h3>
            <div class="space-y-3">
              <input
                v-model="oldPassword"
                type="password"
                placeholder="当前密码"
                class="input-base"
              />
              <input
                v-model="newPassword"
                type="password"
                placeholder="新密码"
                class="input-base"
              />
              <input
                v-model="confirmPassword"
                type="password"
                placeholder="确认新密码"
                class="input-base"
              />
              <button
                class="btn-primary w-full text-sm"
                :disabled="saving"
                @click="changePassword"
              >
                {{ saving ? '保存中...' : '修改密码' }}
              </button>
            </div>
          </div>

          <!-- Logout -->
          <div class="pt-4 border-t border-border">
            <button class="w-full py-2.5 text-sm font-medium text-destructive rounded-md hover:bg-destructive/5 transition-colors" @click="handleLogout">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { authApi } from '@/api'

defineEmits(['close'])

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const saving = ref(false)

const role = computed(() => authStore.role)
const isAdmin = computed(() => authStore.isAdmin)
const athleteName = computed(() => authStore.athlete?.name || '运动员')

async function changePassword() {
  if (!oldPassword.value || !newPassword.value) {
    appStore.showToast('请填写完整', 'error')
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    appStore.showToast('两次密码不一致', 'error')
    return
  }
  saving.value = true
  try {
    await authApi.changePassword(oldPassword.value, newPassword.value)
    appStore.showToast('密码修改成功', 'success')
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch {
    appStore.showToast('密码修改失败，请检查当前密码', 'error')
  } finally {
    saving.value = false
  }
}

function handleLogout() {
  authStore.logout()
  appStore.closeSettings()
  router.push('/login')
}
</script>
