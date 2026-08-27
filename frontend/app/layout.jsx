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
        <header className="flex flex-nowrap items-center justify-between gap-2 px-3 py-4 sm:gap-0 sm:px-9 sm:py-5 border-b-2 border-fm-green-deep">
          <Link href="/" aria-label="Field Manual home" className="shrink-0 font-display text-[22px] tracking-wide sm:text-[26px]">
            <span className="sm:hidden">FM</span>
            <span className="hidden sm:inline">FIELD MANUAL</span>
          </Link>
          <nav className="flex min-w-0 justify-center gap-2 whitespace-nowrap text-[10px] font-semibold uppercase tracking-wide sm:gap-7 sm:text-[13px]">
            <Link href="/">Catalogue</Link>
            <Link href="/bookings">My permits</Link>
            <Link href="/login">Account</Link>
          </nav>
          <Link href="/" className="btn-solid shrink-0 whitespace-nowrap px-2 py-2 text-[12px] sm:px-5 sm:py-[11px] sm:text-[15px]">
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
