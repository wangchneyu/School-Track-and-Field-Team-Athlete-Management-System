import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        { path: '', name: 'AdminDashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'athletes', name: 'Athletes', component: () => import('@/views/admin/AthletesView.vue') },
        { path: 'training', name: 'Training', component: () => import('@/views/admin/TrainingView.vue') },
        { path: 'attendance', name: 'Attendance', component: () => import('@/views/admin/AttendanceView.vue') },
        { path: 'scores', name: 'Scores', component: () => import('@/views/admin/ScoresView.vue') },
        { path: 'rankings', name: 'Rankings', component: () => import('@/views/admin/RankingsView.vue') },
        { path: 'events', name: 'Events', component: () => import('@/views/admin/EventsView.vue') },
        { path: 'ratings', name: 'Ratings', component: () => import('@/views/admin/RatingsView.vue') },
        { path: 'content', name: 'TrainingContent', component: () => import('@/views/admin/TrainingContentView.vue') },
        { path: 'notifications', name: 'AdminNotifications', component: () => import('@/views/admin/NotificationsView.vue') },
      ],
    },
    {
      path: '/athlete',
      component: () => import('@/views/athlete/AthleteLayout.vue'),
      meta: { requiresAuth: true, role: 'athlete' },
      children: [
        { path: '', name: 'AthleteDashboard', component: () => import('@/views/athlete/DashboardView.vue') },
        { path: 'scores', name: 'MyScores', component: () => import('@/views/athlete/MyScoresView.vue') },
        { path: 'attendance', name: 'MyAttendance', component: () => import('@/views/athlete/MyAttendanceView.vue') },
        { path: 'ratings', name: 'MyRatings', component: () => import('@/views/athlete/MyRatingsView.vue') },
        { path: 'checkin', name: 'CheckIn', component: () => import('@/views/athlete/CheckInView.vue') },
        { path: 'notifications', name: 'AthleteNotifications', component: () => import('@/views/athlete/NotificationsView.vue') },
      ],
    },
  ],
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('athletics_token')
  const role = localStorage.getItem('athletics_role')

  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if (to.meta.role && to.meta.role !== role) {
    next(role === 'admin' ? '/admin' : '/athlete')
    return
  }

  if (to.path === '/login' && token) {
    next(role === 'admin' ? '/admin' : '/athlete')
    return
  }

  next()
})

export default router
