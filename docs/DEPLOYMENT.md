# Render deployment

1. Push the repository to GitHub.
2. In Render, create a Blueprint from `render.yaml`.
3. Review the two Free resources before applying the Blueprint.
4. Wait for the database and web service to deploy.
5. Open `/api/health/` on the assigned `onrender.com` URL.

The container runs migrations before Gunicorn starts. A migration or seed error stops the deployment.

`SEED_DEMO_DATA=True` refreshes the fictional services, staff and schedules on startup. The command is idempotent and does not create users or bookings. Change it to `False` after the first successful deploy if the catalog will be edited in Django Admin.

No shell command or pre-deploy job is required.

## Check the deployment

```sh
python scripts/smoke_http.py https://YOUR-SERVICE.onrender.com
python scripts/smoke_http.py https://YOUR-SERVICE.onrender.com --exercise-bookings
```

Use fictional contact details with the second command.

## Free tier limits

- The web service sleeps after 15 minutes without traffic and can take about one minute to wake up.
- The filesystem is temporary. PostgreSQL stores the application data.
- Free PostgreSQL has 1 GB of storage and expires after 30 days.
- A workspace can have one Free PostgreSQL database.
- Free web services have no shell access or one-off jobs.
