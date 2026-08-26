"use client";

import { useState } from "react";

/**
 * Shared 6-digit code entry step, used after both registration and login.
 * `onVerify(code)` should throw on failure (the caller's request already
 * does, via lib/api.js), `onResend()` triggers a fresh code.
 */
export default function OtpForm({ email, onVerify, onResend }) {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [resending, setResending] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!/^\d{6}$/.test(code)) {
      setError("Enter the 6-digit code.");
      return;
    }
    setSubmitting(true);
    try {
      await onVerify(code);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleResend() {
    setError("");
    setInfo("");
    setResending(true);
    try {
      await onResend();
      setInfo("A new code has been sent.");
    } catch (err) {
      setError(err.message);
    } finally {
      setResending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="permit-card">
      <p className="text-sm mb-4">
        We sent a 6-digit code to <b>{email}</b>. It expires in a few minutes.
      </p>

      <label className="block text-xs font-semibold uppercase tracking-wide mb-1">
        Verification code
      </label>
      <input
        value={code}
        onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
        inputMode="numeric"
        maxLength={6}
        className="w-full border-2 border-fm-green-deep bg-white px-3 py-2 mb-4 text-sm tracking-[0.3em] text-center"
        placeholder="000000"
      />

      {error && <p className="text-fm-rust text-sm mb-3">{error}</p>}
      {info && <p className="text-sm mb-3">{info}</p>}

      <button type="submit" disabled={submitting} className="btn-solid w-full disabled:opacity-60 mb-2">
        {submitting ? "Verifying…" : "Verify"}
      </button>

      <button
        type="button"
        onClick={handleResend}
        disabled={resending}
        className="text-xs underline text-fm-green-deep/70 w-full text-center disabled:opacity-60"
      >
        {resending ? "Sending…" : "Resend code"}
      </button>
    </form>
  );
}
