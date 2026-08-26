"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { cancelReservation, getMyReservations, getToken } from "@/lib/api";
import PayButton from "@/components/PayButton";

const STATUS_CLASS = {
  pending: "status-tag pending",
  confirmed: "status-tag",
  cancelled: "status-tag cancelled",
  completed: "status-tag",
};

export default function BookingsPage() {
  const router = useRouter();
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await getMyReservations();
      setReservations(data.results ?? data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(id) {
    try {
      await cancelReservation(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="px-9 py-14">
      <div className="eyebrow mb-3">Your permits</div>
      <h1 className="font-display text-[36px] mb-8">My bookings</h1>

      {loading && <p className="text-sm text-fm-green-deep/70">Loading…</p>}
      {error && <p className="text-fm-rust text-sm mb-4">{error}</p>}
      {!loading && reservations.length === 0 && !error && (
        <p className="text-sm text-fm-green-deep/70">No reservations yet — go browse the catalogue.</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {reservations.map((r) => (
          <div key={r.id} className="permit-card">
            <div className="font-slab text-[11px] font-semibold uppercase tracking-wide text-fm-rust mb-1.5">
              Permit No. {String(r.id).padStart(4, "0")}
            </div>
            <h3 className="font-display text-2xl mb-1">{r.resource.name}</h3>
            <div className="text-[13px] text-fm-green-deep/70 mb-3">
              {new Date(r.start_datetime).toLocaleString()} &rarr;{" "}
              {new Date(r.end_datetime).toLocaleString()}
            </div>
            <span className={STATUS_CLASS[r.status] || "status-tag"}>{r.status}</span>
            <div className="font-display text-xl mt-4">
              KES {Number(r.total_amount).toLocaleString()}
            </div>

            {r.status === "pending" && r.payment_status !== "success" && (
              <PayButton reservation={r} onPaid={load} />
            )}

            {(r.status === "pending" || r.status === "confirmed") && (
              <button
                type="button"
                onClick={() => handleCancel(r.id)}
                className="btn-outline text-sm py-1.5 px-3 mt-3"
              >
                Cancel
              </button>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
