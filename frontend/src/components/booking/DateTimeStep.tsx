import { Arrow } from '../../components'
import { addDays, useStudioDates } from '../../dates'
import { ErrorNotice, Field, Loading } from '../../Form'
import { useI18n } from '../../i18n'
import type { Catalog } from '../../types'

interface DateTimeStepProps {
  catalog: Pick<Catalog, 'today' | 'booking_horizon_days'>
  day: string
  slots: string[]
  slot: string
  slotsLoading: boolean
  slotError: unknown
  onDayChange: (day: string) => void
  onSlotChange: (slot: string) => void
  onRetry: () => void
  onBack: () => void
  onNext: () => void
}

export function DateTimeStep({
  catalog,
  day,
  slots,
  slot,
  slotsLoading,
  slotError,
  onDayChange,
  onSlotChange,
  onRetry,
  onBack,
  onNext,
}: DateTimeStepProps) {
  const { t } = useI18n()
  const { shortDateLabel, timeLabel } = useStudioDates()
  return (
    <>
      <p className="step-description">
        {t(
          "Appointments open up to {days} days ahead, with at least 30 minutes' notice.",
          { days: catalog.booking_horizon_days },
        )}
      </p>
      <Field
        label={t('Appointment date')}
        name="appointment_date"
        type="date"
        value={day}
        min={catalog.today}
        max={addDays(catalog.today, catalog.booking_horizon_days)}
        onChange={(e) => {
          if (e.target.value) {
            onDayChange(e.target.value)
          }
        }}
        required
      />
      <p className="slot-date">
        {shortDateLabel(`${day}T12:00:00Z`)} <span>· {t('Warsaw time')}</span>
      </p>
      <ErrorNotice error={slotError} onRetry={onRetry} />
      {slotsLoading ? (
        <Loading>{t('Finding available times…')}</Loading>
      ) : (
        !slotError && (
          <>
            {slots.length === 0 ? (
              <div className="empty-state">
                <p>{t('No appointments fit this service on this date.')}</p>
                <p>
                  {t(
                    'Try another date or go back to choose a different barber.',
                  )}
                </p>
              </div>
            ) : (
              <fieldset className="slot-grid">
                <legend className="sr-only">
                  {t('Choose an available time')}
                </legend>
                {slots.map((value) => (
                  <label key={value} className="slot-choice">
                    <input
                      type="radio"
                      name="time"
                      checked={slot === value}
                      onChange={() => onSlotChange(value)}
                    />
                    <span>{timeLabel(value)}</span>
                  </label>
                ))}
              </fieldset>
            )}
          </>
        )
      )}
      <div className="step-actions">
        <button className="button button-outline" onClick={onBack}>
          {t('Back')}
        </button>
        <button
          className="button button-dark"
          disabled={!slot || slotsLoading}
          onClick={onNext}
        >
          {t('Your details')}
          <Arrow />
        </button>
      </div>
    </>
  )
}
