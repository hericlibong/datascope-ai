import type { ReactNode } from "react";

export default function KpiStat({
  label, value, hint, accent = "indigo",
}: {
  label: string; value: ReactNode; hint?: string;
  accent?: "indigo" | "emerald" | "amber" | "pink" | "sky";
}) {
  const border =
    accent === "emerald" ? "border-l-emerald-400"
  : accent === "amber"   ? "border-l-amber-400"
  : accent === "pink"    ? "border-l-pink-400"
  : accent === "sky"     ? "border-l-sky-400"
  :                        "border-l-indigo-400";

  return (
    <div className={`rounded-2xl border border-white/15 bg-white/[0.07] p-5 backdrop-blur-sm ${border} border-l-4`}>
      <div className="text-[11px] uppercase tracking-widest text-white/60">{label}</div>
      <div className="mt-1 text-3xl font-extrabold leading-tight">{value}</div>
      {hint ? <div className="mt-1 text-xs text-white/60">{hint}</div> : null}
    </div>
  );
}
