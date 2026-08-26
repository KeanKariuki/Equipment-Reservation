import { Bebas_Neue, Zilla_Slab, Work_Sans } from "next/font/google";
import Script from "next/script";
import Link from "next/link";
import "./globals.css";

const display = Bebas_Neue({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
});

const slab = Zilla_Slab({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-slab",
});

const body = Work_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body",
});

export const metadata = {
  title: "Field Manual — Equipment & Space Reservations",
  description: "Book equipment and spaces by permit — Nairobi.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${slab.variable} ${body.variable} font-body`}>
        {/* Paystack's Inline popup script. Loaded once, globally, so the
            Pay Now button on the bookings page can call window.PaystackPop
            without worrying about load timing. */}
        <Script src="https://js.paystack.co/v1/inline.js" strategy="afterInteractive" />
        <header className="flex items-center justify-between px-9 py-5 border-b-2 border-fm-green-deep">
          <Link href="/" className="font-display text-[26px] tracking-wide">
            FIELD MANUAL
          </Link>
          <nav className="flex gap-7 text-[13px] font-semibold uppercase tracking-wide">
            <Link href="/">Catalogue</Link>
            <Link href="/bookings">My permits</Link>
            <Link href="/login">Account</Link>
          </nav>
          <Link href="/" className="btn-solid">
            Reserve gear
          </Link>
        </header>

        <main>{children}</main>

        <footer className="border-t-2 border-fm-green-deep px-9 py-5 font-slab text-xs uppercase tracking-wide flex justify-between text-fm-green-deep/80">
          <span>Field Manual — Equipment Reservation</span>
          <span>Nairobi, Kenya</span>
        </footer>
      </body>
    </html>
  );
}
