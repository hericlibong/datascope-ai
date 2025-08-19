// REPLACE the entire file `src/components/results/ResultGauge.tsx` with:

import { getScoreTheme } from "@/lib/scoreTheme";

export default function ResultGauge({ score }: { score: number }) {
  const s = Math.max(0, Math.min(100, Number.isFinite(score) ? score : 0));
  const r = 52, w = 10, c = 2 * Math.PI * r;
  const dash = (s / 100) * c;
  const theme = getScoreTheme(s);

  return (
    // ✅ plus d'anneau externe ni de ring-* : conteneur neutre
    <div className="flex flex-col items-center">
      <svg
        viewBox="0 0 140 140"
        width="180"
        height="180"
        aria-label={`Score ${s}%`}
        className="drop-shadow-[0_2px_10px_rgba(0,0,0,0.35)]"
      >
        <defs>
          <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            {/* stops couvrant une palette agréable */}
            <stop offset="0%"   stopColor="#22c55e" />  {/* emerald */}
            <stop offset="50%"  stopColor="#a78bfa" />  {/* violet */}
            <stop offset="100%" stopColor="#f59e0b" />  {/* amber */}
          </linearGradient>
        </defs>

        {/* piste (fond) plus fine et discrète */}
        <circle cx="70" cy="70" r={r} fill="none" stroke="#ffffff22" strokeWidth={w} />

        {/* arc de progression */}
        <circle
          cx="70"
          cy="70"
          r={r}
          fill="none"
          stroke="url(#scoreGrad)"
          strokeWidth={w}
          strokeDasharray={`${dash} ${c - dash}`}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
        />

        {/* valeur */}
        <text
          x="70"
          y="70"
          textAnchor="middle"
          dominantBaseline="central"
          className="fill-white text-3xl font-bold"
        >
          {s}%
        </text>
      </svg>

      <div className={`mt-2 text-xs ${theme.text}`}>Score de datafication</div>
    </div>
  );
}
