import React from 'react'
import ReactDOM from 'react-dom/client'
import '@fontsource-variable/manrope'
import './styles.css'
import './booking.css'
import './language.css'
import './pricing.css'
import App from './App'
import { I18nProvider } from './i18n'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <I18nProvider>
      <App />
    </I18nProvider>
  </React.StrictMode>,
)
