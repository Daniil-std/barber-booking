import { useI18n } from './i18n'

const zone = 'Europe/Warsaw'
export function addDays(value: string, count: number) {
  const day = new Date(`${value}T12:00:00Z`)
  day.setUTCDate(day.getUTCDate() + count)
  return day.toISOString().slice(0, 10)
}

export function useStudioDates() {
  const { language } = useI18n()
  const locale = language === 'pl' ? 'pl-PL' : 'en-GB'
  return {
    timeLabel: (value: string) =>
      new Intl.DateTimeFormat(locale, {
        timeZone: zone,
        hour: '2-digit',
        minute: '2-digit',
      }).format(new Date(value)),
    dateLabel: (value: string) =>
      new Intl.DateTimeFormat(locale, {
        timeZone: zone,
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      }).format(new Date(value)),
    shortDateLabel: (value: string) =>
      new Intl.DateTimeFormat(locale, {
        timeZone: zone,
        weekday: 'short',
        day: 'numeric',
        month: 'short',
      }).format(new Date(value)),
  }
}
