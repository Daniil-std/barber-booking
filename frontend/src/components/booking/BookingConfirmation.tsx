import type { Ref } from 'react'
import { Arrow, Price } from '../../components'
import { useStudioDates } from '../../dates'
import { useI18n } from '../../i18n'
import type { Appointment } from '../../types'

interface BookingConfirmationProps {
  confirmed: Appointment
  heading: Ref<HTMLHeadingElement>
}

export function BookingConfirmation({
  confirmed,
  heading,
}: BookingConfirmationProps) {
  const { t } = useI18n()
  const { dateLabel, timeLabel } = useStudioDates()
  return (
    <section className="page-section confirmation">
      <p className="eyebrow">
        {t('ALL SET · APPOINTMENT #{id}', { id: confirmed.id })}
      </p>
      <span className="success-mark" aria-hidden="true">
        ✓
      </span>
      <h1 ref={heading} tabIndex={-1}>
        {t("You're in good hands.")}
      </h1>
      <p className="page-description">
        {t('Your appointment is confirmed and saved to your account.')}
      </p>
      <dl className="confirmation-details">
        <div>
          <dt>{t('Service')}</dt>
          <dd>{t(confirmed.service_name)}</dd>
        </div>
        <div>
          <dt>{t('Barber')}</dt>
          <dd>
            {confirmed.barber_name} · {t(confirmed.barber_level_label)}
          </dd>
        </div>
        {confirmed.supervisor_name && (
          <div>
            <dt>{t('Senior supervision')}</dt>
            <dd>{confirmed.supervisor_name}</dd>
          </div>
        )}
        <div>
          <dt>{t('When')}</dt>
          <dd>
            {dateLabel(confirmed.starts_at)}
            <br />
            {timeLabel(confirmed.starts_at)}–{timeLabel(confirmed.ends_at)} ·{' '}
            {t('Warsaw time')}
          </dd>
        </div>
        <div>
          <dt>{t('Price')}</dt>
          <dd>
            <Price value={confirmed.price} />
          </dd>
        </div>
      </dl>
      <a className="button button-dark" href="#/account">
        {t('View my appointments')}
        <Arrow />
      </a>
      <p className="small-note">
        {t('Manage or cancel your appointment from your account.')}
      </p>
    </section>
  )
}
