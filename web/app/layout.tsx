import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { QUESTION, REPO_URL, SITE_NAME, SITE_URL } from "@/lib/site";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: SITE_NAME, template: `%s · ${SITE_NAME}` },
  description: QUESTION,
  openGraph: {
    title: SITE_NAME,
    description: QUESTION,
    siteName: SITE_NAME,
    type: "website",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: SITE_NAME }],
  },
  twitter: { card: "summary_large_image" },
};

const NAV = [
  { href: "/explore", label: "Explore" },
  { href: "/radar", label: "Radar" },
  { href: "/method", label: "Method" },
];

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-sans">
        <header className="border-b border-zinc-200 dark:border-zinc-800">
          <nav
            aria-label="Main"
            className="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-x-6 gap-y-1 px-4 py-3"
          >
            <Link href="/" className="mr-auto font-semibold tracking-tight">
              {SITE_NAME}
            </Link>
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="py-1 text-sm text-zinc-700 hover:text-foreground dark:text-zinc-300"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:py-12">{children}</main>
        <footer className="border-t border-zinc-200 dark:border-zinc-800">
          <div className="mx-auto w-full max-w-5xl px-4 py-6 text-sm text-zinc-600 dark:text-zinc-400">
            <p>
              Built from public data: SEC Form D filings and Department of Labor LCA disclosure
              data. An LCA is an application step before an H-1B petition, not an approved visa or
              a hire.
            </p>
            <p className="mt-2">
              <Link href="/method" className="underline">
                How it works
              </Link>
              {" · "}
              <a href={REPO_URL} className="underline">
                Code on GitHub
              </a>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
