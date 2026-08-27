# Equipment Reservation App

Equipment rental and reservation application with a Django REST Framework
backend and a Next.js App Router frontend. It supports resource browsing,
reservations, OTP authentication, photo uploads, and Paystack payments.

## Project structure
- `backend/` — Django API, PostgreSQL models, admin dashboard, management
  commands, media storage, OTP email flow, and Paystack integration.
- `frontend/` — Next.js interface for browsing resources, authentication,
  booking equipment, and completing payments.

## API routes
- `GET /api/resources/` — browse active resources; supports `resource_type`
  and `category` filters.
- `GET /api/resources/<id>/` — view a resource.
- `GET /api/resources/<id>/availability/?start=...&end=...` — check availability.
- `GET/POST /api/reservations/` — list or create the authenticated user's
  reservations.
- `DELETE /api/reservations/<id>/` — cancel an authenticated user's reservation.
- `POST /api/auth/register/` — create an inactive account and send a signup OTP.
- `POST /api/auth/register/verify/` — verify the signup OTP and return a token.
- `POST /api/auth/login/` — validate credentials and send a login OTP.
- `POST /api/auth/login/verify/` — verify the login OTP and return a token.
- `POST /api/auth/otp/resend/` — resend a signup or login OTP.
- `GET /api/auth/me/` — return the authenticated user.
- `POST /api/payments/initialize/` — create a Paystack payment reference.
- `POST /api/payments/verify/` — verify a payment with Paystack.
- `POST /api/payments/webhook/` — receive signed Paystack payment events.

Resource and reservation mutations require token authentication. Public
catalogue and authentication routes are available without a token.

## Run the backend
```
cd backend
python -m venv venv        # or reuse the bundled venv on Windows
venv\Scripts\activate       # Windows PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # to add resources via /admin/
python manage.py seed_resources    # adds 10 sample equipment items with photos
python manage.py runserver
```
Requires a running PostgreSQL database configured by `backend/.env`.

For local development, the email backend defaults to Django's console backend,
so OTP messages are printed in the backend terminal. To deliver real emails,
configure SMTP settings in `backend/config/settings.py` and the environment,
for example:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-google-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Use a provider app password or SMTP credential, never a normal account
password. Keep these values out of Git.

## Run the frontend
```
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Opens on http://localhost:3000, talking to the API at http://localhost:8000/api.

## Authentication and admin

Registration and login use email OTP verification. The OTP service creates a
short-lived code, sends it to the user's email, and consumes it after a
successful verification. The default local console backend does not deliver
messages to an inbox; production deployments need SMTP configuration as
described above.

Create a local admin interactively:

```text
python manage.py createsuperuser
```

For deployments without shell access, `ensure_superuser` safely creates or
updates an admin from these environment variables:

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=use-a-secret-password
```

Run it with `python manage.py ensure_superuser`. The admin dashboard is at
`/admin/` and includes resources, reservations, users, and read-mostly payment
records.

## Pricing
Rental units are rounded up to the next whole hour or day. For a rental with
`units` and a resource rate of `price`:

```
subtotal = price * units
deposit = subtotal * 0.5
total_amount = subtotal
```

The booking form shows a live deposit estimate after start and end times are
selected. The backend recalculates the values when the reservation is created;
the backend values are authoritative. Paystack currently uses `total_amount`
and therefore charges the rental subtotal, while the security deposit remains
recorded separately on the reservation.

## Verified
- `python manage.py check` passes clean.
- `npm run build` compiles all routes with no errors (font fetch requires internet,
  which wasn't available in the sandbox — works normally on your machine).
- Pricing math spot-checked: hourly/daily rates round partial units up correctly,
  and the security deposit is 50% of the rental subtotal.

## Resource images and storage
`Resource` now has two photo-related fields:
- `image` — a real file upload (needs `Pillow`, added to `requirements.txt`)
- `image_url` — an optional link to a photo hosted elsewhere, used only as a
  fallback when no file has been uploaded

The API always returns one resolved `image_url` — an uploaded photo wins
over a linked one — so the frontend doesn't need to know which was used.

`python manage.py seed_resources` creates 10 camera/photography equipment
items with deterministic sample images. Re-running the command is safe; use
`python manage.py seed_resources --reset` to delete and recreate the seeded
items.

The API also serves committed demo images through `/seed-images/<path>` so they
survive deployments. Uploaded files are served from local `backend/media/`
when `DEBUG=True`.

For production, set `CLOUDINARY_URL`. The configured storage backend then
switches automatically to Cloudinary; without it, uploads use local disk and
can be lost when a host restarts or redeploys.

The Resource admin edit screen provides photo preview and upload controls.

## Payments — Paystack
Reservations get paid for via Paystack's **Inline** popup (`PayButton.jsx`
on the bookings page) so the customer never leaves the site.

1. Frontend calls `POST /api/payments/initialize/` with a `reservation_id`.
   Backend creates a `Payment` row (`apps/payments`) and hands back a
   reference, the amount in kobo/cents, and the Paystack public key.
2. Frontend opens the Paystack popup with those values. The customer pays
   with card / M-Pesa / bank transfer, whatever's enabled on the Paystack
   account.
3. On success, the frontend calls `POST /api/payments/verify/`, which
   re-checks the transaction directly against Paystack's API using the
   **secret** key — the popup's own "it worked" callback is never trusted
   on its own.
4. `POST /api/payments/webhook/` is the actual source of truth: Paystack
   calls it server-to-server on `charge.success`, independent of whether
   the customer's browser ever calls `verify`. The signature is checked
   (HMAC-SHA512 with the secret key) before anything is trusted.

Either route 3 or 4 arriving first marks the `Payment` as `success` and
flips the `Reservation` to `confirmed`; the other becomes a no-op.

**To go live:**
- Get real keys from the Paystack dashboard (Settings → API Keys &
  Webhooks) and put them in `backend/.env` as `PAYSTACK_PUBLIC_KEY` /
  `PAYSTACK_SECRET_KEY`. Test keys (`pk_test_...` / `sk_test_...`) work
  the same way against Paystack's sandbox — use those first.
- Register the webhook URL in the Paystack dashboard:
  `https://<your-domain>/api/payments/webhook/`. In local dev, a tool like
  `ngrok` can expose `localhost:8000` so Paystack can actually reach it.
- Payment records are visible (read-only) at `/admin/` under Payments —
  useful for support ("did this booking actually get paid?") without
  needing to log into Paystack.

## Not built yet (next steps)
- No admin-facing "add resource" flow in the Next.js app yet (use Django admin for now).
- Payments are captured in full at booking time; there's no partial deposit-only
  flow or refund handling yet.
- Invoices app is still an empty stub.
