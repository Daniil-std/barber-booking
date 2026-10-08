import { Price } from '../../components'
import { useStudioDates } from '../../dates'
import { useI18n } from '../../i18n'
import type { Barber, Service } from '../../types'

interface BookingSummaryProps {
  service: Service | undefined
  barber: Barber | undefined
  slot: string
  price: string | null
}

export function BookingSummary({
  service,
  barber,
  slot,
  price,
}: BookingSummaryProps) {
  const { t } = useI18n()
  const { shortDateLabel, timeLabel } = useStudioDates()
  return (
    <aside className="booking-summary" aria-label={t('Appointment summary')}>
      <p className="eyebrow">{t('YOUR TIME AT FORM')}</p>
      <h3>{t('A fresh start.')}</h3>
      <dl>
        <div>
          <dt>{t('Service')}</dt>
          <dd>
            {service ? t(service.name) : t('Choose your service')}
            {service && (
              <small>
                {t('{minutes} minutes', {
                  minutes: service.duration_minutes,
                })}
              </small>
            )}
          </dd>
        </div>
        <div>
          <dt>{t('Barber')}</dt>
          <dd>
            {barber ? (
              <>
                {barber.name}
                <small>{t(barber.level_label)}</small>
              </>
            ) : (
              t('Choose your barber.')
            )}
          </dd>
        </div>
        {service?.is_training && barber?.supervisor_name && (
          <div>
            <dt>{t('Senior supervision')}</dt>
            <dd>
              {barber.supervisor_name}
              <small>
                {t('Both barbers are reserved for your full visit.')}
              </small>
            </dd>
          </div>
        )}
        <div>
          <dt>{t('When')}</dt>
          <dd>
            {slot ? (
              <>
                {shortDateLabel(slot)}
                <small>
                  {timeLabel(slot)} · {t('Warsaw time')}
                </small>
              </>
            ) : (
              t('Choose a date & time')
            )}
          </dd>
        </div>
      </dl>
      <div className="summary-total">
        <span>{t('Total')}</span>
        <strong>
          {service ? (
            <>
              {!price && !service.is_training && (
                <small className="price-from">{t('From')}</small>
              )}
              <Price value={price ?? service.min_price} />
            </>
          ) : (
            '—'
          )}
        </strong>
      </div>
      <p className="small-note">
        {service?.is_training
          ? t('50% of the Junior haircut price. Senior supervision included.')
          : t('Your price is based on the barber you choose.')}
      </p>
    </aside>
  )
}
