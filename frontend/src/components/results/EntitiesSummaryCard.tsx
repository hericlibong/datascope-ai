// frontend/src/components/results/EntitiesSummaryCard.tsx
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"


type Props = {
  extraction: {
    persons: string[]
    organizations: string[]
    locations: string[]
    dates: string[]
    numbers: { raw: string; value?: number; unit?: string }[]
  }
  strongVerbs?: string[]
  language: "en" | "fr"
}

export function EntitiesSummaryCard({ extraction, strongVerbs = [], language }: Props) {
  const totalNamed = extraction.persons.length + extraction.organizations.length + extraction.locations.length

  const rows = [
    { label: language === "fr" ? "Entités Nommées" : "Named Entities", value: totalNamed },
    { label: language === "fr" ? "Nombres + Unités" : "Numbers + Units", value: extraction.numbers.length },
    { label: language === "fr" ? "Dates" : "Dates", value: extraction.dates.length },
    { label: language === "fr" ? "Verbes forts" : "Strong Verbs", value: strongVerbs.length }
  ]

  const title = language === "fr" ? "Résumé des entités détectées" : "Summary of Detected Entities"
  const thType = language === "fr" ? "Type d'entité" : "Entity Type"
  const thCount = language === "fr" ? "Nombre" : "Count"

  return (
    <Card>
      <CardContent className="p-4 space-y-4">
        <h2 className="text-xl font-semibold">{title}</h2>
        <table className="w-full text-sm border-separate border-spacing-y-1">
          <thead>
            <tr className="text-left">
              <th className="p-2">{thType}</th>
              <th className="p-2">{thCount}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="bg-muted rounded">
                <td className="p-2">{row.label}</td>
                <td className="p-2">
                  <Badge
                    variant="secondary"
                    className={cn("rounded-full px-2 py-1 text-white", row.value > 0 ? "bg-pink-500" : "bg-gray-400")}
                  >
                    {row.value}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}
