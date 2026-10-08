# API reference

Base path: `/api/`. JSON requests and responses. Catalog/availability/session are public; appointment endpoints require a session. Django Admin remains at `/admin/`.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `catalog/` | Active services and barbers, studio timezone, today's date and booking horizon |
| GET | `availability/?service=1&barber=1&date=2026-10-08` | ISO timestamps for available starts, respecting full service duration |
| GET | `auth/session/` | Current user (or null) and CSRF token |
| POST | `auth/register/` | Create account and sign in; returns HTTP 201 |
| POST | `auth/login/` | Sign in with email/password |
| POST | `auth/logout/` | End the session |
| GET | `appointments/` | Current customer's appointments |
| POST | `appointments/` | Create a validated reservation; returns HTTP 201 or 409 for a busy time |
| GET | `appointments/{id}/` | Current customer's appointment; another customer's ID returns 404 |
| POST | `appointments/{id}/cancel/` | Cancel a future appointment; repeated cancellation is idempotent |

Fetch `auth/session/` first. Keep the returned cookies and send the returned `csrfToken` as `X-CSRFToken` on POST requests. Registration and login rotate the token; use the new value from their response. The frontend handles this automatically through a same-origin Vite proxy. Send `Content-Type: application/json` for JSON bodies.

Registration body:

```json
{
  "first_name": "Jordan",
  "email": "jordan@example.test",
  "password": "<your unique test password>"
}
```

Login takes `email` and `password`. Passwords require ten characters and pass Django's common-password, similarity and numeric checks. The examples do not provide reusable credentials.

Appointment body (use current IDs and a future timestamp returned by availability):

```json
{
  "service": 1,
  "barber": 1,
  "starts_at": "2026-10-08T10:00:00+02:00",
  "contact_name": "Jordan Example",
  "contact_email": "jordan@example.test",
  "contact_phone": "+48 555 010 123",
  "notes": "Fictional demonstration contact details."
}
```

The server computes end time and snapshots price, duration, service name and barber level. Customers cannot submit ownership, status, price, duration, supervisor or end-time overrides. For training services, the server assigns the trainee's configured Senior and reserves both staff members for the full duration. Datetimes must include an offset; equivalent UTC timestamps are accepted. Contacts are required, phone numbers must contain 7–15 digits and supported punctuation, notes are optional up to 500 characters. Cancellation accepts an empty body or `{}`.

## Catalog pricing

Each service includes `price` (the Junior base or derived training price), `min_price`, `is_training` and `prices`. The `prices` list contains eligible barber quotes, for example:

```json
[
  {"barber_id": 2, "level": "junior", "price": "70.00"},
  {"barber_id": 3, "level": "senior", "price": "100.00"},
  {"barber_id": 1, "level": "top", "price": "140.00"}
]
```

Use IDs from the current catalog. Barber records include `level`, `level_label`, `supervisor` and `supervisor_name`. Supported levels are `junior`, `senior`, `top` and `trainee`. Training services only quote eligible trainees with an active Senior assigned to the reference service. Training prices are always 50% of that service's Junior price, rounded to two decimal places. Availability intersects both staff schedules, breaks, days off and reservations.

Appointment responses additionally include `barber_level`, `barber_level_label`, `supervisor` and `supervisor_name`. The request body is unchanged: supervision and price are server-controlled.

Errors use an `errors` object. Values may be strings, lists or nested field errors. Example HTTP 409:

```json
{"errors":{"detail":"This time is no longer available. Please choose another slot."}}
```

Malformed input returns 400; missing authentication/CSRF returns 403; unavailable or unowned records return 404; throttled requests return 429. A reservation that has already started cannot be cancelled. API text remains English; the frontend translates supported validation messages when Polish is selected.
