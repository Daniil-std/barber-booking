import type { Appointment, Catalog, Contact, Session } from './types'

function messages(value: unknown): string[] {
  if (typeof value === 'string') return [value]
  if (Array.isArray(value)) return value.flatMap(messages)
  if (value && typeof value === 'object')
    return Object.values(value).flatMap(messages)
  return []
}

export class ApiError extends Error {
  status: number
  fields: Record<string, unknown>
  constructor(status: number, body: unknown) {
    const fields =
      body && typeof body === 'object' && 'errors' in body
        ? (body.errors as Record<string, unknown>)
        : {}
    super(
      messages(fields).join(' ') ||
        (status >= 500
          ? 'The studio is temporarily unavailable. Please try again.'
          : 'The request could not be completed. Please try again.'),
    )
    this.status = status
    this.fields = fields
  }
  field(name: string) {
    return messages(this.fields?.[name]).join(' ')
  }
}

let csrfToken = ''

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), 15000)
  const signal = options.signal
    ? AbortSignal.any([controller.signal, options.signal])
    : controller.signal
  try {
    const response = await fetch(`/api/${path}`, {
      ...options,
      signal,
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.method === 'POST' ? { 'X-CSRFToken': csrfToken } : {}),
        ...options.headers,
      },
    })
    const body: unknown = await response.json().catch(() => null)
    if (!response.ok) throw new ApiError(response.status, body)
    if (
      body &&
      typeof body === 'object' &&
      'csrfToken' in body &&
      typeof body.csrfToken === 'string'
    )
      csrfToken = body.csrfToken
    return body as T
  } catch (error) {
    if (options.signal?.aborted) throw error
    if (error instanceof ApiError) throw error
    throw new Error(
      'We could not reach the studio. Check your connection and try again.',
    )
  } finally {
    window.clearTimeout(timer)
  }
}

async function post<T>(path: string, data: unknown = {}) {
  if (!csrfToken) await request<Session>('auth/session/')
  return request<T>(path, { method: 'POST', body: JSON.stringify(data) })
}

export const api = {
  catalog: (signal?: AbortSignal) => request<Catalog>('catalog/', { signal }),
  session: (signal?: AbortSignal) =>
    request<Session>('auth/session/', { signal }),
  register: (first_name: string, email: string, password: string) =>
    post<Session>('auth/register/', { first_name, email, password }),
  login: (email: string, password: string) =>
    post<Session>('auth/login/', { email, password }),
  logout: () => post<Session>('auth/logout/'),
  slots: (
    service: number,
    barber: number,
    date: string,
    signal?: AbortSignal,
  ) =>
    request<{ slots: string[] }>(
      `availability/?${new URLSearchParams({ service: String(service), barber: String(barber), date })}`,
      { signal },
    ),
  book: (
    service: number,
    barber: number,
    starts_at: string,
    contact: Contact,
  ) =>
    post<Appointment>('appointments/', {
      service,
      barber,
      starts_at,
      ...contact,
    }),
  appointments: (signal?: AbortSignal) =>
    request<Appointment[]>('appointments/', { signal }),
  cancel: (id: number) => post<Appointment>(`appointments/${id}/cancel/`),
}
export const errorText = (error: unknown) =>
  error instanceof Error
    ? error.message
    : 'Something went wrong. Please try again.'
