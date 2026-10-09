import type { Metadata } from "next";
import Link from "next/link";
import { RateBars } from "@/components/RateBars";
import { Section, Stat } from "@/components/ui";
import { loadFindings, loadMetrics, loadRadar } from "@/lib/data";
import { count, day, pct } from "@/lib/format";
import { QUESTION } from "@/lib/site";

export const metadata: Metadata = {
  title: { absolute: "Funded & Sponsoring: which funded Bay Area startups file for H-1B workers" },
  description: QUESTION,
};

export default function Home() {
  const { findings, coverage, match_quality: quality } = loadFindings();
  const metrics = loadMetrics();
  const radar = loadRadar();

  const headline = metrics.mart_sponsor_rate.find((r) => r.metric === "any")!;
  const rounds = metrics.mart_by_round;
  const known = rounds.filter((r) => r.round_bin !== "unknown");
  const topRound = known.reduce((a, b) => (b.sponsor_rate > a.sponsor_rate ? b : a));
  const before = metrics.mart_by_history.find((r) => r.history === "sponsored_before")!;
  const never = metrics.mart_by_history.find((r) => r.history === "no_prior")!;
  const entry = metrics.mart_entry_level[0];

  return (
    <>
      <div className="max-w-3xl">
        <p className="text-sm font-medium text-accent">Bay Area · SEC Form D × DOL LCA data</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">{QUESTION}</h1>
        <p className="mt-4 text-lg text-zinc-700 dark:text-zinc-300">
          {pct(headline.sponsor_rate)} of raises are. The share moves a lot with how much the
          startup raised and with whether it has filed for H-1B workers before.
        </p>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          value={pct(headline.sponsor_rate)}
          label="of raises are followed by an H-1B filing within a year"
          note={`n = ${count(headline.n)} raises`}
        />
        <Stat
          value={pct(topRound.sponsor_rate)}
          label={`for raises of ${topRound.round_bin}`}
          note={`n = ${count(topRound.n)} raises`}
        />
        <Stat
          value={pct(before.sponsor_rate)}
          label="for startups that had filed in the two years before"
          note={`n = ${count(before.n)} raises`}
        />
        <Stat
          value={pct(entry.entry_level_share)}
          label="of filing startups file for an early-career tech role"
          note={`n = ${count(entry.n)} startups`}
        />
      </div>

      <Section title="Bigger raises file far more often">
        <p className="mb-4 max-w-3xl text-sm text-zinc-700 dark:text-zinc-300">
          Share of raises followed by at least one certified H-1B LCA from the same company within
          12 months, by amount sold.
        </p>
        <RateBars
          caption="Share of raises followed by an H-1B filing within 12 months, by size of raise"
          rows={rounds.map((r) => ({
            label: r.round_bin === "unknown" ? "Not reported" : r.round_bin,
            rate: r.sponsor_rate,
            n: r.n,
            highlight: r.round_bin === topRound.round_bin,
          }))}
        />
      </Section>

      <Section title="Past filing is the strongest signal">
        <p className="mb-4 max-w-3xl text-sm text-zinc-700 dark:text-zinc-300">
          The same share, split by whether the company filed for H-1B workers in the 24 months
          before the raise.
        </p>
        <RateBars
          caption="Share of raises followed by an H-1B filing, by earlier filing history"
          rows={[
            { label: "Filed before", rate: before.sponsor_rate, n: before.n, highlight: true },
            { label: "No earlier filing", rate: never.sponsor_rate, n: never.n },
          ]}
        />
      </Section>

      <Section title="All findings">
        <ol className="max-w-3xl list-decimal space-y-3 pl-5">
          {findings.map((finding) => (
            <li key={finding.id}>
              {finding.text}
              {finding.small_sample ? " (small sample)" : ""}
            </li>
          ))}
        </ol>
        <p className="mt-4 max-w-3xl text-sm text-zinc-600 dark:text-zinc-400">
          {quality.text} Based on {count(coverage.raises)} raises by {count(coverage.companies)}{" "}
          startups filed from {day(coverage.first_raise)} to {day(coverage.last_raise)}. Rates use
          raises up to {day(coverage.last_raise_with_full_followup)}, the last with a full year of
          LCA data after them.
        </p>
      </Section>

      <Section title="Who raised recently and has sponsored before?">
        <p className="max-w-3xl">
          The{" "}
          <Link href="/radar" className="font-medium underline">
            radar
          </Link>{" "}
          ranks startups that filed a Form D in the last few weeks by their H-1B filing history
          {radar.rows.length ? ` (${radar.rows.length} this week)` : ""}. Or{" "}
          <Link href="/explore" className="font-medium underline">
            explore all {count(coverage.companies)} startups
          </Link>
          .
        </p>
      </Section>
    </>
  );
}
