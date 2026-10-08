import type { InputHTMLAttributes } from 'react'
import { ApiError, errorText } from './api'
import { translateError, useI18n } from './i18n'

export function ErrorNotice({
  error,
  onRetry,
}: {
  error: unknown
  onRetry?: () => void
}) {
  const { language, t } = useI18n()
  if (!error) return null
  return (
    <div className="error-notice" role="alert">
      <p>{translateError(errorText(error), language)}</p>
      {onRetry && (
        <button className="text-link" onClick={onRetry}>
          {t('Try again')}
        </button>
      )}
    </div>
  )
}
export function Loading({ children = 'Loading…' }: { children?: string }) {
  const { t } = useI18n()
  return (
    <p className="loading-state" role="status">
      <span aria-hidden="true" className="loading-dot" />
      {t(children)}
    </p>
  )
}
export function Field({
  label,
  name,
  hint,
  error,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label: string
  name: string
  hint?: string
  error?: unknown
}) {
  const { language } = useI18n()
  const message = error instanceof ApiError ? error.field(name) : ''
  const descriptions = [hint && `${name}-hint`, message && `${name}-error`]
    .filter(Boolean)
    .join(' ')
  return (
    <div className="form-field">
      <label htmlFor={name}>{label}</label>
      <input
        {...props}
        id={name}
        name={name}
        aria-invalid={Boolean(message)}
        aria-describedby={descriptions || undefined}
      />
      {hint && (
        <p className="field-hint" id={`${name}-hint`}>
          {hint}
        </p>
      )}
      {message && (
        <p className="field-error" id={`${name}-error`}>
          {translateError(message, language)}
        </p>
      )}
    </div>
  )
}
