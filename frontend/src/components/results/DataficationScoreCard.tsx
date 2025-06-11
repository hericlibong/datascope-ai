// frontend/src/components/results/DataficationScoreCard.tsx



import { Badge } from "@/components/ui/badge"

type Props = {
  score: number
  profileLabel: string
  language: "en" | "fr"
}

// Traduction + couleur en fonction du score
function getTranslatedLabel(score: number, language: "en" | "fr"): string {
  if (score < 4)
    return language === "fr" ? "Potentiel faible" : "Low potential"
  if (score < 6)
    return language === "fr" ? "Potentiel modéré" : "Moderate potential"
  if (score < 8)
    return language === "fr" ? "Potentiel élevé" : "High potential"
  return language === "fr" ? "Potentiel très élevé" : "Very high potential"
}

function getBadgeColor(score: number): string {
  if (score < 4) return "bg-red-500"
  if (score < 6) return "bg-yellow-500"
  if (score < 8) return "bg-green-500"
  return "bg-emerald-600"
}

function getEditorialComment(score: number, language: "en" | "fr"): string {
  if (language === "fr") {
    if (score < 4) return "📉 Peu de données exploitables – article peu structuré"
    if (score < 6) return "📘 Contenu partiellement structuré – potentiel à explorer"
    if (score < 8) return "📊 Données bien structurées – bon candidat pour l’analyse"
    return "🔍 Article riche en données – excellent pour l’investigation"
  } else {
    if (score < 4) return "📉 Few usable data points – poorly structured"
    if (score < 6) return "📘 Some structure detected – might be explored"
    if (score < 8) return "📊 Well-structured data – good candidate for analysis"
    return "🔍 Rich, structured article – great for investigative work"
  }
}

export function DataficationScoreCard({ score, language }: Props) {
    if (score === undefined || score === null) return null
  const translatedLabel = getTranslatedLabel(score, language)
  const badgeColor = getBadgeColor(score)
  const comment = getEditorialComment(score, language)

  return (
    <div className="rounded-lg border p-4 shadow-md bg-white space-y-2">
      <h2 className="text-md font-semibold mb-1">
        {language === "fr" ? "📈 Score de datafication" : "📈 Datafication Score"}
      </h2>

      <div className="flex items-center gap-3">
        <span className="text-2xl font-bold">{score.toFixed(1)} / 10</span>
        <Badge className={`${badgeColor} text-white text-sm`}>
          {translatedLabel}
        </Badge>
      </div>

      <div className="text-sm text-muted-foreground">
        {comment}
      </div>
    </div>
  )
}
