# Local verification

Executed October 7, 2026 in the prepared Windows workspace. These are local development results, not a deployment certification.

| Check | Result |
| --- | --- |
| Django integration tests on PostgreSQL 17.11 | 30 passed |
| `makemigrations --check --dry-run` | No changes detected |
| Django system check | No issues |
| Frontend localization and pricing tests | 7 passed |
| TypeScript check and Vite production build | Passed |
| Prettier source check | Passed |

Browser review used the installed Opera browser through the browser automation plugin. Explicit viewport overrides covered 320, 390, 768 and 1440 pixels; these simulate responsive widths and are not tests on physical devices.

Confirmed through the UI against the actual Django API:

- Registration with generated fictional test credentials.
- A 75-minute appointment saved for 10:00–11:15 Warsaw time, with confirmation and account listing.
- Switching Polish → English at review kept the chosen service, barber, time and customer details.
- Cancellation from the Polish account, followed by the Cancelled filter and success state.
- Sign-out from mobile navigation and successful sign-in afterwards.
- A malformed phone number displayed Polish client validation; an incorrect password displayed Polish server validation.
- Polish preference survived reload. Keyboard Tab/Enter reached and operated the language selector, with a visible focus outline.
- Both languages were visually reviewed at desktop/mobile widths, with the Polish layout also reviewed on tablet. Narrow headline wrapping was corrected after an overflow was observed.
- The updated desktop homepage showed Junior/Senior/Top Barber prices and the four-person team at 1440 pixels.
- Selecting Mika, Sam and Alex for the signature cut updated the booking total to 70, 100 and 140 PLN respectively.
- A new account booked a supervised training haircut through the Polish UI for 10:00–11:00 Warsaw time at 35 PLN. Confirmation and the mobile account at 390 pixels displayed Noah, supervising Senior Sam and the saved price.
- The training visit was cancelled through the Polish account and appeared in the Cancelled filter. The updated Polish homepage and service section were also reviewed at 320 pixels.
- Public portfolio notices and the asset credits link were absent from the reviewed homepage, booking and account UI. Attribution remains in `docs/ASSETS.md`.

Overlap, simultaneous requests, ownership, invalid input and released availability are verified by automated PostgreSQL tests. New tests cover 70/100/140 PLN tier snapshots, the derived 35 PLN training price, supervisor schedules/breaks/days off, cancellation releasing both staff, and API/direct ORM races between training and a regular Senior appointment. Browser review is manual and is not a checked-in browser regression suite. Docker setup, macOS/Linux setup, production hosting and physical mobile devices were not tested in this workspace. No administrator password was seeded; Admin's custom user creation was exercised by the backend test suite.
