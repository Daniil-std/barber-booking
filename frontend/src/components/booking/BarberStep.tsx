import { Arrow, Price } from '../../components'
import { useI18n } from '../../i18n'
import { quoteFor } from '../../pricing'
import type { Barber, Service } from '../../types'

interface BarberStepProps {
  eligible: Barber[]
  barberId: number | undefined
  service: Service | undefined
  onSelect: (id: number) => void
  onBack: () => void
  onNext: () => void
}

export function BarberStep({
  eligible,
  barberId,
  service,
  onSelect,
  onBack,
  onNext,
}: BarberStepProps) {
  const { t } = useI18n()
  return (
    <>
      <p className="step-description">
        {t('Your cut, your person. Choose who you would like to see.')}
      </p>
      <fieldset className="choice-list">
        <legend className="sr-only">{t('Choose a barber')}</legend>
        {eligible.map((item) => (
          <label className="barber-choice" key={item.id}>
            <input
              type="radio"
              name="barber"
              checked={barberId === item.id}
              onChange={() => onSelect(item.id)}
            />
            <span className="mini-monogram" aria-hidden="true">
              {item.initials}
            </span>
            <span>
              <strong>{item.name}</strong>
              <span className="barber-level">{t(item.level_label)}</span>
              <small>{t(item.role)}</small>
              {item.supervisor_name && (
                <small>
                  {t('Supervised by {name} · Senior', {
                    name: item.supervisor_name,
                  })}
                </small>
              )}
            </span>
            <span className="barber-quote">
              <Price value={quoteFor(service, item.id)!} />
            </span>
          </label>
        ))}
      </fieldset>
      {eligible.length === 0 && (
        <p className="empty-state">
          {t(
            'No barbers currently offer this service. Choose another service.',
          )}
        </p>
      )}
      <div className="step-actions">
        <button className="button button-outline" onClick={onBack}>
          {t('Back')}
        </button>
        <button
          className="button button-dark"
          disabled={!eligible.some((item) => item.id === barberId)}
          onClick={onNext}
        >
          {t('Find a time')}
          <Arrow />
        </button>
      </div>
    </>
  )
}
