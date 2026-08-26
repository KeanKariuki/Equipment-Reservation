"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { checkAvailability, createReservation, getToken } from "@/lib/api";

// datetime-local inputs give/take a naive "wall clock" string with no
// timezone info, interpreted by the browser as the user's local time.
// The API stores everything in UTC, so we convert explicitly at the
// boundary rather than sending the local string straight through --
// otherwise "10:00" typed in Nairobi (UTC+3) was silently saved as
// 10:00 UTC, three hours off from what the user actually picked.
function toISOString(localDateTimeValue) {
  if (!localDateTimeValue) return null;
  return new Date(localDateTimeValue).toISOString();
}

// For the `min` attribute on the inputs themselves, which needs the same
// naive local-wall-clock format the input works in (not UTC).
function nowAsLocalInputValue() {
  const d = new Date();
  d.setSeconds(0, 0);
  const offset = d.getTimezoneOffset();
  const local = new Date(d.getTime() - offset * 60000);
  return local.toISOString().slice(0, 16);
}

export default function BookingForm({ resource }) {
  const router = useRouter();
  const minStart = nowAsLocalInputValue();

  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [availability, setAvailability] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function getPricingEstimate() {
    if (!start || !end || end <= start) return null;

    const durationHours = (new Date(end) - new Date(start)) / (1000 * 60 * 60);
    const unitHours = resource.pricing_unit === "hour" ? 1 : 24;
    const units = Math.max(1, Math.ceil(durationHours / unitHours));
    const subtotal = Number(resource.price) * units;

    return {
      deposit: subtotal / 2,
      total: subtotal ,
    };
  }

  function validateWindow() {
    if (!start || !end) {
      setError("Pick a start and end time first.");
      return false;
    }
    if (start < minStart) {
      setError("Start time can't be in the past.");
      return false;
    }
    if (end <= start) {
      setError("End time has to be after the start time.");
      return false;
    }
    return true;
  }

  async function handleCheck() {
    setError("");
    setAvailability(null);
    if (!validateWindow()) return;

    try {
      const result = await checkAvailability(resource.id, toISOString(start), toISOString(end));
      setAvailability(result.available);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleReserve() {
    setError("");

    if (!getToken()) {
      router.push("/login");
      return;
    }

    if (!validateWindow()) return;

    setSubmitting(true);
    try {
      const reservation = await createReservation({
        resource_id: resource.id,
        start_datetime: toISOString(start),
        end_datetime: toISOString(end),
      });
      router.push(`/bookings?created=${reservation.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="permit-card max-w-[360px]">
      <div className="font-slab text-[11px] font-semibold uppercase tracking-wide text-fm-rust mb-1.5">
        Reserve this item
      </div>
      <h3 className="font-display text-2xl mb-1">{resource.name}</h3>
      <div className="text-[13px] text-fm-green-deep/70 mb-4">
        {resource.location || resource.category}
      </div>

      <label className="block text-xs font-semibold uppercase tracking-wide mb-1">
        Starts
      </label>
      <input
        type="datetime-local"
        value={start}
        min={minStart}
        onChange={(e) => setStart(e.target.value)}
        className="w-full border-2 border-fm-green-deep bg-white px-3 py-2 mb-3 text-sm"
      />

      <label className="block text-xs font-semibold uppercase tracking-wide mb-1">Ends</label>
      <input
        type="datetime-local"
        value={end}
        min={start || minStart}
        onChange={(e) => setEnd(e.target.value)}
        className="w-full border-2 border-fm-green-deep bg-white px-3 py-2 mb-4 text-sm"
      />

      <div className="flex gap-2 mb-3">
        <button type="button" onClick={handleCheck} className="btn-outline text-sm py-2 px-4">
          Check availability
        </button>
      </div>

      {availability === true && (
        <span className="status-tag mb-3 inline-block">Open for this window</span>
      )}
      {availability === false && (
        <span className="status-tag pending mb-3 inline-block">Already booked</span>
      )}

      {error && <p className="text-fm-rust text-sm mb-3">{error}</p>}

      <div className="border-t border-fm-line pt-3 mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span>Rate</span>
          <span>
            KES {Number(resource.price).toLocaleString()} / {resource.pricing_unit}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Security deposit</span>
          <span>
            {getPricingEstimate()
              ? `KES ${getPricingEstimate().deposit.toLocaleString()}`
              : "50% of rental subtotal"}
          </span>
        </div>
        {getPricingEstimate() && (
          <div className="flex justify-between text-sm mt-1 font-semibold">
            <span>Estimated total</span>
            <span>KES {getPricingEstimate().total.toLocaleString()}</span>
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={handleReserve}
        disabled={submitting}
        className="btn-solid w-full text-center disabled:opacity-60"
      >
        {submitting ? "Reserving…" : "Reserve now"}
      </button>
    </div>
  );
}
