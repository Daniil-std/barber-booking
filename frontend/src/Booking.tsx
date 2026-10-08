import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { api, ApiError } from './api'
import { addDays } from './dates'
import { useI18n } from './i18n'
import { ErrorNotice } from './Form'
import { quoteFor } from './pricing'
import type { Appointment, Catalog, Contact, User } from './types'

import { ServiceStep } from './components/booking/ServiceStep'
import { BarberStep } from './components/booking/BarberStep'
import { DateTimeStep } from './components/booking/DateTimeStep'
import { DetailsStep } from './components/booking/DetailsStep'
import { ReviewStep } from './components/booking/ReviewStep'
import { BookingSummary } from './components/booking/BookingSummary'
import { BookingConfirmation } from './components/booking/BookingConfirmation'

const steps = ['Service', 'Barber', 'Date & time', 'Your details', 'Review']

export function Booking({
  catalog,
  user,
  onUser,
  initialService,
  initialBarber,
}: {
  catalog: Catalog
  user: User | null
  onUser: (user: User | null) => void
  initialService?: number
  initialBarber?: number
}) {
  const { t } = useI18n()
  const [step, setStep] = useState(0)
  const [serviceId, setServiceId] = useState(initialService)
  const [barberId, setBarberId] = useState(initialBarber)
  const [day, setDay] = useState(addDays(catalog.today, 1))
  const [slots, setSlots] = useState<string[]>([])
  const [slot, setSlot] = useState('')
  const [slotsLoading, setSlotsLoading] = useState(false)
  const [slotError, setSlotError] = useState<unknown>(null)
  const [refresh, setRefresh] = useState(0)
  const [contact, setContact] = useState<Contact>({
    contact_name: user?.first_name || '',
    contact_email: user?.email || '',
    contact_phone: '',
    notes: '',
  })
  const [error, setError] = useState<unknown>(null)
  const [busy, setBusy] = useState(false)
  const [confirmed, setConfirmed] = useState<Appointment | null>(null)
  const pending = useRef(false)
  const heading = useRef<HTMLHeadingElement>(null)
  const service = catalog.services.find((item) => item.id === serviceId)
  const barber = catalog.barbers.find((item) => item.id === barberId)
  const price = quoteFor(service, barberId)
  const eligible = catalog.barbers.filter(
    (item) => quoteFor(service, item.id) !== null,
  )

  useEffect(() => {
    heading.current?.focus({ preventScroll: true })
  }, [step, confirmed])
  useEffect(() => {
    if (step !== 2 || !serviceId || !barberId) return
    const controller = new AbortController()
    setSlotsLoading(true)
    setSlotError(null)
    setSlots([])
    setSlot('')
    api
      .slots(serviceId, barberId, day, controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setSlots(data.slots)
      })
      .catch((failure) => {
        if (!controller.signal.aborted) setSlotError(failure)
      })
      .finally(() => {
        if (!controller.signal.aborted) setSlotsLoading(false)
      })
    return () => controller.abort()
  }, [step, serviceId, barberId, day, refresh])

  function setService(id: number) {
    setServiceId(id)
    setSlot('')
    if (
      !quoteFor(
        catalog.services.find((item) => item.id === id),
        barberId,
      )
    )
      setBarberId(undefined)
  }
  function contactChanged(name: keyof Contact, value: string) {
    setContact((current) => ({ ...current, [name]: value }))
  }
  function detailsSubmit(event: FormEvent) {
    event.preventDefault()
    const digits = contact.contact_phone.replace(/\D/g, '')
    if (
      digits.length < 7 ||
      digits.length > 15 ||
      !/^[+]?[0-9 ()-]{7,25}$/.test(contact.contact_phone)
    ) {
      setError(new Error('Enter a phone number containing 7–15 digits.'))
      return
    }
    if (!contact.contact_name.trim()) {
      setError(new Error('Enter your name.'))
      return
    }
    setError(null)
    setStep(4)
  }
  async function confirm() {
    if (pending.current || !serviceId || !barberId || !slot) return
    pending.current = true
    setBusy(true)
    setError(null)
    try {
      setConfirmed(
        await api.book(serviceId, barberId, slot, {
          ...contact,
          contact_name: contact.contact_name.trim(),
          contact_email: contact.contact_email.trim(),
          contact_phone: contact.contact_phone.trim(),
        }),
      )
    } catch (failure) {
      setError(failure)
      if (failure instanceof ApiError && failure.status === 409) {
        setSlot('')
        setRefresh((value) => value + 1)
        setStep(2)
      } else if (failure instanceof ApiError && failure.status === 403) {
        const session = await api.session().catch(() => null)
        if (session) onUser(session.user)
        setStep(3)
      } else if (failure instanceof ApiError && failure.status === 400)
        setStep(3)
    } finally {
      pending.current = false
      setBusy(false)
    }
  }

  if (confirmed)
    return <BookingConfirmation confirmed={confirmed} heading={heading} />

  return (
    <section className="page-section booking-page">
      <a href="#" className="back-link">
        {t('← Back to the studio')}
      </a>
      <div className="booking-heading">
        <div>
          <p className="eyebrow">{t('A LITTLE TIME FOR YOU')}</p>
          <h1>{t('Find your next form.')}</h1>
        </div>
        <p className="small-note">
          {t('Appointments in Warsaw')}
          <br />
          {t('All times in Europe/Warsaw')}
        </p>
      </div>
      <ol className="booking-steps" aria-label={t('Booking progress')}>
        {steps.map((label, index) => (
          <li
            key={label}
            aria-current={step === index ? 'step' : undefined}
            className={index < step ? 'is-complete' : ''}
          >
            <span>
              {index < step ? '✓' : String(index + 1).padStart(2, '0')}
            </span>
            {t(label)}
          </li>
        ))}
      </ol>
      <div className="booking-layout">
        <div className="booking-content">
          <h2 ref={heading} tabIndex={-1}>
            {
              [
                t('Start with the service.'),
                t('Choose your barber.'),
                t('Pick your moment.'),
                t('Make it yours.'),
                t('One last look.'),
              ][step]
            }
          </h2>
          <ErrorNotice error={error} />
          {step === 0 && (
            <ServiceStep
              catalog={catalog}
              serviceId={serviceId}
              service={service}
              onSelect={setService}
              onNext={() => setStep(1)}
            />
          )}
          {step === 1 && (
            <BarberStep
              eligible={eligible}
              barberId={barberId}
              service={service}
              onSelect={(id) => {
                setBarberId(id)
                setSlot('')
              }}
              onBack={() => setStep(0)}
              onNext={() => setStep(2)}
            />
          )}
          {step === 2 && (
            <DateTimeStep
              catalog={catalog}
              day={day}
              slots={slots}
              slot={slot}
              slotsLoading={slotsLoading}
              slotError={slotError}
              onDayChange={(value) => {
                setDay(value)
                setSlot('')
              }}
              onSlotChange={(value) => {
                setSlot(value)
                setError(null)
              }}
              onRetry={() => setRefresh((value) => value + 1)}
              onBack={() => {
                setError(null)
                setStep(1)
              }}
              onNext={() => {
                setError(null)
                setStep(3)
              }}
            />
          )}
          {step === 3 && (
            <DetailsStep
              user={user}
              contact={contact}
              error={error}
              onChange={contactChanged}
              onSubmit={detailsSubmit}
              onBack={() => setStep(2)}
              onSuccess={(account) => {
                onUser(account)
                setContact((current) => ({
                  ...current,
                  contact_name: current.contact_name || account.first_name,
                  contact_email: current.contact_email || account.email,
                }))
                setError(null)
              }}
            />
          )}
          {step === 4 && (
            <ReviewStep
              contact={contact}
              busy={busy}
              onBack={() => setStep(3)}
              onConfirm={confirm}
            />
          )}
        </div>
        <BookingSummary
          service={service}
          barber={barber}
          slot={slot}
          price={price}
        />
      </div>
    </section>
  )
}
