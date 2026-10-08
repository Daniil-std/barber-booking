export interface Service {
  id: number
  name: string
  description: string
  duration_minutes: number
  price: string
  min_price: string
  is_training: boolean
  prices: { barber_id: number; level: BarberLevel; price: string }[]
}

export type BarberLevel = 'junior' | 'senior' | 'top' | 'trainee'

export interface Barber {
  id: number
  name: string
  role: string
  bio: string
  initials: string
  services: number[]
  level: BarberLevel
  level_label: string
  supervisor: number | null
  supervisor_name: string | null
}

export interface Catalog {
  services: Service[]
  barbers: Barber[]
  timezone: string
  today: string
  booking_horizon_days: number
}
export interface User {
  id: number
  email: string
  first_name: string
}
export interface Session {
  user: User | null
  csrfToken: string
}
export interface Contact {
  contact_name: string
  contact_email: string
  contact_phone: string
  notes: string
}
export interface Appointment extends Contact {
  id: number
  service: number
  service_name: string
  barber: number
  barber_name: string
  barber_level: BarberLevel
  barber_level_label: string
  supervisor: number | null
  supervisor_name: string | null
  starts_at: string
  ends_at: string
  duration_minutes: number
  price: string
  status: 'confirmed' | 'cancelled'
  created_at: string
  cancelled_at: string | null
}
