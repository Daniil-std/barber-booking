# Upwork Portfolio Entry

**Project title:** Barber Booking Platform | Django, React & PostgreSQL

**Project type:** Personal Full-Stack Portfolio Project

## Project Description

I built a full-stack appointment booking application to demonstrate how a service business can present its catalog and turn customer selections into persistent reservations. Customers can browse services and barbers, see available times, create an account, book an appointment, and manage future cancellations. The interface supports English and Polish and adapts to desktop and mobile layouts.

The backend handles scheduling, input validation, account ownership, and historical pricing. PostgreSQL constraints and ordered transaction locks prevent overlapping reservations, including concurrent requests. Training appointments reserve both the trainee and an assigned Senior supervisor, so their availability must match for the full service duration.

The same-origin deployment preparation includes Gunicorn, WhiteNoise, complete Docker Compose, a Render Blueprint and GitHub Actions configuration. This is a personal portfolio project with a fictional brand, not paid client work. Public hosting and remote CI are pending; no customers, revenue or business results are claimed.

## Ready-to-paste description (120–180 words)

I built a full-stack appointment booking platform to demonstrate how a service business can turn its catalog into reliable, manageable reservations. Customers choose a service, barber and available time, create an account, confirm an appointment, and manage future cancellations through an English or Polish interface that adapts to desktop and mobile screens.

The Django REST API calculates availability from service duration, staff schedules, breaks, days off and existing bookings. PostgreSQL exclusion constraints, database triggers and ordered transaction locks prevent overlapping reservations, including simultaneous requests. Supervised training visits reserve both a trainee and Senior barber, while price and duration snapshots preserve appointment history after catalog updates.

My work covered frontend design, API integration, authentication, validation, scheduling, testing and deployment preparation. The repository includes a Docker image definition using Gunicorn and WhiteNoise, complete Compose configuration, a Render Blueprint, CI configuration and real application screenshots. This is a personal portfolio project with a fictional studio brand; public hosting and remote CI verification are pending.

## Short description (40–60 words)

Personal full-stack booking platform built with Django, React and PostgreSQL. Includes bilingual booking, customer accounts, cancellations, tiered pricing and supervised training appointments. Database constraints and transaction locks prevent overlapping reservations. Docker, Gunicorn, WhiteNoise, Render and CI configurations prepare the application for deployment. Real local screenshots are included; public hosting is pending.

**Skills/tags:** Python, Django, Django REST Framework, React, TypeScript, PostgreSQL, REST API, Docker, GitHub Actions, Full-Stack Development.

**Links:** Add GitHub/Live Demo only after real URLs exist and are verified. Never publish placeholders.

## Problem

Appointment availability depends on more than a free start time. A full service must fit inside a barber's shift without overlapping breaks, days off, or other appointments. A supervised visit also needs a second staff member, while simultaneous requests can compete for the same slot.

## Solution

A React booking flow uses server-calculated availability and prices from a Django REST API. The backend validates requests, locks participating staff in a consistent order, stores appointment snapshots, and uses PostgreSQL exclusion constraints as a final collision guarantee. Customers see clear feedback when a slot becomes unavailable.

## Main Features

- Registration, login/logout, session cookies, and CSRF-protected account actions.
- Service, barber, date, and time selection with persisted confirmation.
- Customer appointment history and cancellation of future bookings.
- Django Admin catalog, schedules, breaks, and days off.
- Junior/Senior/Top Barber prices and supervised training appointments.
- EN/PL localization and responsive layouts.

## Technical Challenges

- Modeling overlapping time ranges with half-open PostgreSQL intervals.
- Handling concurrent booking requests and direct ORM writes through ordered staff locks and exclusion constraints.
- Reserving trainee and supervisor availability together, then releasing both on cancellation.
- Applying Warsaw time/DST rules without silently shifting invalid local times.
- Retaining booked price/duration snapshots after catalog changes.
- Keeping a multi-step booking flow readable without changing its existing state or behavior.

## Technology Stack

React, TypeScript, Vite, Python, Django, Django REST Framework, PostgreSQL, psycopg, Gunicorn, WhiteNoise, Docker, full Compose, Render Blueprint, GitHub Actions configuration, Node's test runner, Django tests and Prettier.

## My Responsibilities

Full-stack implementation: frontend layout and localization, booking flow and API integration, backend models and endpoints, authentication and ownership checks, scheduling and concurrency protection, demo data, automated tests, and setup/documentation.

## Testing

44 backend tests and seven frontend tests passed, with types/build/format checks and actual HTTP registration, regular/training bookings and cancellation. Browser checks/screenshots use the actual API/PostgreSQL. Current results are in [FINAL_DEMO_REVIEW.md](FINAL_DEMO_REVIEW.md); historical checks are in [VERIFICATION.md](VERIFICATION.md).

## Possible Future Improvements

Finish remote CI/Docker verification, publish the approved GitHub repository and deploy the approved demo. This project intentionally stops there: payments, SMS, Redis, Celery and extra product features are outside its final scope. Browser CI and shared-cache throttling would require separate review if the demo were later scaled.
