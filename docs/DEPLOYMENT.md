# Render deployment

The [live demo](https://barber-booking-web.onrender.com/) runs on Render. For a new deployment, create a Blueprint from `render.yaml`, review the two Free resources, then check `/api/health/` on the assigned URL.

The Blueprint disables automatic deployments (`autoDeployTrigger: "off"`). Deploy a chosen commit manually after CI passes.

The container runs migrations before Gunicorn starts. A migration or seed error stops the deployment.

`SEED_DEMO_DATA=True` refreshes the fictional services, staff and schedules on startup. The command is idempotent and does not create users or bookings. Change it to `False` after the first successful deploy if the catalog will be edited in Django Admin.

No shell command or pre-deploy job is required.

Keep `DJANGO_SECRET_KEY` and database credentials in Render environment variables. Production uses PostgreSQL with SSL, HTTPS and secure cookies. Trust forwarded headers only behind a trusted proxy. Render supplies the exact hostname; set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` explicitly for custom domains.

## Check the deployment

```sh
python scripts/smoke_http.py https://barber-booking-web.onrender.com/
python scripts/smoke_http.py https://barber-booking-web.onrender.com/ --exercise-bookings
```

The second command creates a fictional account and two cancelled appointments. It leaves those records in the database.

## Free tier limits

- The web service sleeps after 15 minutes without traffic and can take about one minute to wake up.
- The filesystem is temporary. PostgreSQL stores the application data.
- Free PostgreSQL has 1 GB of storage and expires after 30 days.
- A workspace can have one Free PostgreSQL database.
- Free web services have no shell access or one-off jobs.

Check [Render's current limits](https://render.com/docs/free) before deploying. The database expiry can make the demo unavailable.
