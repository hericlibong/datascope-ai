import ResultGauge from "./ResultGauge";
import { Button } from "@/components/ui/button";

interface ResultOverviewProps {
  title: string;
  score: number;
  summary: string[];
}

export default function ResultOverview({ title, score, summary }: ResultOverviewProps) {
  return (
    <section id="overview" className="space-y-6">
      <h2 className="text-2xl font-bold text-white">{title}</h2>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Résumé */}
        <div className="space-y-3">
          <h3 className="text-sm uppercase text-gray-400">Résumé</h3>
          <ul className="list-disc pl-5 text-gray-200 space-y-1">
            {summary.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ul>
        </div>

        {/* Score */}
        <div className="flex flex-col items-center justify-center">
          <ResultGauge score={score} />
          <Button className="mt-4">Exporter</Button>
        </div>
      </div>
    </section>
  );
}
