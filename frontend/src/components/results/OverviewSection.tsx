import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { FileDown, RefreshCw } from "lucide-react";

interface OverviewSectionProps {
  score?: number;
  language: "en" | "fr";
  source?: string;
  dateAnalyzed?: string;
  isLoading?: boolean;
}

export function OverviewSection({ 
  score, 
  language, 
  source, 
  dateAnalyzed, 
  isLoading = false 
}: OverviewSectionProps) {
  const t = (en: string, fr: string) => language === "fr" ? fr : en;

  if (isLoading) {
    return (
      <section id="overview" className="mb-12">
        <Card className="rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm">
          <CardContent className="p-8">
            <div className="flex items-start justify-between mb-6">
              <div className="space-y-2">
                <Skeleton className="h-3 w-32" />
                <Skeleton className="h-8 w-64" />
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-3 w-32" />
              </div>
              <div className="flex gap-2">
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-24" />
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <Skeleton className="h-6 w-48" />
                <div className="flex items-center gap-4">
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-6 w-32" />
                </div>
                <Skeleton className="h-2 w-full" />
              </div>
              <div className="space-y-4">
                <Skeleton className="h-6 w-32" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-5/6" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    );
  }

  const getScoreLabel = (score: number) => {
    if (score < 4) return t("Low potential", "Potentiel faible");
    if (score < 6) return t("Moderate potential", "Potentiel modéré");
    if (score < 8) return t("High potential", "Potentiel élevé");
    return t("Very high potential", "Potentiel très élevé");
  };

  const getScoreColor = (score: number) => {
    if (score < 4) return "bg-red-500";
    if (score < 6) return "bg-yellow-500";
    if (score < 8) return "bg-green-500";
    return "bg-emerald-600";
  };

  const getKeyTakeaways = () => {
    if (!score) return [];
    
    if (language === "fr") {
      if (score >= 8) {
        return [
          "🔍 Article riche en données structurées",
          "📊 Excellent potentiel pour l'investigation",
          "⚡ Prêt pour l'analyse avancée"
        ];
      } else if (score >= 6) {
        return [
          "📊 Données bien structurées détectées",
          "🎯 Bon candidat pour l'analyse",
          "🔧 Quelques optimisations possibles"
        ];
      } else if (score >= 4) {
        return [
          "📘 Structure partielle détectée",
          "🔍 Potentiel à explorer",
          "⚙️ Analyse nécessitant des ajustements"
        ];
      } else {
        return [
          "📉 Peu de données exploitables",
          "🔧 Article peu structuré",
          "💡 Recommandations d'amélioration disponibles"
        ];
      }
    } else {
      if (score >= 8) {
        return [
          "🔍 Rich, structured data detected",
          "📊 Excellent potential for investigation",
          "⚡ Ready for advanced analysis"
        ];
      } else if (score >= 6) {
        return [
          "📊 Well-structured data found",
          "🎯 Good candidate for analysis",
          "🔧 Some optimizations possible"
        ];
      } else if (score >= 4) {
        return [
          "📘 Partial structure detected",
          "🔍 Potential to explore",
          "⚙️ Analysis requiring adjustments"
        ];
      } else {
        return [
          "📉 Few usable data points",
          "🔧 Poorly structured article",
          "💡 Improvement recommendations available"
        ];
      }
    }
  };

  return (
    <section id="overview" className="mb-12">
      <Card className="rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm">
        <CardContent className="p-8">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-400 mb-2">
                {t("ANALYSIS OVERVIEW", "VUE D'ENSEMBLE")}
              </p>
              <h1 className="text-2xl font-bold text-white mb-2">
                {t("Analysis Results", "Résultats d'analyse")}
              </h1>
              {source && (
                <p className="text-sm text-slate-300">
                  {t("Source", "Source")}: {source}
                </p>
              )}
              {dateAnalyzed && (
                <p className="text-xs text-slate-400">
                  {t("Analyzed on", "Analysé le")}: {dateAnalyzed}
                </p>
              )}
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm"
                className="border-white/20 bg-white/5 text-white hover:bg-white/10"
              >
                <FileDown className="w-4 h-4 mr-2" />
                {t("Export", "Exporter")}
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className="border-white/20 bg-white/5 text-white hover:bg-white/10"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                {t("Re-analyze", "Re-analyser")}
              </Button>
            </div>
          </div>

          {/* Score and Key Takeaways */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* Datafication Score */}
            {typeof score === "number" && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">
                  {t("Datafication Score", "Score de datafication")}
                </h3>
                <div className="flex items-center gap-4">
                  <div className="text-3xl font-bold text-white">
                    {score.toFixed(1)}/10
                  </div>
                  <Badge className={`${getScoreColor(score)} text-white`}>
                    {getScoreLabel(score)}
                  </Badge>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getScoreColor(score)}`}
                    style={{ width: `${(score / 10) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Key Takeaways */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">
                {t("Key Insights", "Points clés")}
              </h3>
              <ul className="space-y-2">
                {getKeyTakeaways().map((takeaway, index) => (
                  <li key={index} className="text-sm text-slate-300 flex items-start gap-2">
                    <span className="opacity-60">•</span>
                    <span>{takeaway}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}