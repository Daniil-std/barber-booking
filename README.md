# Barber Booking Platform

An appointment booking app for a fictional barber studio, built with Django, React and PostgreSQL.

## Features

- Customer registration, login and appointment history
- Service and barber selection
- Available slots based on shifts, breaks, days off and existing bookings
- Booking confirmation and cancellation of future visits
- Junior / Senior / Top pricing, saved with each appointment
- Training visits that reserve both a trainee and a Senior supervisor
- EN / PL interface and responsive layouts
- Django Admin for services, staff and schedules
- PostgreSQL protection against double booking, including simultaneous requests

## Stack

- Python 3.13, Django, Django REST Framework
- PostgreSQL 17
- React, TypeScript, Vite (Node >=22.12)
- Docker Compose, Gunicorn, WhiteNoise
- GitHub Actions
- [Manrope](https://fontsource.org/fonts/manrope) font, SIL Open Font License 1.1

## Screenshots

![Homepage](docs/screenshots/01-homepage-desktop.png)

![Training appointment confirmation](docs/screenshots/08-training-confirmation.png)

[All eight screenshots](docs/SCREENSHOTS.md) are from the local app, using fictional contact details.

Studio photo: [Redd Francisco](https://unsplash.com/photos/a-barber-shop-with-a-chair-and-a-mirror-BBGyxhtPpC0), [Unsplash License](https://unsplash.com/license).

## Run

Requires Docker Compose and Python 3 for the environment helper.

```sh
python scripts/create_local_env.py
docker compose --env-file backend/.env up --build -d --wait
docker compose --env-file backend/.env exec web python manage.py seed_demo
```

Open **http://127.0.0.1:8080**. Admin is at `/admin/`.

The helper preserves an existing `.env`. The seed adds fictional services, staff and schedules. Database data stays in a Docker volume. Use fictional details when trying registration and booking.

## Tests

Last local run: 44 backend tests and 7 frontend tests passed. With Compose running:

```sh
docker compose --env-file backend/.env exec web python manage.py test studio.tests --noinput
```

Frontend: from `frontend/`, run `npm ci`, `npm test`, `npm run typecheck`, `npm run build` and `npm run format:check`.

## Demo

No public demo yet. CI is configured; the remote run and Docker startup still need verification. Compose configuration was checked.

## Note

Personal portfolio project.
