"use client";

import { useState } from "react";
import { initializePayment, verifyPayment } from "@/lib/api";

export default function PayButton({ reservation, onPaid }) {
  const [status, setStatus] = useState("idle"); // idle | opening | verifying | error
  const [error, setError] = useState("");

  async function handlePay() {
    setError("");
    setStatus("opening");

    let init;
    try {
      init = await initializePayment(reservation.id);
    } catch (err) {
      setError(err.message);
      setStatus("error");
      return;
    }

    if (typeof window === "undefined" || !window.PaystackPop) {
      setError("Payment isn't ready yet — give the page a second to finish loading and try again.");
      setStatus("error");
      return;
    }

    const handler = window.PaystackPop.setup({
      key: init.public_key,
      email: init.email,
      amount: init.amount_kobo,
      ref: init.reference,
      currency: "KES",
      onClose: () => {
        setStatus("idle");
      },
      callback: (response) => {
        // Runs after the popup reports success. We still re-verify against
        // Paystack server-side before trusting it (see VerifyPaymentView) —
        // this callback firing is not, by itself, proof of payment.
        setStatus("verifying");
        verifyPayment(response.reference)
          .then((result) => {
            setStatus("idle");
            if (result.reservation_status === "confirmed") {
              onPaid?.();
            } else {
              setError("Paystack hasn't confirmed this payment yet. It'll update automatically shortly — refresh in a moment.");
            }
          })
          .catch((err) => {
            setStatus("error");
            setError(err.message);
          });
      },
    });

    handler.openIframe();
  }

  return (
    <div className="mt-3">
      <button
        type="button"
        onClick={handlePay}
        disabled={status === "opening" || status === "verifying"}
        className="btn-solid text-sm py-1.5 px-3 disabled:opacity-60"
      >
        {status === "verifying" ? "Confirming…" : "Pay now"}
      </button>
      {error && <p className="text-fm-rust text-xs mt-2">{error}</p>}
    </div>
  );
}
