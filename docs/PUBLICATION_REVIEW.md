# Publication Review

Historical October 8 report. Current commit, deployment preparation and screenshot status are recorded in [FINAL_DEMO_REVIEW.md](FINAL_DEMO_REVIEW.md). The legacy private ZIP and temporary audit tools mentioned below were subsequently removed during the owner's authorized size cleanup. Do not treat historical pre-commit status as current.

Reviewed October 8, 2026 in the Windows workspace, then reverified after the owner initialized and staged the independent project repository. No commit, push, Git-history rewrite, or external deployment was performed.

## 1. Changes made

- Rewrote README around confirmed features, architecture, local setup, tests, limitations, and personal-project status.
- Added Upwork portfolio copy and a real screenshot checklist.
- Added source-only packaging and Docker-context exclusions.
- Fixed Node 22 test execution, preserved the npm lockfile, and extended translation coverage to nested components.
- Hardened DEBUG parsing and whitespace handling for host/CSRF-origin lists, with four configuration regression tests.

## 2. Security issues fixed

`backend/.env` and environment variants are ignored; only placeholder examples are publishable. The existing local environment was preserved. No copy of its secret key or database password was found in the reviewed source.

The existing `barber-booking-under-512mb.zip` contains `backend/.env`, `.local/pg-password`, PostgreSQL data, dependencies, and generated files. It is now ignored and excluded from the clean package. It was kept locally because it contains project data. Do not share it.

The source package and a fresh snapshot of all 83 staged index blobs were scanned with Gitleaks 8.30.1 using full redaction: no leaks found. No staged blob contains the local Django secret key or database password. The current independent repository has zero commits; history, reflogs, and unreachable-object checks found no earlier commit. backend/.env has never been committed in this repository. This does not audit any separate older repository or shared archive.

## 3. Files/directories excluded from publication

`backend/.env`, `backend/.venv`, `frontend/node_modules`, `frontend/dist`, `.local`, `.tools`, `.vscode`, Python bytecode/caches, coverage/build output, and workspace ZIP files are ignored. They are absent from `barber-booking-source.zip`.

At the initial review, this folder used a parent Git repository and had no project index entries to remove. The owner subsequently initialized an independent repository here; the final index contains 83 legitimate source files and no forbidden generated/private paths. Developer dependencies, portable tools, and the local database were retained. The clean package is approximately 300 KB instead of the legacy archive's 187 MB compressed / 522 MB uncompressed.

## 4. Booking.tsx refactor

`frontend/src/Booking.tsx` decreased from **705 to 282 lines**. Seven typed components implement ServiceStep, BarberStep, DateTimeStep, DetailsStep, ReviewStep, BookingSummary, and BookingConfirmation.

State, request cancellation, slot refresh, validation, pending-submit protection, and error recovery stay in Booking.tsx. Existing shared types are reused. No dependency was added. Translation dictionaries, CSS, pricing helpers, backend scheduling/services/models, all migrations, and original backend tests remain byte-for-byte unchanged.

## 5. Backend test results

- Existing 30 tests passed on real PostgreSQL after starting the portable server.
- Final suite: **34 passed**, including four new settings tests.
- A fresh isolated Python 3.13.16 environment installed all eight pinned requirements successfully; its dependency check and full 34-test suite also passed.
- Django system check: no issues.
- `makemigrations --check --dry-run`: no changes detected.
- `migrate --check`: passed.
- No SQLite substitution or concurrency-constraint modification was made.

The installed Python launcher cannot locate Python 3.13 through py -3.13 on this machine; the prepared backend/.venv/Scripts/python.exe reports Python 3.13.16 and passed verification. The README fresh-clone commands require Python 3.13 installed and available to the launcher. The original environment had no pip module, so dependency verification used the installed uv tool. The fresh dependency install used:

```powershell
.tools/uv/uv.exe venv .local/portfolio-venv --python backend/.venv/Scripts/python.exe
.tools/uv/uv.exe pip install --python .local/portfolio-venv/Scripts/python.exe -r backend/requirements.txt
.tools/uv/uv.exe pip check --python .local/portfolio-venv/Scripts/python.exe
```

## 6. Frontend test results

Verified on **Node 22.12.0**, the declared minimum, and installed Node 24.11.0:

- `npm ci`: passed; npm reported zero dependency vulnerabilities.
- `npm test`: **7 passed**.
- `npm run typecheck`: passed.
- `npm run format:check`: passed.
- No lint script is configured.

A fresh extraction of the final source package also passed npm ci, all seven tests, type checking, build, and formatting on Node 22.12. Fresh-source environment generation and its no-overwrite behavior were verified.

Node 22.12 prints the expected experimental TypeScript-stripping warning; the test process succeeds. See [Node's flag documentation](https://nodejs.org/download/release/v22.12.0/docs/api/cli.html#--experimental-strip-types).

An initial second `npm ci` failed because the running Vite server held a native dependency open on Windows. Stopping that workspace server released the file; installation and all scripts then succeeded. The server was restarted.

## 7. Build and application results

Production frontend builds passed on Node 22.12 and 24.11. Django and Vite started locally.

Live Opera checks against the real API covered:

- Training service selection, eligible trainee Noah, supervising Senior Sam, and the 35 PLN total.
- Generated fictional local registration, contact details, review, and EN-to-PL switching without losing the selection.
- Saved training confirmation for 10:00–11:00 Warsaw time, account listing, cancellation, and the cancelled filter.
- Signature haircut totals of 70/100/140 PLN when switching Junior/Senior/Top Barber.
- DOM width checks with 320, 390, and 1440 pixel viewport overrides, with no horizontal overflow on the reviewed views.

Screenshot capture timed out, so this turn's browser checks used rendered DOM content and dimensions, not visual screenshot QA. They are not an automated browser regression suite or physical-device tests. The fictional account/appointment created for this review were removed afterwards; existing project data was preserved.

## 8. Docker verification

The workspace has a PostgreSQL-only `compose.yaml`, not application Dockerfiles. Its loopback binding, named data volume, required credentials, healthcheck, and host-side connection configuration were reviewed.

Docker Engine/CLI is not installed. A checksum-verified official standalone Docker Compose **5.6.0** binary successfully ran:

```powershell
.tools/compose/docker-compose.exe --env-file backend/.env config --quiet
```

Resolved credentials were not printed. The exact docker compose config command could not run because the Docker CLI is absent. Standalone Compose without --env-file also correctly rejected missing POSTGRES variables; the README-documented --env-file backend/.env form passed again. Container startup was not tested. The documented Docker workflow still needs a Docker-enabled machine. [Docker documents the standalone command](https://docs.docker.com/compose/install/standalone/).

## 9. Remaining issues

- The initial Git-boundary issue is resolved: the project now has its own .git directory. Its 83 indexed files passed secret/exclusion checks, and the new repository has no commit history. A separate older repository, if one exists, remains outside this audit.
- The legacy archive remains private and unsafe to publish.
- Real screenshots are still to be captured.
- Docker container startup, macOS/Linux setup, production hosting, and physical devices were not verified.
- Production features listed as future work in README remain unimplemented.

## 10. Manual publication actions

1. The owner has completed independent repository initialization and source staging. git rev-parse --show-toplevel now identifies barber-booking itself. Review the final staged files before the first commit.
2. Review `git status --short` and `git ls-files` in that actual repository. If a private environment is tracked there, `git rm --cached -- backend/.env` retains the developer file while removing its index entry.
3. The new repository has no commits to scan. If older history is imported later, audit all branches with a redacted scan: `gitleaks git --redact --log-opts="--all" .`. [Gitleaks documents Git scanning and redaction](https://github.com/gitleaks/gitleaks).
4. If the legacy archive or environment was ever shared or committed, rotate **DJANGO_SECRET_KEY** and the **PostgreSQL role password**. Update both the local environment and database role; changing only the environment does not rotate the database password. Rotate any other credentials discovered in the original history.
5. Capture the actual screenshots and run `docker compose --env-file backend/.env up -d --wait db` on a Docker-enabled machine before claiming Docker startup verification.

If secrets are found in history, rotate them first, back up the repository, coordinate with collaborators, and perform cleanup only after explicit approval in a fresh clone of the actual project. An example path-removal command is:

```text
git filter-repo --sensitive-data-removal --invert-paths --path backend/.env --path .local/ --path .tools/ --path barber-booking-under-512mb.zip
```

Include every historical path/rename found in the audit. A separate replacement strategy is needed for secrets embedded in legitimate source. Rewriting changes commit IDs and requires coordinated remote cleanup; forks/cached copies may remain. Follow [GitHub's sensitive-data removal process](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository). This command was **not executed**.

## 11. Publication readiness

The staged source and honest portfolio documentation are ready for public GitHub publication. The independent Git root is verified, all 83 index blobs passed the final secret audit, all requested frontend/backend checks passed, and the current repository has no commits containing secrets. Publish only the reviewed source. The whole workspace and legacy archive remain private; production deployment and Docker container startup were not verified.

## Git status and indexed source

Final pre-commit verification: 83 files staged as additions, no unstaged source changes, and no commits. The branch remains master; that is valid and does not affect publication readiness.

```text
A  .dockerignore
A  .editorconfig
A  .gitignore
A  README.md
A  backend/.env.example
A  backend/config/__init__.py
A  backend/config/settings.py
A  backend/config/urls.py
A  backend/config/wsgi.py
A  backend/manage.py
A  backend/requirements.in
A  backend/requirements.txt
A  backend/studio/__init__.py
A  backend/studio/admin.py
A  backend/studio/apps.py
A  backend/studio/exceptions.py
A  backend/studio/management/__init__.py
A  backend/studio/management/commands/__init__.py
A  backend/studio/management/commands/seed_demo.py
A  backend/studio/migrations/0001_initial.py
A  backend/studio/migrations/0002_staffreservation_appointment_barber_level_and_more.py
A  backend/studio/migrations/0003_staff_occupancy_trigger.py
A  backend/studio/migrations/0004_lock_staff_before_appointment.py
A  backend/studio/migrations/0005_service_valid_service_tier_prices.py
A  backend/studio/migrations/__init__.py
A  backend/studio/models.py
A  backend/studio/scheduling.py
A  backend/studio/serializers.py
A  backend/studio/services.py
A  backend/studio/tests/__init__.py
A  backend/studio/tests/test_booking.py
A  backend/studio/tests/test_settings.py
A  backend/studio/tests/test_training.py
A  backend/studio/urls.py
A  backend/studio/views.py
A  compose.yaml
A  docs/API.md
A  docs/ASSETS.md
A  docs/PLAN.md
A  docs/PORTFOLIO.md
A  docs/PUBLICATION_REVIEW.md
A  docs/SCREENSHOTS.md
A  docs/VERIFICATION.md
A  frontend/.env.example
A  frontend/.prettierrc.json
A  frontend/index.html
A  frontend/package-lock.json
A  frontend/package.json
A  frontend/public/favicon.svg
A  frontend/public/images/studio.jpg
A  frontend/src/Account.tsx
A  frontend/src/App.tsx
A  frontend/src/Auth.tsx
A  frontend/src/Booking.tsx
A  frontend/src/Form.tsx
A  frontend/src/Home.tsx
A  frontend/src/api.ts
A  frontend/src/booking.css
A  frontend/src/components.tsx
A  frontend/src/components/booking/BarberStep.tsx
A  frontend/src/components/booking/BookingConfirmation.tsx
A  frontend/src/components/booking/BookingSummary.tsx
A  frontend/src/components/booking/DateTimeStep.tsx
A  frontend/src/components/booking/DetailsStep.tsx
A  frontend/src/components/booking/ReviewStep.tsx
A  frontend/src/components/booking/ServiceStep.tsx
A  frontend/src/dates.ts
A  frontend/src/i18n.tsx
A  frontend/src/language.css
A  frontend/src/localization.ts
A  frontend/src/main.tsx
A  frontend/src/pricing.css
A  frontend/src/pricing.ts
A  frontend/src/styles.css
A  frontend/src/translations/pl.ts
A  frontend/src/types.ts
A  frontend/tests/localization.test.mjs
A  frontend/tests/pricing.test.mjs
A  frontend/tsconfig.json
A  frontend/vite.config.ts
A  scripts/create_local_env.py
A  scripts/package_source.py
A  scripts/start-local.ps1
```

`git ls-files` returned:

```text
.dockerignore
.editorconfig
.gitignore
README.md
backend/.env.example
backend/config/__init__.py
backend/config/settings.py
backend/config/urls.py
backend/config/wsgi.py
backend/manage.py
backend/requirements.in
backend/requirements.txt
backend/studio/__init__.py
backend/studio/admin.py
backend/studio/apps.py
backend/studio/exceptions.py
backend/studio/management/__init__.py
backend/studio/management/commands/__init__.py
backend/studio/management/commands/seed_demo.py
backend/studio/migrations/0001_initial.py
backend/studio/migrations/0002_staffreservation_appointment_barber_level_and_more.py
backend/studio/migrations/0003_staff_occupancy_trigger.py
backend/studio/migrations/0004_lock_staff_before_appointment.py
backend/studio/migrations/0005_service_valid_service_tier_prices.py
backend/studio/migrations/__init__.py
backend/studio/models.py
backend/studio/scheduling.py
backend/studio/serializers.py
backend/studio/services.py
backend/studio/tests/__init__.py
backend/studio/tests/test_booking.py
backend/studio/tests/test_settings.py
backend/studio/tests/test_training.py
backend/studio/urls.py
backend/studio/views.py
compose.yaml
docs/API.md
docs/ASSETS.md
docs/PLAN.md
docs/PORTFOLIO.md
docs/PUBLICATION_REVIEW.md
docs/SCREENSHOTS.md
docs/VERIFICATION.md
frontend/.env.example
frontend/.prettierrc.json
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/public/favicon.svg
frontend/public/images/studio.jpg
frontend/src/Account.tsx
frontend/src/App.tsx
frontend/src/Auth.tsx
frontend/src/Booking.tsx
frontend/src/Form.tsx
frontend/src/Home.tsx
frontend/src/api.ts
frontend/src/booking.css
frontend/src/components.tsx
frontend/src/components/booking/BarberStep.tsx
frontend/src/components/booking/BookingConfirmation.tsx
frontend/src/components/booking/BookingSummary.tsx
frontend/src/components/booking/DateTimeStep.tsx
frontend/src/components/booking/DetailsStep.tsx
frontend/src/components/booking/ReviewStep.tsx
frontend/src/components/booking/ServiceStep.tsx
frontend/src/dates.ts
frontend/src/i18n.tsx
frontend/src/language.css
frontend/src/localization.ts
frontend/src/main.tsx
frontend/src/pricing.css
frontend/src/pricing.ts
frontend/src/styles.css
frontend/src/translations/pl.ts
frontend/src/types.ts
frontend/tests/localization.test.mjs
frontend/tests/pricing.test.mjs
frontend/tsconfig.json
frontend/vite.config.ts
scripts/create_local_env.py
scripts/package_source.py
scripts/start-local.ps1
```

## Main changed files

- `.gitignore`, `.dockerignore`, `backend/.env.example`
- `backend/config/settings.py`, `backend/studio/tests/test_settings.py`
- `frontend/package.json`, `frontend/tests/localization.test.mjs`
- `frontend/src/Booking.tsx` and seven files under `frontend/src/components/booking/`
- `README.md`, `docs/PORTFOLIO.md`, `docs/SCREENSHOTS.md`, this report
- `scripts/package_source.py`

The source archive is generated and ignored; the npm lockfile and original application assets remain unchanged.
