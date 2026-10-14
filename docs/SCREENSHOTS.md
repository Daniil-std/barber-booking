# Screenshot Checklist

Eight real captures are now included under `docs/screenshots/`, taken October 14, 2026 in headless Microsoft Edge. They show the actual local React production build served by Django + WhiteNoise, using real PostgreSQL, DEBUG=False and local HTTP. This server is Django's development server, not Linux Gunicorn; these images do not prove Render deployment.

Desktop viewport: 1440 × 1000 (full-page captures may be taller). Mobile: 390 × 844, a simulated viewport rather than a physical phone. Pricing is an element capture. All account details are fictional `@example.test` data. No browser chrome, credentials, developer logs or personal bookmarks are included. Confirmations show real saved visits; cancellation was exercised afterwards.

| File | Captured state |
| --- | --- |
| [01-homepage-desktop.png](screenshots/01-homepage-desktop.png) | English homepage, photo and booking CTA |
| [02-services-pricing.png](screenshots/02-services-pricing.png) | Real catalog, tiered prices and training |
| [03-barber-selection.png](screenshots/03-barber-selection.png) | Junior Mika and server-provided quote |
| [04-date-time-booking.png](screenshots/04-date-time-booking.png) | Actual available slots and selected Warsaw time |
| [05-booking-confirmation.png](screenshots/05-booking-confirmation.png) | Saved normal visit and appointment ID |
| [06-account-upcoming.png](screenshots/06-account-upcoming.png) | Fictional account, upcoming visit and cancel action |
| [07-mobile-booking-pl.png](screenshots/07-mobile-booking-pl.png) | Polish at 390 px; selection retained; no horizontal overflow |
| [08-training-confirmation.png](screenshots/08-training-confirmation.png) | Saved Noah + Sam visit; 60 minutes, 35 PLN |

Training replaces the optional eighth architecture image; Mermaid architecture is in README. After deployment, recapture and identify the new date/origin before describing images as live-demo captures.

## Checklist for recapture

Use fictional details and exclude private data and unrelated browser tabs.

| # | Capture | What should be visible |
| --- | --- | --- |
| 1 | Homepage / hero | FORM wordmark, main headline, real studio design asset, and booking call to action. A second homepage capture can show the service pricing tiers. |
| 2 | Service selection | Service names, descriptions, durations, minimum prices, selected service, and summary. Include the training option if space allows. |
| 3 | Barber selection | Eligible barbers, Junior/Senior/Top Barber labels, selected quote, and appointment summary. For a training example, show the trainee and supervisor information. |
| 4 | Date/time booking | A future working day, real API-returned slots, selected time, Warsaw timezone label, and summary. |
| 5 | Booking confirmation | Actual saved appointment ID, service, barber, date/time, price, and link to the account. For training, include the Senior supervisor. |
| 6 | Customer account / bookings | Fictional customer name, upcoming appointment, price, status, cancellation control, and account filters. An optional second capture can show a real cancelled test booking. |
| 7 | Mobile responsive view | A real narrow viewport showing navigation and a readable booking step or account card without horizontal overflow. |
| 8 | Optional architecture graphic | Render the Mermaid diagram from README, showing React, Django API/scheduling, PostgreSQL, and Admin. Label it as architecture, not a product screenshot. |

Capture at least one Polish view to demonstrate localization. Use consistent browser zoom and crop deliberately. Record the capture viewport; a simulated viewport is not proof of testing on a physical phone.

Save selected real captures under `docs/screenshots/` using names such as `homepage-desktop.png` and `booking-mobile-pl.png`. Add README image links only after those files exist. Do not substitute stock photos or generated mockups for screenshots of the working application.
