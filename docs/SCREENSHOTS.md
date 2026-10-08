# Screenshot Checklist

Capture the actual local application after seeding the fictional catalog. Use fictional contact information and a test account. Keep credentials, developer logs, Admin secrets, and unrelated browser tabs out of screenshots. These are recommended captures; no screenshot files are included yet.

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
