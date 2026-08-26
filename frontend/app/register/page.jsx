"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import OtpForm from "@/components/OtpForm";
import { register, resendOtp, setToken, verifyRegisterOtp } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState("details"); // "details" | "otp"
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [userId, setUserId] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const result = await register(username, email, password);
      setUserId(result.user_id);
      setStep("otp");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVerify(code) {
    const { token } = await verifyRegisterOtp(userId, code);
    setToken(token);
    router.push("/bookings");
  }

  function handleResend() {
    return resendOtp(userId, "signup");
  }

  return (
    <section className="px-9 py-14 max-w-[380px]">
      <div className="eyebrow mb-3">Account</div>
      <h1 className="font-display text-[36px] mb-6">Create an account</h1>

      {step === "details" && (
        <form onSubmit={handleSubmit} className="permit-card">
          <label className="block text-xs font-semibold uppercase tracking-wide mb-1">
            Username
          </label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full border-2 border-fm-green-deep bg-white px-3 py-2 mb-3 text-sm"
          />

          <label className="block text-xs font-semibold uppercase tracking-wide mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border-2 border-fm-green-deep bg-white px-3 py-2 mb-3 text-sm"
          />

          <label className="block text-xs font-semibold uppercase tracking-wide mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border-2 border-fm-green-deep bg-white px-3 py-2 mb-4 text-sm"
          />

          {error && <p className="text-fm-rust text-sm mb-3">{error}</p>}

          <button type="submit" disabled={submitting} className="btn-solid w-full disabled:opacity-60">
            {submitting ? "Sending code…" : "Create account"}
          </button>
        </form>
      )}

      {step === "otp" && (
        <OtpForm email={email} onVerify={handleVerify} onResend={handleResend} />
      )}
    </section>
  );
}
