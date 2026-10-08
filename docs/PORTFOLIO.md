# Upwork Portfolio Entry

**Project title:** Barber Booking Platform | Django, React & PostgreSQL

**Project type:** Personal Full-Stack Portfolio Project

## Project Description

I built a full-stack appointment booking application to demonstrate how a service business can present its catalog and turn customer selections into persistent reservations. Customers can browse services and barbers, see available times, create an account, book an appointment, and manage future cancellations. The interface supports English and Polish and adapts to desktop and mobile layouts.

The backend handles scheduling, input validation, account ownership, and historical pricing. PostgreSQL constraints and ordered transaction locks prevent overlapping reservations, including concurrent requests. Training appointments reserve both the trainee and an assigned Senior supervisor, so their availability must match for the full service duration.

This is a personal portfolio demonstration using a fictional FORM Barber Studio brand and fictional staff/catalog data. It was not paid client work and is not currently deployed as a production service. No claims about real customers, revenue, or business outcomes are made.

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

React, TypeScript, Vite, Python, Django, Django REST Framework, PostgreSQL, psycopg, Docker Compose for a local database, Node's test runner, Django test cases, and Prettier.

## My Responsibilities

Full-stack implementation: frontend layout and localization, booking flow and API integration, backend models and endpoints, authentication and ownership checks, scheduling and concurrency protection, demo data, automated tests, and setup/documentation.

## Testing

The project contains API/integration tests, database concurrency tests, settings tests, and frontend translation/pricing tests. TypeScript and production-build checks also run. Current executed results and limitations are recorded in [PUBLICATION_REVIEW.md](PUBLICATION_REVIEW.md); historical browser review is in [VERIFICATION.md](VERIFICATION.md).

## Possible Future Improvements

Email verification and password reset, reminders, rescheduling, payment integration, a waitlist, shared-cache throttling, automated browser regression tests, CI, and production hosting. These are future work, not existing features.
