import type { Metadata } from "next";
import Link from "next/link";
import { PageTitle } from "@/components/ui";
import { loadRadar } from "@/lib/data";
import { city, day, money } from "@/lib/format";

export const metadata: Metadata = {
  title: "Radar: recently funded startups that have sponsored before",
  description:
    "A weekly ranked list of Bay Area startups that just filed a Form D, scored by their H-1B filing history.",
  openGraph: { title: "Radar · Funded & Sponsoring" },
};

export default function RadarPage() {
  const radar = loadRadar();
  return (
    <>
      <PageTitle
        title="Radar"
        lead={
          <>
            Bay Area startups that filed a Form D in the last {radar.days ?? 30} days, ranked by
            how likely they are to file for H-1B workers, based on what they have filed before.
            The score runs from 0 to 100; <Link href="/method#radar" className="underline">how it
            is worked out</Link>.
          </>
        }
      />
      <p className="text-sm text-zinc-600 dark:text-zinc-400" data-testid="radar-generated">
        {radar.generated ? `Generated ${day(radar.generated)}. Updated every Monday.` : null}
      </p>

      {radar.rows.length === 0 ? (
        <p className="mt-6">The first radar has not been generated yet.</p>
      ) : (
        <ol className="mt-6 divide-y divide-zinc-200 dark:divide-zinc-800">
          {radar.rows.map((row) => (
            <li key={row.accession} className="flex gap-4 py-4">
              <div
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg border border-zinc-300 text-lg font-semibold tabular-nums dark:border-zinc-700"
                aria-label={`Score ${row.score} out of 100`}
              >
                {row.score}
              </div>
              <div className="min-w-0">
                <h2 className="font-semibold">
                  {row.slug ? (
                    <Link href={`/company/${row.slug}`} className="underline">
                      {row.company}
                    </Link>
                  ) : (
                    row.company
                  )}
                </h2>
                <p className="text-sm text-zinc-700 dark:text-zinc-300">
                  {city(row.city)} · {row.industry ?? "Industry not given"} · raised{" "}
                  {row.amount_sold ? money(row.amount_sold) : "an undisclosed amount"}, filed{" "}
                  {day(row.filing_date)}
                </p>
                <p className="mt-1 text-sm">{row.reasons}</p>
                <p className="mt-1 text-sm">
                  <a href={row.sec_url} className="underline">
                    Form D on SEC EDGAR
                  </a>
                </p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </>
  );
}
