import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api'
import { LanguageSwitcher, useI18n } from './i18n'
import { Account } from './Account'
import { Auth } from './Auth'
import { Booking } from './Booking'
import { Arrow, Wordmark } from './components'
import { ErrorNotice, Loading } from './Form'
import { Home } from './Home'
import type { Catalog, User } from './types'

function currentRoute() {
  return window.location.hash.startsWith('#/')
    ? window.location.hash.slice(2)
    : 'home'
}

export default function App() {
  const { t, language } = useI18n()
  const [route, setRoute] = useState(currentRoute)
  const [menuOpen, setMenuOpen] = useState(false)
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [catalogError, setCatalogError] = useState<unknown>(null)
  const [catalogLoading, setCatalogLoading] = useState(true)
  const [user, setUser] = useState<User | null>(null)
  const [sessionLoading, setSessionLoading] = useState(true)
  const [sessionError, setSessionError] = useState<unknown>(null)
  const [reload, setReload] = useState(0)
  const [logoutBusy, setLogoutBusy] = useState(false)
  const [bookingKey, setBookingKey] = useState(0)
  const [initialChoice, setInitialChoice] = useState<{
    serviceId?: number
    barberId?: number
  }>({})
  const main = useRef<HTMLElement>(null)

  useEffect(() => {
    const changed = () => {
      setRoute(currentRoute())
      setMenuOpen(false)
    }
    window.addEventListener('hashchange', changed)
    return () => window.removeEventListener('hashchange', changed)
  }, [])
  useEffect(() => {
    document.title = `${t(route === 'home' ? 'FORM — Barber Studio' : route === 'book' ? 'Book your visit — FORM' : route === 'account' ? 'Your account — FORM' : 'Welcome — FORM')} · ${t('Warsaw')}`
  }, [route, language])
  useEffect(() => {
    if (route !== 'home') {
      window.scrollTo(0, 0)
      main.current?.focus({ preventScroll: true })
    }
  }, [route])
  useEffect(() => {
    const controller = new AbortController()
    setCatalogLoading(true)
    setCatalogError(null)
    setSessionLoading(true)
    setSessionError(null)
    api
      .catalog(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setCatalog(data)
      })
      .catch((error) => {
        if (!controller.signal.aborted) setCatalogError(error)
      })
      .finally(() => {
        if (!controller.signal.aborted) setCatalogLoading(false)
      })
    api
      .session(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setUser(data.user)
      })
      .catch((error) => {
        if (!controller.signal.aborted) setSessionError(error)
      })
      .finally(() => {
        if (!controller.signal.aborted) setSessionLoading(false)
      })
    return () => controller.abort()
  }, [reload])
  function book(serviceId?: number, barberId?: number) {
    setInitialChoice({ serviceId, barberId })
    setBookingKey((value) => value + 1)
    window.location.hash = '/book'
  }
  const signedOut = useCallback(() => {
    setUser(null)
    window.location.hash = '/login'
  }, [])
  async function logout() {
    if (logoutBusy) return
    setLogoutBusy(true)
    setSessionError(null)
    try {
      await api.logout()
      setUser(null)
      window.location.hash = ''
    } catch (error) {
      setSessionError(error)
    } finally {
      setLogoutBusy(false)
    }
  }
  const catalogNotice = catalogLoading ? (
    <Loading>{t('Loading the studio menu…')}</Loading>
  ) : catalogError ? (
    <ErrorNotice
      error={catalogError}
      onRetry={() => setReload((value) => value + 1)}
    />
  ) : null
  return (
    <>
      <a
        className="skip-link"
        href="#main"
        onClick={(event) => {
          event.preventDefault()
          main.current?.focus()
        }}
      >
        {t('Skip to content')}
      </a>
      <header className="site-header">
        <a href="#" aria-label={t('FORM home')}>
          <Wordmark />
        </a>
        <nav
          id="main-navigation"
          className={menuOpen ? 'main-nav is-open' : 'main-nav'}
          aria-label={t('Main navigation')}
        >
          <a href="#services" onClick={() => setMenuOpen(false)}>
            {t('Services')}
          </a>
          <a href="#studio" onClick={() => setMenuOpen(false)}>
            {t('The studio')}
          </a>
          <a href="#barbers" onClick={() => setMenuOpen(false)}>
            {t('Our barbers')}
          </a>
          <a className="mobile-account" href={user ? '#/account' : '#/login'}>
            {user ? t('My account') : t('Sign in')}
          </a>
          {user && (
            <button
              className="mobile-account mobile-logout"
              disabled={logoutBusy}
              onClick={() => {
                setMenuOpen(false)
                void logout()
              }}
            >
              {logoutBusy ? t('Signing out…') : t('Sign out')}
            </button>
          )}
        </nav>
        <div className="header-actions">
          <LanguageSwitcher />
          {user ? (
            <>
              <a className="account-link" href="#/account">
                {t('My account')}
              </a>
              <button
                className="logout-link"
                disabled={logoutBusy}
                onClick={logout}
              >
                {logoutBusy ? t('Signing out…') : t('Sign out')}
              </button>
            </>
          ) : (
            <a className="account-link" href="#/login">
              {t('Sign in')}
            </a>
          )}
          <button
            className="button button-small button-copper"
            onClick={() => book()}
          >
            {t('Book a visit')}
            <Arrow diagonal />
          </button>
          <button
            className="menu-toggle icon-button"
            aria-label={menuOpen ? t('Close menu') : t('Open menu')}
            aria-expanded={menuOpen}
            aria-controls="main-navigation"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? '✕' : '☰'}
          </button>
        </div>
      </header>
      <main id="main" ref={main} tabIndex={-1}>
        {Boolean(sessionError) && (
          <div className="session-notice">
            <ErrorNotice
              error={sessionError}
              onRetry={() => setReload((value) => value + 1)}
            />
          </div>
        )}
        {route === 'home' ? (
          <Home
            services={catalog?.services || []}
            barbers={catalog?.barbers || []}
            catalogNotice={catalogNotice}
            onBook={book}
          />
        ) : route === 'book' ? (
          catalogLoading || !catalog ? (
            <section className="page-section">{catalogNotice}</section>
          ) : (
            <Booking
              key={bookingKey}
              catalog={catalog}
              user={user}
              onUser={setUser}
              initialService={initialChoice.serviceId}
              initialBarber={initialChoice.barberId}
            />
          )
        ) : route === 'account' ? (
          sessionLoading ? (
            <section className="page-section">
              <Loading>{t('Loading your account…')}</Loading>
            </section>
          ) : user ? (
            <Account user={user} onSignedOut={signedOut} />
          ) : (
            <Auth
              onSuccess={(account) => {
                setUser(account)
                window.location.hash = '/account'
              }}
            />
          )
        ) : route === 'login' || route === 'register' ? (
          user ? (
            <section className="page-section">
              <h1>{t("You're signed in.")}</h1>
              <a className="button button-dark" href="#/account">
                {t('Go to my account')}
                <Arrow />
              </a>
            </section>
          ) : (
            <Auth
              key={route}
              initialMode={route === 'register' ? 'register' : 'login'}
              onSuccess={(account) => {
                setUser(account)
                window.location.hash = '/account'
              }}
            />
          )
        ) : (
          <section className="page-section">
            <h1>{t('This page took a wrong turn.')}</h1>
            <a className="text-link" href="#">
              {t('Back to the studio')}
              <Arrow />
            </a>
          </section>
        )}
      </main>
      <footer className="site-footer">
        <div className="footer-top">
          <a href="#" aria-label={t('Back to FORM home')}>
            <Wordmark />
          </a>
          <p>
            {t('Good hair. Great form.')}
            <br />
            <span>{t('Warsaw · Europe/Warsaw')}</span>
          </p>
          <a className="text-link" href="#services">
            {t('Explore the services')}
            <Arrow diagonal />
          </a>
        </div>
        <div className="footer-bottom">
          <p>
            © {new Date().getFullYear()} {t('FORM — Barber Studio')}
          </p>
          <p>{t('Appointments · Europe/Warsaw')}</p>
        </div>
      </footer>
    </>
  )
}
