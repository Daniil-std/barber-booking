import { Arrow } from '../../components'
import { useI18n } from '../../i18n'
import type { Contact } from '../../types'

interface ReviewStepProps {
  contact: Contact
  busy: boolean
  onBack: () => void
  onConfirm: () => void
}

export function ReviewStep({
  contact,
  busy,
  onBack,
  onConfirm,
}: ReviewStepProps) {
  const { t } = useI18n()
  return (
    <>
      <p className="step-description">
        {t('Check your details. Your appointment is saved when you confirm.')}
      </p>
      <dl className="review-details">
        <div>
          <dt>{t('Name')}</dt>
          <dd>{contact.contact_name}</dd>
        </div>
        <div>
          <dt>{t('Email')}</dt>
          <dd>{contact.contact_email}</dd>
        </div>
        <div>
          <dt>{t('Phone')}</dt>
          <dd>{contact.contact_phone}</dd>
        </div>
        {contact.notes && (
          <div>
            <dt>{t('Notes')}</dt>
            <dd>{contact.notes}</dd>
          </div>
        )}
      </dl>
      <p className="review-note">
        {t(
          'You can cancel a future appointment in your account. Your confirmation is saved there too.',
        )}
      </p>
      <div className="step-actions">
        <button
          className="button button-outline"
          disabled={busy}
          onClick={onBack}
        >
          {t('Edit details')}
        </button>
        <button
          className="button button-copper"
          disabled={busy}
          onClick={onConfirm}
        >
          {busy ? t('Confirming…') : t('Confirm appointment')}
          <Arrow />
        </button>
      </div>
    </>
  )
}
