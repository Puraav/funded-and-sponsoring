// Display helpers. Numbers arrive ready-made from the data files; these only format them.

export function pct(value: number): string {
  const percent = value * 100;
  return percent >= 9.95 ? `${Math.round(percent)}%` : `${percent.toFixed(1)}%`;
}

export function usd(value: number | null | undefined): string {
  if (value == null) return "–";
  return `$${Math.round(value).toLocaleString("en-US")}`;
}

/** $1,250,000 → "$1.3M"; $18,600,000,000 → "$18.6B". */
export function money(value: number | null | undefined): string {
  if (value == null || value <= 0) return "–";
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(value >= 1e8 ? 0 : 1)}M`;
  if (value >= 1e3) return `$${Math.round(value / 1e3)}K`;
  return `$${Math.round(value)}`;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2025-03-25" → "25 Mar 2025" (no timezone surprises). */
export function day(iso: string | null | undefined): string {
  if (!iso) return "–";
  const [year, month, date] = iso.split("-").map(Number);
  return `${date} ${MONTHS[month - 1]} ${year}`;
}

/** "SAN MATEO" → "San Mateo". Form D cities come in mixed case. */
export function city(name: string | null | undefined): string {
  if (!name) return "–";
  return name.toLowerCase().replace(/(^|[\s-])\S/g, (letter) => letter.toUpperCase());
}

export function count(value: number): string {
  return value.toLocaleString("en-US");
}
