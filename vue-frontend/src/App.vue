<template>
  <div class="min-h-screen">
    <!-- Toast container -->
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div
        v-for="toast in appStore.toasts"
        :key="toast.id"
        :class="[
          'px-4 py-3 rounded-lg text-sm font-medium shadow-elegant max-w-sm',
          toast.type === 'success' ? 'bg-success text-accent-foreground' : '',
          toast.type === 'error' ? 'bg-destructive text-accent-foreground' : '',
          toast.type === 'info' ? 'bg-primary text-primary-foreground' : '',
        ]"
      >
        {{ toast.message }}
      </div>
    </TransitionGroup>

    <!-- Settings Panel -->
    <SettingsPanel v-if="appStore.settingsOpen" @close="appStore.closeSettings" />

    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useAppStore } from '@/stores/app'
import SettingsPanel from '@/components/settings/SettingsPanel.vue'

const appStore = useAppStore()
</script>

<style>
.toast-container {
  position: fixed;
  bottom: 5rem;
  right: 1rem;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
@media (min-width: 640px) {
  .toast-container {
    bottom: 1rem;
  }
}
.toast-enter-active {
  animation: slide-up 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
