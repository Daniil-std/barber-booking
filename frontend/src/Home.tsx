import { Arrow, Price, SectionLabel } from './components'
import type { Barber, Service } from './types'
import type { ReactNode } from 'react'
import { useI18n } from './i18n'

export function Home({
  services,
  barbers,
  onBook,
  catalogNotice,
}: {
  services: Service[]
  barbers: Barber[]
  onBook: (serviceId?: number, barberId?: number) => void
  catalogNotice?: ReactNode
}) {
  const { t } = useI18n()
  return (
    <>
      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">
            <span className="copper-line" />
            {t('A CONTEMPORARY BARBER STUDIO · WARSAW')}
          </p>
          <h1 id="hero-title">
            {t('Good hair.')}
            <br />
            {t('Great')} <span>{t('form.')}</span>
          </h1>
          <p className="hero-description">
            {t('A fresh perspective on the everyday ritual.')}
            <br className="desktop-break" />
            {t('Considered cuts. Good company. Time for you.')}
          </p>
          <button className="button button-copper" onClick={() => onBook()}>
            {t('Find your next cut')}
            <Arrow />
          </button>
          <div className="hero-footnote">
            <span>{t('CRAFTED AROUND YOU')}</span>
            <a href="#services" aria-label={t('Explore our services')}>
              {t('SCROLL TO EXPLORE')}
              <span aria-hidden="true">↓</span>
            </a>
          </div>
        </div>
        <figure className="hero-image">
          <img
            src="/images/studio.jpg"
            alt={t(
              'A leather barber chair beside a mirror in a warmly lit studio',
            )}
            width="1200"
            height="1500"
            fetchPriority="high"
          />
          <figcaption>
            <span>{t('A LITTLE TIME. A FRESH START.')}</span>
            <span>
              {t('THE FORM PERSPECTIVE')}
              <Arrow diagonal />
            </span>
          </figcaption>
          <span className="photo-label">{t('STUDIO INSPIRATION')}</span>
        </figure>
      </section>
      <div className="ritual-strip" aria-label={t('Our approach')}>
        <span>{t('YOUR STYLE.')}</span>
        <span className="strip-small">{t('OUR CRAFT.')}</span>
        <span>{t('GOOD FORM.')}</span>
        <span className="strip-note">
          {t('A considered approach to looking yourself.')}
        </span>
      </div>
      <section
        className="section services-section"
        id="services"
        aria-labelledby="services-title"
      >
        <div className="section-intro">
          <SectionLabel number="01">{t('THE MENU')}</SectionLabel>
          <h2 id="services-title">
            {t('Keep it sharp.')}
            <br />
            {t('Keep it')} <em>{t('you.')}</em>
          </h2>
          <p>
            {t('No unnecessary extras. Just good barbering,')}
            <br className="desktop-break" />
            {t('with time for the details that matter.')}
          </p>
          <p className="small-note">
            {t('Every service starts with a consultation.')}
            <br />
            {t('Prices in Polish złoty (PLN).')}
          </p>
          <div className="level-guide">
            <p className="eyebrow">{t('YOUR BARBER. YOUR LEVEL.')}</p>
            <p>{t('Junior · Senior · Top Barber')}</p>
            <p>{t('Choose your level. The price follows your barber.')}</p>
          </div>
        </div>
        <div className="service-list">
          {catalogNotice}
          {!catalogNotice && services.length === 0 && (
            <p className="empty-state">
              {t('The studio menu is being prepared. Please check back soon.')}
            </p>
          )}
          {services.map((service, index) => (
            <button
              className="service-row"
              key={service.id}
              onClick={() => onBook(service.id)}
              aria-label={t(
                'Book {service}, {duration} minutes, from {price} PLN',
                {
                  service: t(service.name),
                  duration: service.duration_minutes,
                  price: service.min_price,
                },
              )}
            >
              <span className="service-index">0{index + 1}</span>
              <span className="service-copy">
                <span className="service-name">{t(service.name)}</span>
                <span className="service-description">
                  {t(service.description)}
                </span>
                <span className="service-duration">
                  {service.duration_minutes} MIN
                  {service.is_training && (
                    <span className="training-tag">
                      {t('50% OFF · SENIOR SUPERVISION')}
                    </span>
                  )}
                </span>
                {!service.is_training && (
                  <span className="tier-prices">
                    {(['junior', 'senior', 'top'] as const).map((level) => {
                      const quote = service.prices.find(
                        (item) => item.level === level,
                      )
                      return (
                        quote && (
                          <span key={level}>
                            {t(
                              level === 'junior'
                                ? 'Junior'
                                : level === 'senior'
                                  ? 'Senior'
                                  : 'Top Barber',
                            )}{' '}
                            <Price value={quote.price} />
                          </span>
                        )
                      )
                    })}
                  </span>
                )}
              </span>
              <span className="service-price">
                {!service.is_training && (
                  <small className="price-from">{t('From')}</small>
                )}
                <Price value={service.min_price} />
                <span className="round-arrow">
                  <Arrow diagonal />
                </span>
              </span>
            </button>
          ))}
        </div>
      </section>
      <section
        className="studio-section"
        id="studio"
        aria-labelledby="studio-title"
      >
        <div className="studio-art">
          <img
            src="/images/studio.jpg"
            alt={t('Detail of the barber studio interior')}
            loading="lazy"
            width="1200"
            height="1500"
          />
          <span className="studio-art-caption">{t('ROOM TO SLOW DOWN.')}</span>
        </div>
        <div className="studio-copy">
          <SectionLabel number="02">{t('THE STUDIO')}</SectionLabel>
          <h2 id="studio-title">
            {t('A good cut.')}
            <br />
            {t('An unhurried')}
            <br />
            <em>{t('moment.')}</em>
          </h2>
          <p>
            {t(
              'Step out of the rush and into your own time. At FORM, a haircut deserves as much care as the space around it.',
            )}
          </p>
          <p>
            {t(
              'Honest conversations. Thoughtful details. A style that works long after you leave the chair.',
            )}
          </p>
          <div className="studio-details">
            <div>
              <span className="eyebrow">{t('THE SETTING')}</span>
              <p>{t('Warsaw, Poland')}</p>
            </div>
            <div>
              <span className="eyebrow">{t('THE RHYTHM')}</span>
              <p>
                {t('Mon–Fri · 10:00–19:00')}
                <br />
                {t('Saturday · 10:00–16:00')}
              </p>
            </div>
          </div>
          <p className="small-note">
            {t('Choose your barber and find a time that works for you.')}
          </p>
        </div>
      </section>
      <section
        className="section team-section"
        id="barbers"
        aria-labelledby="team-title"
      >
        <div className="section-heading">
          <div>
            <SectionLabel number="03">{t('BEHIND THE CHAIR')}</SectionLabel>
            <h2 id="team-title">{t('Find your person.')}</h2>
          </div>
          <p>
            {t('Different approaches. The same attention to you.')}
            <br />
            <span className="small-note">
              {t('From Junior to Top Barber. Find your fit.')}
            </span>
          </p>
        </div>
        {barbers.length === 0 && !catalogNotice && (
          <p className="empty-state">{t('Our team will be available soon.')}</p>
        )}
        <div className="team-grid">
          {barbers.map((barber, index) => (
            <article
              className={`barber-profile barber-${index}`}
              key={barber.id}
            >
              <div className="barber-monogram" aria-hidden="true">
                <span>{barber.initials}</span>
                <small>FORM / {String(index + 1).padStart(2, '0')}</small>
              </div>
              <div className="barber-title">
                <h3>{barber.name}</h3>
                <button
                  className="icon-button"
                  aria-label={t('Book with {name}', { name: barber.name })}
                  onClick={() => onBook(undefined, barber.id)}
                >
                  <Arrow diagonal />
                </button>
              </div>
              <p className="barber-role">{t(barber.role)}</p>
              <p className={`barber-level level-${barber.level}`}>
                {t(barber.level_label)}
              </p>
              <p className="barber-bio">{t(barber.bio)}</p>
              {barber.supervisor_name && (
                <p className="supervision-note">
                  {t('Supervised by {name} · Senior', {
                    name: barber.supervisor_name,
                  })}
                </p>
              )}
            </article>
          ))}
        </div>
      </section>
      <section className="booking-banner" aria-labelledby="cta-title">
        <div>
          <p className="eyebrow">{t('MAKE SOME TIME FOR YOURSELF')}</p>
          <h2 id="cta-title">{t('Your chair is waiting.')}</h2>
        </div>
        <button className="button button-light" onClick={() => onBook()}>
          {t('Book an appointment')}
          <Arrow />
        </button>
      </section>
    </>
  )
}
