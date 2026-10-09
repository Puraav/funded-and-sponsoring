"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Company } from "@/lib/data";
import { city, day, money, usd } from "@/lib/format";

type SortKey = "name" | "latest_raise" | "total_sold" | "prior_24m" | "lcas_total" | "median_wage";

const COLUMNS: { key: SortKey; label: string; numeric?: boolean }[] = [
  { key: "name", label: "Startup" },
  { key: "latest_raise", label: "Latest raise" },
  { key: "total_sold", label: "Raised", numeric: true },
  { key: "prior_24m", label: "H-1B filings, 24 mo before", numeric: true },
  { key: "lcas_total", label: "H-1B filings, all", numeric: true },
  { key: "median_wage", label: "Median wage", numeric: true },
];
const ROUNDS = ["<$2M", "$2–10M", "$10–50M", "$50M+", "unknown"];
const PAGE = 100;
const fieldClass =
  "mt-1 block w-full rounded-md border border-zinc-300 bg-transparent px-2 py-1.5 text-sm dark:border-zinc-700";

function csvCell(value: unknown): string {
  const text = value == null ? "" : String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

export function Explorer({ companies }: { companies: Company[] }) {
  const [query, setQuery] = useState("");
  const [round, setRound] = useState("");
  const [industry, setIndustry] = useState("");
  const [county, setCounty] = useState("");
  const [sponsored, setSponsored] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [sort, setSort] = useState<{ key: SortKey; desc: boolean }>({
    key: "latest_raise",
    desc: true,
  });
  const [shown, setShown] = useState(PAGE);

  const industries = useMemo(
    () => [...new Set(companies.map((c) => c.industry ?? "Not given"))].sort(),
    [companies],
  );
  const counties = useMemo(() => [...new Set(companies.map((c) => c.county))].sort(), [companies]);

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const filtered = companies.filter(
      (c) =>
        (!needle || c.name.toLowerCase().includes(needle)) &&
        (!round || c.round_bin === round) &&
        (!industry || (c.industry ?? "Not given") === industry) &&
        (!county || c.county === county) &&
        (!sponsored || c.sponsored_before === (sponsored === "yes")) &&
        (!from || c.latest_raise >= from) &&
        (!to || c.latest_raise <= to),
    );
    const direction = sort.desc ? -1 : 1;
    return filtered.sort((a, b) => {
      const x = a[sort.key];
      const y = b[sort.key];
      if (x == null) return 1;
      if (y == null) return -1;
      return (x < y ? -1 : x > y ? 1 : 0) * direction;
    });
  }, [companies, query, round, industry, county, sponsored, from, to, sort]);

  function download() {
    const keys: (keyof Company)[] = [
      "name", "city", "county", "industry", "latest_raise", "raises", "total_sold", "round_bin",
      "prior_24m", "after_12m", "lcas_total", "median_wage", "role_groups",
    ]; // prettier-ignore
    const lines = [keys.join(","), ...rows.map((r) => keys.map((k) => csvCell(r[k])).join(","))];
    const url = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "funded-and-sponsoring.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  const change = (set: (value: string) => void) => (event: { target: { value: string } }) => {
    set(event.target.value);
    setShown(PAGE);
  };

  return (
    <div>
      <form
        className="grid grid-cols-2 gap-3 sm:grid-cols-4"
        onSubmit={(event) => event.preventDefault()}
      >
        <label className="col-span-2 text-sm">
          Startup name
          <input
            type="search"
            value={query}
            onChange={change(setQuery)}
            placeholder="Search"
            className={fieldClass}
          />
        </label>
        <label className="text-sm">
          Size of latest raise
          <select value={round} onChange={change(setRound)} className={fieldClass}>
            <option value="">Any</option>
            {ROUNDS.map((r) => (
              <option key={r} value={r}>
                {r === "unknown" ? "Not reported" : r}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Filed for H-1B before
          <select value={sponsored} onChange={change(setSponsored)} className={fieldClass}>
            <option value="">Any</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        </label>
        <label className="text-sm">
          Industry
          <select value={industry} onChange={change(setIndustry)} className={fieldClass}>
            <option value="">Any</option>
            {industries.map((i) => (
              <option key={i}>{i}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          County
          <select value={county} onChange={change(setCounty)} className={fieldClass}>
            <option value="">Any</option>
            {counties.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Raised from
          <input type="date" value={from} onChange={change(setFrom)} className={fieldClass} />
        </label>
        <label className="text-sm">
          Raised to
          <input type="date" value={to} onChange={change(setTo)} className={fieldClass} />
        </label>
      </form>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <p className="mr-auto text-sm" aria-live="polite" data-testid="result-count">
          {rows.length.toLocaleString()} of {companies.length.toLocaleString()} startups
        </p>
        <button
          type="button"
          onClick={download}
          className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm font-medium hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
        >
          Download CSV
        </button>
      </div>

      <div className="mt-3 overflow-x-auto">
        <table className="w-full min-w-[46rem] text-left text-sm">
          <thead>
            <tr>
              {COLUMNS.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  aria-sort={
                    sort.key !== column.key ? "none" : sort.desc ? "descending" : "ascending"
                  }
                  className={`border-b border-zinc-200 py-2 pr-4 font-medium dark:border-zinc-800 ${column.numeric ? "text-right" : ""}`}
                >
                  <button
                    type="button"
                    className="hover:underline"
                    onClick={() =>
                      setSort((s) => ({
                        key: column.key,
                        desc: s.key === column.key ? !s.desc : column.key !== "name",
                      }))
                    }
                  >
                    {column.label}
                    {sort.key === column.key ? (sort.desc ? " ↓" : " ↑") : ""}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, shown).map((c) => (
              <tr key={c.slug} className="border-b border-zinc-100 dark:border-zinc-900">
                <td className="py-2 pr-4">
                  {c.has_page ? (
                    <Link href={`/company/${c.slug}`} className="font-medium underline">
                      {c.name}
                    </Link>
                  ) : (
                    c.name
                  )}
                  <div className="text-xs text-zinc-600 dark:text-zinc-400">
                    {city(c.city)} · {c.industry ?? "Industry not given"}
                  </div>
                </td>
                <td className="py-2 pr-4 whitespace-nowrap">{day(c.latest_raise)}</td>
                <td className="py-2 pr-4 text-right tabular-nums">{money(c.total_sold)}</td>
                <td className="py-2 pr-4 text-right tabular-nums">{c.prior_24m}</td>
                <td className="py-2 pr-4 text-right tabular-nums">{c.lcas_total}</td>
                <td className="py-2 pr-4 text-right tabular-nums">{usd(c.median_wage)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length === 0 ? <p className="mt-4 text-sm">No startups match these filters.</p> : null}
      {rows.length > shown ? (
        <button
          type="button"
          onClick={() => setShown((n) => n + PAGE)}
          className="mt-4 rounded-md border border-zinc-300 px-3 py-1.5 text-sm font-medium hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
        >
          Show {Math.min(PAGE, rows.length - shown)} more
        </button>
      ) : null}
    </div>
  );
}
