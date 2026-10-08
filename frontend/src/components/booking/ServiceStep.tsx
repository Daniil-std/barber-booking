import { Arrow, Price } from '../../components'
import { useI18n } from '../../i18n'
import type { Catalog, Service } from '../../types'

interface ServiceStepProps {
  catalog: Pick<Catalog, 'services'>
  serviceId: number | undefined
  service: Service | undefined
  onSelect: (id: number) => void
  onNext: () => void
}

export function ServiceStep({
  catalog,
  serviceId,
  service,
  onSelect,
  onNext,
}: ServiceStepProps) {
  const { t } = useI18n()
  return (
    <>
      <p className="step-description">
        {t('A consultation is included. Prices are in PLN.')}{' '}
        {t('The final price depends on your barber’s level.')}
      </p>
      <fieldset className="choice-list">
        <legend className="sr-only">{t('Choose a service')}</legend>
        {catalog.services.map((item) => (
          <label className="service-choice" key={item.id}>
            <input
              type="radio"
              name="service"
              checked={serviceId === item.id}
              onChange={() => onSelect(item.id)}
            />
            <span>
              <strong>{t(item.name)}</strong>
              <small>{t(item.description)}</small>
              <span className="choice-meta">
                {item.duration_minutes} MIN
                {item.is_training && (
                  <span className="training-tag">
                    {t('50% OFF · SENIOR SUPERVISION')}
                  </span>
                )}
              </span>
            </span>
            <span className="choice-price">
              {!item.is_training && (
                <small className="price-from">{t('From')}</small>
              )}
              <Price value={item.min_price} />
            </span>
          </label>
        ))}
      </fieldset>
      {catalog.services.length === 0 && (
        <p className="empty-state">
          {t('No services are available yet. Please check back soon.')}
        </p>
      )}
      <div className="step-actions">
        <button
          className="button button-dark"
          disabled={!service}
          onClick={onNext}
        >
          {t('Choose a barber')}
          <Arrow />
        </button>
      </div>
    </>
  )
}
