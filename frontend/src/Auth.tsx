import { useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from './api'
import { Arrow } from './components'
import { ErrorNotice, Field } from './Form'
import type { User } from './types'
import { useI18n } from './i18n'

export function Auth({
  onSuccess,
  initialMode = 'login',
  embedded = false,
}: {
  onSuccess: (user: User) => void
  initialMode?: 'login' | 'register'
  embedded?: boolean
}) {
  const { t } = useI18n()
  const [mode, setMode] = useState(initialMode)
  const [firstName, setFirstName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<unknown>(null)
  const [busy, setBusy] = useState(false)
  const pending = useRef(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (pending.current) return
    pending.current = true
    setBusy(true)
    setError(null)
    try {
      const session =
        mode === 'register'
          ? await api.register(firstName.trim(), email.trim(), password)
          : await api.login(email.trim(), password)
      if (session.user) onSuccess(session.user)
    } catch (failure) {
      setError(failure)
    } finally {
      pending.current = false
      setBusy(false)
    }
  }
  const content = (
    <>
      <p className="eyebrow">{t('YOUR FORM ACCOUNT')}</p>
      {embedded ? (
        <h3>
          {mode === 'login' ? t('Welcome back.') : t('Make yourself at home.')}
        </h3>
      ) : (
        <h1>
          {mode === 'login' ? t('Welcome back.') : t('Make yourself at home.')}
        </h1>
      )}
      <p className="page-description">
        {embedded
          ? t(
              'Sign in or create an account to keep your appointment in one place.',
            )
          : t('Your appointments, a little more organised.')}
      </p>
      <div className="auth-tabs" aria-label={t('Account access')}>
        <button
          aria-pressed={mode === 'login'}
          disabled={busy}
          onClick={() => {
            setMode('login')
            setError(null)
          }}
        >
          {t('Sign in')}
        </button>
        <button
          aria-pressed={mode === 'register'}
          disabled={busy}
          onClick={() => {
            setMode('register')
            setError(null)
          }}
        >
          {t('Create account')}
        </button>
      </div>
      <ErrorNotice error={error} />
      {mode === 'register' && (
        <p className="small-note">
          {t('Public demo — please use fictional contact details.')}
        </p>
      )}
      <form onSubmit={submit} className="auth-form">
        {mode === 'register' && (
          <Field
            label={t('First name')}
            name="first_name"
            autoComplete="given-name"
            required
            maxLength={100}
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            error={error}
            disabled={busy}
          />
        )}
        <Field
          label={t('Email address')}
          name="email"
          type="email"
          autoComplete="email"
          required
          maxLength={254}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={error}
          disabled={busy}
        />
        <Field
          label={t('Password')}
          name="password"
          type="password"
          autoComplete={
            mode === 'register' ? 'new-password' : 'current-password'
          }
          required
          minLength={mode === 'register' ? 10 : undefined}
          maxLength={128}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          hint={
            mode === 'register'
              ? t(
                  'At least 10 characters. Avoid common or all-numeric passwords.',
                )
              : undefined
          }
          error={error}
          disabled={busy}
        />
        <button className="button button-dark" disabled={busy} type="submit">
          {busy
            ? t('Just a moment…')
            : mode === 'login'
              ? t('Sign in')
              : t('Create account')}
          <Arrow />
        </button>
        <p className="small-note">
          {t(
            'Your account keeps your appointments and contact details in one place.',
          )}
        </p>
      </form>
    </>
  )
  return embedded ? (
    <div className="embedded-auth">{content}</div>
  ) : (
    <section className="account-access page-section">
      <a href="#" className="back-link">
        {t('← Back to the studio')}
      </a>
      {content}
    </section>
  )
}
