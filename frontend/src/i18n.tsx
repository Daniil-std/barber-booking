import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { createTranslator } from './localization'
import type { Language, Translator } from './localization'
export { translateError } from './localization'
export type { Language } from './localization'

const I18nContext = createContext<{
  language: Language
  setLanguage: (value: Language) => void
  t: Translator
} | null>(null)

function savedLanguage(): Language {
  try {
    return localStorage.getItem('form-language') === 'pl' ? 'pl' : 'en'
  } catch {
    return 'en'
  }
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(savedLanguage)
  useEffect(() => {
    document.documentElement.lang = language
    try {
      localStorage.setItem('form-language', language)
    } catch {
      /* The selection still works when browser storage is unavailable. */
    }
  }, [language])
  const t = createTranslator(language)
  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  const value = useContext(I18nContext)
  if (!value) throw new Error('The language provider is missing.')
  return value
}

export function LanguageSwitcher() {
  const { language, setLanguage, t } = useI18n()
  return (
    <div
      className="language-switcher"
      role="group"
      aria-label={t('Site language')}
    >
      <button
        lang="en"
        aria-label="English"
        aria-pressed={language === 'en'}
        onClick={() => setLanguage('en')}
      >
        EN
      </button>
      <span aria-hidden="true">/</span>
      <button
        lang="pl"
        aria-label="Polski"
        aria-pressed={language === 'pl'}
        onClick={() => setLanguage('pl')}
      >
        PL
      </button>
    </div>
  )
}
