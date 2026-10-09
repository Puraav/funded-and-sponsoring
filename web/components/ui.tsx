import type { ReactNode } from "react";

export function PageTitle({ title, lead }: { title: string; lead?: ReactNode }) {
  return (
    <div className="mb-8 max-w-3xl">
      <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{title}</h1>
      {lead ? <p className="mt-3 text-zinc-700 dark:text-zinc-300">{lead}</p> : null}
    </div>
  );
}

export function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="mt-10">
      <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
      <div className="mt-3">{children}</div>
    </section>
  );
}

export function Stat({ value, label, note }: { value: string; label: string; note: string }) {
  return (
    <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
      <div className="text-3xl font-semibold tracking-tight tabular-nums">{value}</div>
      <div className="mt-1 text-sm">{label}</div>
      <div className="mt-1 text-xs text-zinc-600 dark:text-zinc-400">{note}</div>
    </div>
  );
}

export const tableClass = "w-full min-w-[32rem] text-left text-sm";
export const thClass =
  "border-b border-zinc-200 py-2 pr-4 font-medium text-zinc-600 dark:border-zinc-800 dark:text-zinc-400";
export const tdClass = "border-b border-zinc-100 py-2 pr-4 align-top dark:border-zinc-900";
