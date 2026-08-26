# Equipment Reservation App — Django + Next.js (Field Manual design)

## What changed
- **backend/** — added a real REST API (Django REST Framework):
  - `GET /api/resources/` — browse resources (`?resource_type=` and `?category=` filters)
  - `GET /api/resources/<id>/availability/?start=...&end=...` — availability check
  - `GET/POST /api/reservations/`, `DELETE /api/reservations/<id>/` (cancel) — requires auth
  - `POST /api/auth/register/`, `POST /api/auth/token/`, `GET /api/auth/me/` — token auth
  - `reservation_service.py` computes the rental `subtotal` from the resource's
    hourly/daily rate (rounds partial units up), and sets `security_deposit` to
    50% of that subtotal. The deposit is stored separately; `total_amount`
    currently represents the rental subtotal used for payment.
  - CORS is configured for `http://localhost:3000`.
- **frontend/** — Next.js (App Router) frontend in the "Field Manual" design.

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
Requires a running PostgreSQL matching `backend/.env`.

## Run the frontend
```
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Opens on http://localhost:3000, talking to the API at http://localhost:8000/api.

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

## Sample photos
`Resource` now has two photo-related fields:
- `image` — a real file upload (needs `Pillow`, added to `requirements.txt`)
- `image_url` — an optional link to a photo hosted elsewhere, used only as a
  fallback when no file has been uploaded

The API always returns one resolved `image_url` — an uploaded photo wins
over a linked one — so the frontend doesn't need to know which was used.

`python manage.py seed_resources` creates 10 camera/photography equipment
items (mirrorless body, lenses, gimbal, lighting kit, drone, etc.) using
placeholder photos from picsum.photos so the catalogue isn't empty out of
the box. Each item's placeholder is deterministic (same item = same photo),
so re-running the command is safe. Run with `--reset` to delete and
recreate the seeded items.

Uploaded photos are saved to `backend/media/` and served locally in dev via
`config/urls.py`. **For production, don't rely on local disk storage** —
swap in a real storage backend (e.g. `django-storages` with S3/Cloudinary)
so uploads survive deploys.

## Admin dashboard — no developer needed for day-to-day updates
`/admin/` is reskinned to match the frontend's "Field Manual" look (same
colors, same fonts) so it feels like part of the product rather than a
separate tool. The Resource edit screen leads with a photo preview and an
upload button — whoever runs the day-to-day catalogue can add or swap a
photo, change a price, or mark something inactive without touching code.
Create their login with `python manage.py createsuperuser`.

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
