import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, athleteApi } from '@/api'
import type { Athlete } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('athletics_token') || '')
  const role = ref(localStorage.getItem('athletics_role') || '')
  const athlete = ref<Athlete | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')
  const isAthlete = computed(() => role.value === 'athlete')

  async function login(username: string, password: string) {
    const res = await authApi.login(username, password)
    token.value = res.data.access_token
    role.value = res.data.role
    localStorage.setItem('athletics_token', token.value)
    localStorage.setItem('athletics_role', role.value)

    if (role.value === 'athlete') {
      await fetchAthleteProfile()
    }
    return res.data
  }

  async function fetchAthleteProfile() {
    try {
      const res = await athleteApi.getMe()
      athlete.value = res.data
    } catch {
      athlete.value = null
    }
  }

  function logout() {
    token.value = ''
    role.value = ''
    athlete.value = null
    localStorage.removeItem('athletics_token')
    localStorage.removeItem('athletics_role')
  }

  return {
    token,
    role,
    athlete,
    isLoggedIn,
    isAdmin,
    isAthlete,
    login,
    logout,
    fetchAthleteProfile,
  }
})
