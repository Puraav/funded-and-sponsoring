"use client";

import { usePlot } from "./usePlot";

type Month = { month: string; lcas: number; new_hire_lcas: number };

const ACCENT = "#2f7fdc";

/** H-1B filings per month for one company, with a line at each raise. */
export function MonthlyBars({ months, raises }: { months: Month[]; raises: string[] }) {
  const height = 260;
  const ref = usePlot(
    (Plot, width) => {
      const data = months.map((m) => ({ ...m, date: new Date(`${m.month}T00:00:00Z`) }));
      const marks = raises.map((r) => ({ date: new Date(`${r}T00:00:00Z`) }));
      return Plot.plot({
        width,
        height,
        marginLeft: 36,
        marginTop: 24,
        style: { background: "transparent", fontSize: "12px" },
        x: { type: "utc", label: null },
        y: { label: "H-1B filings", grid: true, tickFormat: "d", ticks: 5 },
        marks: [
          Plot.rectY(data, {
            x: "date",
            y: "lcas",
            interval: "month",
            fill: ACCENT,
            inset: 1,
            title: (m: (typeof data)[number]) =>
              `${m.month.slice(0, 7)}: ${m.lcas} filings (${m.new_hire_lcas} for new hires)`,
            tip: true,
          }),
          Plot.ruleX(marks, { x: "date", stroke: "currentColor", strokeDasharray: "3,3" }),
          Plot.text(marks, {
            x: "date",
            frameAnchor: "top",
            dy: -14,
            text: () => "raise",
            fontSize: 11,
          }),
          Plot.ruleY([0]),
        ],
      });
    },
    [months, raises],
  );

  return (
    <div
      ref={ref}
      style={{ minHeight: height }}
      role="img"
      aria-label="H-1B filings per month, with a dashed line at each raise"
    />
  );
}
