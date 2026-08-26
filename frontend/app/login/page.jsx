"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import OtpForm from "@/components/OtpForm";
import { requestLogin, resendOtp, setToken, verifyLoginOtp } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [step, setStep] = useState("credentials"); // "credentials" | "otp"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [userId, setUserId] = useState(null);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleCredentials(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const result = await requestLogin(username, password);
      setUserId(result.user_id);
      setEmail(result.email);
      setStep("otp");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVerify(code) {
    const { token } = await verifyLoginOtp(userId, code);
    setToken(token);
    router.push("/bookings");
  }

  function handleResend() {
    return resendOtp(userId, "login");
  }

  return (
    <section className="px-9 py-14 max-w-[380px]">
      <div className="eyebrow mb-3">Account</div>
      <h1 className="font-display text-[36px] mb-6">Sign in</h1>

      {step === "credentials" && (
        <>
          <form onSubmit={handleCredentials} className="permit-card">
            <label className="block text-xs font-semibold uppercase tracking-wide mb-1">
              Username
            </label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
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
              {submitting ? "Checking…" : "Continue"}
            </button>
          </form>

          <p className="text-sm mt-4">
            No account yet?{" "}
            <Link href="/register" className="underline">
              Register
            </Link>
          </p>
        </>
      )}

      {step === "otp" && (
        <OtpForm email={email} onVerify={handleVerify} onResend={handleResend} />
      )}
    </section>
  );
}
