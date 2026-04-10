import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Toast, ToastType } from '@/types'

let toastId = 0

export const useAppStore = defineStore('app', () => {
  const sidebarOpen = ref(true)
  const toasts = ref<Toast[]>([])
  const settingsOpen = ref(false)

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function showToast(message: string, type: ToastType = 'info') {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id)
    }, 3000)
  }

  function openSettings() {
    settingsOpen.value = true
  }

  function closeSettings() {
    settingsOpen.value = false
  }

  return {
    sidebarOpen,
    toasts,
    settingsOpen,
    toggleSidebar,
    showToast,
    openSettings,
    closeSettings,
  }
})
