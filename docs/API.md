# API

Requests use JSON and same-origin session cookies. Fetch `/api/auth/session/` first and send its `csrfToken` as `X-CSRFToken` on POST requests. Login and registration return a fresh token. Appointment endpoints and logout require authentication; each customer can access only their own appointments.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health/` | Database readiness |
| GET | `/api/catalog/` | Services, barbers and prices |
| GET | `/api/availability/?service={id}&barber={id}&date={YYYY-MM-DD}` | Available start times |
| GET | `/api/auth/session/` | Current user and CSRF token |
| POST | `/api/auth/register/` | Register and sign in |
| POST | `/api/auth/login/` | Sign in |
| POST | `/api/auth/logout/` | Sign out |
| GET | `/api/appointments/` | List the customer's appointments |
| POST | `/api/appointments/` | Book an appointment |
| GET | `/api/appointments/{id}/` | Read the customer's appointment |
| POST | `/api/appointments/{id}/cancel/` | Cancel a future appointment |
