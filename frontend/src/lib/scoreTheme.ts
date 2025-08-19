export function getScoreTheme(scoreRaw: number) {
  const s = Math.max(0, Math.min(100, Number.isFinite(scoreRaw) ? scoreRaw : 0));
  if (s >= 75)
    return {
      label: "Potentiel élevé",
      grad: "from-emerald-400 via-lime-300 to-emerald-500",
      ring: "ring-emerald-400/40",
      text: "text-emerald-300",
      chip: "bg-emerald-500/15 text-emerald-200 border-emerald-400/30",
    };
  if (s >= 40)
    return {
      label: "Potentiel moyen",
      grad: "from-indigo-400 via-violet-300 to-fuchsia-500",
      ring: "ring-violet-400/40",
      text: "text-violet-300",
      chip: "bg-violet-500/15 text-violet-200 border-violet-400/30",
    };
  return {
    label: "Potentiel faible",
    grad: "from-amber-400 via-orange-300 to-rose-500",
    ring: "ring-amber-400/40",
    text: "text-amber-300",
    chip: "bg-amber-500/15 text-amber-100 border-amber-400/30",
  };
}
