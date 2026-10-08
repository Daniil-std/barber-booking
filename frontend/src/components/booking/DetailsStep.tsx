import type { FormEvent } from 'react'
import { Auth } from '../../Auth'
import { Arrow } from '../../components'
import { Field } from '../../Form'
import { useI18n } from '../../i18n'
import type { Contact, User } from '../../types'

interface DetailsStepProps {
  user: User | null
  contact: Contact
  error: unknown
  onSuccess: (user: User) => void
  onChange: (name: keyof Contact, value: string) => void
  onSubmit: (event: FormEvent) => void
  onBack: () => void
}

export function DetailsStep({
  user,
  contact,
  error,
  onSuccess,
  onChange,
  onSubmit,
  onBack,
}: DetailsStepProps) {
  const { t } = useI18n()
  return (
    <>
      {!user ? (
        <>
          <Auth embedded onSuccess={onSuccess} />
          <button className="text-link" onClick={onBack}>
            {t('← Back to available times')}
          </button>
        </>
      ) : (
        <>
          <p className="step-description">
            {t(
              'Signed in as {email}. These details are saved with your appointment.',
              { email: user.email },
            )}
          </p>
          <form className="contact-form" onSubmit={onSubmit}>
            <Field
              label={t('Your name')}
              name="contact_name"
              autoComplete="name"
              required
              maxLength={100}
              value={contact.contact_name}
              onChange={(e) => onChange('contact_name', e.target.value)}
              error={error}
            />
            <Field
              label={t('Email address')}
              name="contact_email"
              type="email"
              autoComplete="email"
              required
              maxLength={254}
              value={contact.contact_email}
              onChange={(e) => onChange('contact_email', e.target.value)}
              error={error}
            />
            <Field
              label={t('Phone number')}
              name="contact_phone"
              type="tel"
              autoComplete="tel"
              required
              maxLength={25}
              value={contact.contact_phone}
              onChange={(e) => onChange('contact_phone', e.target.value)}
              hint={t('Include a country code, for example +48 555 010 123.')}
              error={error}
            />
            <div className="form-field">
              <label htmlFor="notes">
                {t('Anything we should know?')} <span>{t('(optional)')}</span>
              </label>
              <textarea
                id="notes"
                name="notes"
                maxLength={500}
                rows={3}
                value={contact.notes}
                onChange={(e) => onChange('notes', e.target.value)}
              />
              <p className="field-hint">{t('Up to 500 characters.')}</p>
            </div>
            <div className="step-actions">
              <button
                className="button button-outline"
                type="button"
                onClick={onBack}
              >
                {t('Back')}
              </button>
              <button className="button button-dark" type="submit">
                {t('Review appointment')}
                <Arrow />
              </button>
            </div>
          </form>
        </>
      )}
    </>
  )
}
