import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor — attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('athletics_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor — handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('athletics_token')
      localStorage.removeItem('athletics_role')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

/* ---- Auth ---- */
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  changePassword: (old_password: string, new_password: string) =>
    api.post('/auth/change-password', { old_password, new_password }),
}

/* ---- Athletes ---- */
export const athleteApi = {
  list: (params?: Record<string, string>) => api.get('/athletes', { params }),
  get: (id: number) => api.get(`/athletes/${id}`),
  getMe: () => api.get('/athletes/me'),
  create: (data: Record<string, unknown>) => api.post('/athletes', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/athletes/${id}`, data),
  delete: (id: number) => api.delete(`/athletes/${id}`),
}

/* ---- Sessions ---- */
export const sessionApi = {
  list: (params?: Record<string, string>) => api.get('/sessions', { params }),
  create: (data: Record<string, unknown>) => api.post('/sessions', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/sessions/${id}`, data),
  delete: (id: number) => api.delete(`/sessions/${id}`),
  generateQR: (id: number, data?: Record<string, unknown>) => api.post(`/sessions/${id}/qr`, data),
  getQR: (id: number) => api.get(`/sessions/${id}/qr`),
}

/* ---- Attendance ---- */
export const attendanceApi = {
  list: (params?: Record<string, string>) => api.get('/attendance', { params }),
  getMe: () => api.get('/attendance/me'),
  create: (data: Record<string, unknown>) => api.post('/attendance', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/attendance/${id}`, data),
  delete: (id: number) => api.delete(`/attendance/${id}`),
  qrCheckin: (data: Record<string, unknown>) => api.post('/attendance/qr-checkin', data),
}

/* ---- Scores ---- */
export const scoreApi = {
  list: (params?: Record<string, string>) => api.get('/scores', { params }),
  getMe: () => api.get('/scores/me'),
  create: (data: Record<string, unknown>) => api.post('/scores', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/scores/${id}`, data),
  delete: (id: number) => api.delete(`/scores/${id}`),
}

/* ---- Events ---- */
export const eventApi = {
  list: () => api.get('/events'),
  create: (data: Record<string, unknown>) => api.post('/events', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/events/${id}`, data),
  delete: (id: number) => api.delete(`/events/${id}`),
}

/* ---- Ratings ---- */
export const ratingApi = {
  list: (params?: Record<string, string>) => api.get('/ratings', { params }),
  getMe: () => api.get('/ratings/me'),
  create: (data: Record<string, unknown>) => api.post('/ratings', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/ratings/${id}`, data),
  delete: (id: number) => api.delete(`/ratings/${id}`),
}

/* ---- Rankings ---- */
export const rankingApi = {
  get: (eventId: number) => api.get(`/rankings/${eventId}`),
}

/* ---- Stats ---- */
export const statsApi = {
  attendance: () => api.get('/stats/attendance'),
  events: () => api.get('/stats/events'),
}

/* ---- Featured Event ---- */
export const featuredEventApi = {
  get: () => api.get('/featured-event'),
  update: (data: Record<string, unknown>) => api.put('/featured-event', data),
}

/* ---- Training Content ---- */
export const trainingContentApi = {
  list: (params?: Record<string, string>) => api.get('/training-contents', { params }),
  get: (id: number) => api.get(`/training-contents/${id}`),
  create: (data: Record<string, unknown>) => api.post('/training-contents', data),
  update: (id: number, data: Record<string, unknown>) => api.put(`/training-contents/${id}`, data),
  delete: (id: number) => api.delete(`/training-contents/${id}`),
  categories: () => api.get('/training-contents/categories/list'),
  targetGroups: () => api.get('/training-contents/target-groups/list'),
}
