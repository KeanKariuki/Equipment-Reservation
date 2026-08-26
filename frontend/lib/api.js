const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export function getToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("fm_token");
}

export function setToken(token) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("fm_token", token);
}

export function clearToken() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("fm_token");
}

async function request(path, { method = "GET", body, auth = false, cache } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Token ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    cache,
  });

  const isJson = res.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await res.json() : null;

  if (!res.ok) {
    const message = data?.detail || JSON.stringify(data) || res.statusText;
    throw new Error(message);
  }

  return data;
}

// Resources
export const getResources = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return request(`/resources/${query ? `?${query}` : ""}`, { cache: "no-store" });
};

export const getResource = (id) => request(`/resources/${id}/`, { cache: "no-store" });

export const checkAvailability = (id, start, end) =>
  request(`/resources/${id}/availability/?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`, {
    cache: "no-store",
  });

// Reservations
export const getMyReservations = () => request("/reservations/", { auth: true, cache: "no-store" });

export const createReservation = ({ resource_id, start_datetime, end_datetime }) =>
  request("/reservations/", {
    method: "POST",
    auth: true,
    body: { resource_id, start_datetime, end_datetime },
  });

export const cancelReservation = (id) =>
  request(`/reservations/${id}/`, { method: "DELETE", auth: true });

// Payments
export const initializePayment = (reservationId) =>
  request("/payments/initialize/", {
    method: "POST",
    auth: true,
    body: { reservation_id: reservationId },
  });

export const verifyPayment = (reference) =>
  request("/payments/verify/", {
    method: "POST",
    auth: true,
    body: { reference },
  });

// Auth
// Registration and login are now both two-step: the first call never
// returns a token, only a user_id and confirmation that a code was
// emailed. The token only comes back from the matching /verify/ call.
export const register = (username, email, password) =>
  request("/auth/register/", { method: "POST", body: { username, email, password } });

export const verifyRegisterOtp = (userId, code) =>
  request("/auth/register/verify/", { method: "POST", body: { user_id: userId, code } });

export const requestLogin = (username, password) =>
  request("/auth/login/", { method: "POST", body: { username, password } });

export const verifyLoginOtp = (userId, code) =>
  request("/auth/login/verify/", { method: "POST", body: { user_id: userId, code } });

export const resendOtp = (userId, purpose) =>
  request("/auth/otp/resend/", { method: "POST", body: { user_id: userId, purpose } });

export const getMe = () => request("/auth/me/", { auth: true, cache: "no-store" });
