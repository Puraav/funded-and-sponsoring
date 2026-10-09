"use client";

import { pct } from "@/lib/format";
import { usePlot } from "./usePlot";

export type RateBar = { label: string; rate: number; n: number; highlight?: boolean };

const ACCENT = "#2f7fdc";

/** Horizontal bars of a rate per group, one group in the accent colour, with a table view. */
export function RateBars({ rows, caption }: { rows: RateBar[]; caption: string }) {
  const height = rows.length * 46 + 40;
  const ref = usePlot(
    (Plot, width) =>
      Plot.plot({
        width,
        height,
        marginLeft: Math.min(170, Math.max(...rows.map((r) => r.label.length)) * 7 + 16),
        marginRight: 96,
        style: { background: "transparent", fontSize: "13px", overflow: "visible" },
        x: { domain: [0, Math.max(...rows.map((r) => r.rate)) * 1.02], axis: null },
        y: { domain: rows.map((r) => r.label), label: null, tickSize: 0, padding: 0.3 },
        marks: [
          Plot.barX(rows, {
            x: "rate",
            y: "label",
            fill: (r: RateBar) => (r.highlight ? ACCENT : "currentColor"),
            fillOpacity: (r: RateBar) => (r.highlight ? 1 : 0.22),
            rx2: 3,
            title: (r: RateBar) => `${r.label}: ${pct(r.rate)} of ${r.n.toLocaleString()} raises`,
            tip: true,
          }),
          Plot.text(rows, {
            x: "rate",
            y: "label",
            text: (r: RateBar) => `${pct(r.rate)}  n = ${r.n.toLocaleString()}`,
            textAnchor: "start",
            dx: 8,
          }),
        ],
      }),
    [rows],
  );

  return (
    <figure>
      <div ref={ref} style={{ minHeight: height }} role="img" aria-label={caption} />
      <details className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        <summary className="cursor-pointer select-none">View as table</summary>
        <table className="mt-2 w-full max-w-md text-left">
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr className="border-b border-zinc-200 dark:border-zinc-800">
              <th className="py-1 font-medium">Group</th>
              <th className="py-1 text-right font-medium">Share</th>
              <th className="py-1 text-right font-medium">Raises (n)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label}>
                <td className="py-1">{row.label}</td>
                <td className="py-1 text-right tabular-nums">{pct(row.rate)}</td>
                <td className="py-1 text-right tabular-nums">{row.n.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}
