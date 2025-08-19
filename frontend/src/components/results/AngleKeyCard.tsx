// ADD new file: src/components/results/AngleKeyCard.tsx

export default function AngleKeyCard({
  index,
  title,
}: {
  index: number;
  title: string;
}) {
  return (
    <div
      className="
        group rounded-2xl border border-white/10 bg-white/6
        px-4 py-3 backdrop-blur-sm hover:border-white/20
        hover:bg-white/10 transition
        flex items-start gap-3
        shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]
      "
      role="listitem"
    >
      <div
        className="
          flex h-8 w-8 shrink-0 items-center justify-center
          rounded-xl bg-gradient-to-br from-indigo-500/40 to-fuchsia-500/40
          border border-white/10 text-white/90 text-sm font-bold
        "
      >
        {index}
      </div>
      <div className="flex-1">
        <div className="text-sm font-semibold text-white/95 leading-snug">
          {title}
        </div>
        <div className="mt-1 text-[11px] text-white/60">
          {/* Hint court : “angle prioritaire” */}
          Angle prioritaire
        </div>
      </div>
    </div>
  );
}
