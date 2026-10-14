# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PORT=8000
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 app
COPY --chown=app:app backend/ ./
COPY --chown=app:app --from=frontend /build/frontend/dist /app/frontend/dist
# A disposable build-only key; neither a runtime default nor an ENV layer.
# collectstatic needs settings, but never connects to a database.
RUN DJANGO_SECRET_KEY=collectstatic-build-only-not-a-runtime-secret python manage.py collectstatic --noinput \
    && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=8s --start-period=30s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/api/health/', timeout=5)"
CMD ["python", "start.py"]
