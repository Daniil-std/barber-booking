import { useEffect, useRef, useState } from 'react'
import { api, ApiError } from './api'
import { Arrow, Price } from './components'
import { useStudioDates } from './dates'
import { useI18n } from './i18n'
import { ErrorNotice, Loading } from './Form'
import type { Appointment, User } from './types'

export function Account({
  user,
  onSignedOut,
}: {
  user: User
  onSignedOut: () => void
}) {
  const { t } = useI18n()
  const { dateLabel, timeLabel } = useStudioDates()
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [refresh, setRefresh] = useState(0)
  const [filter, setFilter] = useState<'upcoming' | 'past' | 'cancelled'>(
    'upcoming',
  )
  const [cancelId, setCancelId] = useState<number | null>(null)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const pending = useRef(false)

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setError(null)
    api
      .appointments(controller.signal)
      .then((items) => {
        if (!controller.signal.aborted) setAppointments(items)
      })
      .catch((failure) => {
        if (!controller.signal.aborted) {
          setError(failure)
          if (failure instanceof ApiError && failure.status === 403)
            onSignedOut()
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [refresh, onSignedOut])

  async function cancel(id: number) {
    if (pending.current) return
    pending.current = true
    setBusy(true)
    setError(null)
    setNotice('')
    try {
      const updated = await api.cancel(id)
      setAppointments((items) =>
        items.map((item) => (item.id === id ? updated : item)),
      )
      setCancelId(null)
      setNotice(
        'Your appointment has been cancelled. The time is available again.',
      )
    } catch (failure) {
      setError(failure)
    } finally {
      pending.current = false
      setBusy(false)
    }
  }
  const visible = appointments
    .filter((item) =>
      filter === 'cancelled'
        ? item.status === 'cancelled'
        : item.status === 'confirmed' &&
          (filter === 'upcoming'
            ? new Date(item.starts_at).getTime() > Date.now()
            : new Date(item.starts_at).getTime() <= Date.now()),
    )
    .sort((a, b) =>
      filter === 'upcoming'
        ? Date.parse(a.starts_at) - Date.parse(b.starts_at)
        : Date.parse(b.starts_at) - Date.parse(a.starts_at),
    )

  return (
    <section className="page-section account-page">
      <a href="#" className="back-link">
        {t('← Back to the studio')}
      </a>
      <div className="booking-heading">
        <div>
          <p className="eyebrow">{t('YOUR FORM ACCOUNT')}</p>
          <h1>
            {t('Good to see you, {name}.', {
              name: user.first_name || t('friend'),
            })}
          </h1>
          <p className="page-description">
            {t('Your appointments, all in one place.')}
          </p>
        </div>
        <a className="button button-dark" href="#/book">
          {t('Book a visit')}
          <Arrow />
        </a>
      </div>
      <div className="account-tabs" aria-label={t('Filter appointments')}>
        {(['upcoming', 'past', 'cancelled'] as const).map((value) => (
          <button
            key={value}
            aria-pressed={filter === value}
            onClick={() => {
              setFilter(value)
              setCancelId(null)
            }}
          >
            {t(value.charAt(0).toUpperCase() + value.slice(1))}
          </button>
        ))}
      </div>
      <ErrorNotice
        error={error}
        onRetry={() => setRefresh((value) => value + 1)}
      />
      {notice && (
        <p className="success-notice" role="status">
          {t(notice)}
        </p>
      )}
      {loading ? (
        <Loading>{t('Loading your appointments…')}</Loading>
      ) : (
        !error && (
          <>
            {visible.length === 0 ? (
              <div className="empty-state account-empty">
                <span className="eyebrow">
                  {t('A LITTLE SPACE IN YOUR DIARY')}
                </span>
                <h2>
                  {filter === 'upcoming'
                    ? t('Your next cut starts here.')
                    : t(
                        filter === 'past'
                          ? 'No past appointments yet.'
                          : 'No cancelled appointments yet.',
                      )}
                </h2>
                <p>
                  {filter === 'upcoming'
                    ? t(
                        'Choose a service, a barber and a time that works for you.',
                      )
                    : t('Appointments will appear here as your plans change.')}
                </p>
                {filter === 'upcoming' && (
                  <a className="text-link" href="#/book">
                    {t('Find an appointment')}
                    <Arrow />
                  </a>
                )}
              </div>
            ) : (
              <div className="appointment-list">
                {visible.map((item) => (
                  <article className="appointment-item" key={item.id}>
                    <div className="appointment-main">
                      <span className={`status-badge ${item.status}`}>
                        {item.status === 'cancelled'
                          ? t('Cancelled')
                          : new Date(item.starts_at).getTime() <= Date.now()
                            ? t('Past appointment')
                            : t('Confirmed')}{' '}
                        · #{item.id}
                      </span>
                      <h2>{t(item.service_name)}</h2>
                      <p>{dateLabel(item.starts_at)}</p>
                      <p>
                        {timeLabel(item.starts_at)}–{timeLabel(item.ends_at)} ·{' '}
                        {t('Warsaw time')}
                        <br />
                        {t('With {name} · {minutes} minutes', {
                          name: item.barber_name,
                          minutes: item.duration_minutes,
                        })}
                        <br />
                        {t(item.barber_level_label)}
                        {item.supervisor_name && (
                          <>
                            <br />
                            {t('Supervised by {name} · Senior', {
                              name: item.supervisor_name,
                            })}
                          </>
                        )}
                      </p>
                    </div>
                    <div className="appointment-side">
                      <strong>
                        <Price value={item.price} />
                      </strong>
                      {filter === 'upcoming' && (
                        <button
                          className="text-link"
                          disabled={busy}
                          onClick={() => setCancelId(item.id)}
                        >
                          {t('Cancel appointment')}
                        </button>
                      )}
                    </div>
                    {cancelId === item.id && (
                      <div
                        className="cancel-confirm"
                        role="group"
                        aria-label={t('Confirm cancellation')}
                      >
                        <p>
                          {t(
                            'Cancel this appointment? You can book another time afterwards.',
                          )}
                        </p>
                        <div>
                          <button
                            className="button button-outline"
                            disabled={busy}
                            onClick={() => setCancelId(null)}
                          >
                            {t('Keep appointment')}
                          </button>
                          <button
                            className="button button-dark"
                            disabled={busy}
                            onClick={() => cancel(item.id)}
                          >
                            {busy ? t('Cancelling…') : t('Yes, cancel')}
                          </button>
                        </div>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </>
        )
      )}
      <p className="small-note account-note">
        {t('All appointment times use Europe/Warsaw.')}
      </p>
    </section>
  )
}
