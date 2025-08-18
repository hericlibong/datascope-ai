interface ResultGaugeProps {
  score: number; // entre 0 et 100
}

export default function ResultGauge({ score }: ResultGaugeProps) {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;

  return (
    <svg width="140" height="140" className="transform -rotate-90">
      <circle
        cx="70"
        cy="70"
        r={radius}
        stroke="gray"
        strokeWidth="10"
        fill="none"
        className="opacity-30"
      />
      <circle
        cx="70"
        cy="70"
        r={radius}
        stroke="url(#grad)"
        strokeWidth="10"
        fill="none"
        strokeDasharray={circumference}
        strokeDashoffset={circumference - progress}
        strokeLinecap="round"
      />
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6366F1" />
          <stop offset="100%" stopColor="#EC4899" />
        </linearGradient>
      </defs>
      <text
        x="70"
        y="70"
        textAnchor="middle"
        dominantBaseline="central"
        className="fill-white text-xl font-bold rotate-90"
      >
        {score}%
      </text>
    </svg>
  );
}
