import { polish } from './translations/pl.ts'

export type Language = 'en' | 'pl'
type Values = Record<string, string | number>
export type Translator = (text: string, values?: Values) => string

export function createTranslator(language: Language): Translator {
  return (text, values = {}) => {
    const translated = language === 'pl' ? polish[text] || text : text
    return translated.replace(/\{(\w+)\}/g, (_, key: string) =>
      String(values[key] ?? `{${key}}`),
    )
  }
}

export function translateError(text: string, language: Language): string {
  if (language === 'en' || Object.values(polish).includes(text)) return text
  if (polish[text]) return polish[text]
  const replacements: [RegExp, string][] = [
    [
      /Ensure this field has no more than (\d+) characters\./g,
      'Pole może zawierać maksymalnie $1 znaków.',
    ],
    [
      /Ensure this field has at least (\d+) characters\./g,
      'Pole musi zawierać co najmniej $1 znaków.',
    ],
    [
      /This password is too short\. It must contain at least (\d+) characters\./g,
      'Hasło jest za krótkie. Musi zawierać co najmniej $1 znaków.',
    ],
    [
      /Request was throttled\. Expected available in (\d+) seconds?\./g,
      'Zbyt wiele prób. Spróbuj ponownie za $1 sekund.',
    ],
    [
      /Invalid pk "\d+" - object does not exist\./g,
      'Wybrana usługa lub osoba nie jest już dostępna.',
    ],
  ]
  let output = text
  for (const [pattern, replacement] of replacements)
    output = output.replace(pattern, replacement)
  for (const [english, translated] of Object.entries(polish).sort(
    (a, b) => b[0].length - a[0].length,
  )) {
    if (english.includes('.') && output.includes(english))
      output = output.replaceAll(english, translated)
  }
  return output === text
    ? 'Nie udało się wykonać tej operacji. Sprawdź dane i spróbuj ponownie.'
    : output
}
