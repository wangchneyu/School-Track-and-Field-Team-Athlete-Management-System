/* ---- Shared Types ---- */

export interface User {
  id: number
  username: string
  role: 'admin' | 'athlete'
  is_active: boolean
}

export interface Athlete {
  id: number
  user_id: number
  name: string
  student_id: string
  gender: string
  group: string
  main_event: string
  phone: string
}

export interface TrainingSession {
  id: number
  date: string
  start_time: string
  end_time: string
  location: string
  description: string
  created_by: number | null
}

export interface Attendance {
  id: number
  session_id: number
  athlete_id: number
  status: 'present' | 'late' | 'absent' | 'leave'
  remark: string
  method: string
  created_at: string
  athlete_name?: string
  session_date?: string
}

export interface Event {
  id: number
  name: string
  type: 'time' | 'distance'
  gender_limit: string
}

export interface Score {
  id: number
  athlete_id: number
  event_id: number
  performance: number
  is_official: boolean
  remark: string
  recorded_at: string
  athlete_name?: string
  event_name?: string
}

export interface Rating {
  id: number
  athlete_id: number
  coach_id: number
  date: string
  attitude: number
  attendance: number
  performance: number
  comment: string
  athlete_name?: string
}

export interface FeaturedEvent {
  id?: number
  name: string
  start_time: string
  location: string
  description: string
  countdown_seconds?: number
  countdown_days?: number
}

export interface TrainingContent {
  id: number
  title: string
  content: string
  category: string
  target_group: string
  duration: number
  intensity: 'low' | 'medium' | 'high'
  created_at: string
}

export interface Ranking {
  rank: number
  athlete_id: number
  name: string
  group: string
  best_performance: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  role: string
}

export interface Stats {
  attendance: Array<{
    athlete_id: number
    name: string
    total: number
    present: number
    rate: number
  }>
  events: Array<{
    event_id: number
    name: string
    count: number
  }>
}

export interface Notification {
  id: number
  title: string
  content: string
  type: 'training' | 'announcement' | 'general'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  target_group: string
  session_id: number | null
  created_by: number
  created_at: string
  is_active: boolean
  creator_name?: string
  session_date?: string
  session_location?: string
  session_time?: string
  is_read: boolean
  read_at?: string
  read_count: number
  total_target: number
}

export interface NotificationReadUser {
  user_id: number
  username: string
  read_at: string
}

export interface NotificationUnreadUser {
  user_id: number
  username: string
  name: string
}

export interface NotificationDetail extends Notification {
  read_users: NotificationReadUser[]
  unread_users: NotificationUnreadUser[]
}

export type ToastType = 'success' | 'error' | 'info'

export interface Toast {
  id: number
  message: string
  type: ToastType
}

export interface AthleteCheckinDetail {
  athlete_id: number
  name: string
  student_id: string
  group: string
  status: 'present' | 'late' | 'absent' | 'leave' | 'unchecked'
  method: string | null
  checkin_time: string | null
}

export interface SessionAttendanceStat {
  session_id: number
  session_date: string
  start_time: string
  end_time: string
  location: string
  total_athletes: number
  present_count: number
  late_count: number
  absent_count: number
  leave_count: number
  unchecked_count: number
  attendance_rate: number
  athletes: AthleteCheckinDetail[]
}

export interface DailyAttendanceSummary {
  date: string
  total_sessions: number
  total_athletes: number
  present_count: number
  late_count: number
  absent_count: number
  leave_count: number
  unchecked_count: number
  attendance_rate: number
  sessions: SessionAttendanceStat[]
}
