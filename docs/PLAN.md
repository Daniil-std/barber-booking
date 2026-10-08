# Implementation plan

1. **Foundation:** React, TypeScript and Vite; design tokens; responsive homepage; local licensed assets; keyboard focus and reduced motion support.
2. **Backend:** Django and DRF with PostgreSQL; services, barbers, working hours, breaks, days off and appointments; deterministic demo data; database-level overlap prevention.
3. **Integration:** real API catalog; service → barber → slot → details → confirmation; session authentication; customer account and cancellation.
4. **Quality:** booking, conflict, duration, cancellation, ownership, invalid-data and concurrency checks; frontend build and types; browser checks; architecture and limitations documentation.

No external deployment, payments, SMS or paid integrations are included.

## Implemented

All four stages are implemented. The application uses the real Django API and PostgreSQL. English/Polish website localization was added during the quality stage; code, API messages, Admin and documentation remain English.

Automated verification includes 30 backend tests, seven frontend tests, TypeScript checking, a production frontend build and migration/system checks. Browser review covers registration, booking, account cancellation, sign-in/out, keyboard language selection, persistent language preference and responsive layouts. No external deployment was performed.

The pricing update adds Junior/Senior/Top Barber tiers (70/100/140 PLN for the signature cut) and a 35 PLN supervised training haircut. Training reserves both staff members through database-maintained occupancy rows and exclusion constraints. Public portfolio notices and the credits page/link were removed; asset provenance remains in `docs/ASSETS.md`.
