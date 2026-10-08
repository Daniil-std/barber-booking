import type { ReactNode } from 'react'
import { useI18n } from './i18n'

export function Arrow({ diagonal = false }: { diagonal?: boolean }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d={diagonal ? 'M6 18 18 6M6 6h12v12' : 'M4 12h16m-6-6 6 6-6 6'}
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  )
}

export function Wordmark() {
  return (
    <span className="wordmark">
      FORM<span>.</span>
      <small>BARBER STUDIO</small>
    </span>
  )
}

export function SectionLabel({
  number,
  children,
}: {
  number: string
  children: ReactNode
}) {
  return (
    <p className="eyebrow section-label">
      <span>{number}</span>
      {children}
    </p>
  )
}

export function Price({ value }: { value: string }) {
  const { language } = useI18n()
  const amount = Number(value)
  return (
    <>
      {new Intl.NumberFormat(language === 'pl' ? 'pl-PL' : 'en-GB', {
        minimumFractionDigits: amount % 1 ? 2 : 0,
        maximumFractionDigits: 2,
      }).format(amount)}{' '}
      <span className="currency">PLN</span>
    </>
  )
}
