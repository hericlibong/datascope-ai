// frontend/src/components/results/EntitiesSummaryCard.tsx
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

type Entity = {
  id: number
  type: "PER" | "ORG" | "LOC" | "DATE" | "NUM" | "MISC"
  value: string
  context?: string | null
}

type Props = {
  entities: Entity[]
  language: "en" | "fr"
}

export function EntitiesSummaryCard({ entities, language }: Props) {
  const countByType: Record<Entity["type"], number> = {
    PER: 0,
    ORG: 0,
    LOC: 0,
    DATE: 0,
    NUM: 0,
    MISC: 0,
  }

  entities.forEach((ent) => {
    countByType[ent.type]++
  })

  

  const rows = [
  
    { label:language == "fr" ? "Personnes" : "Persons", value: countByType.PER },
    { label:language == "fr" ? "Organisations" : "Organisms", value: countByType.ORG},
    { label:language == "fr" ? "Location" : "Location", value: countByType.LOC },
    { label: language === "fr" ? "Nombres + Unités" : "Numbers + Units", value: countByType.NUM },
    { label: language === "fr" ? "Dates" : "Dates", value: countByType.DATE },
    { label: language === "fr" ? "Autres" : "Misc", value: countByType.MISC }
  ]

  return (
    <Card className="rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm">
      <CardContent className="p-6 space-y-4">
      <h2 className="text-xl font-semibold flex items-center justify-between text-white">
        {language === "fr" ? "Résumé des entités détectées" : "Summary of Detected Entities"}
        <Badge variant="outline" className="ml-2 text-xs border-white/20 bg-white/10 text-slate-300">
            {entities.length} {language === "fr" ? "au total" : "total"}
        </Badge>
        </h2>
        <table className="w-full text-sm border-separate border-spacing-y-1">
          <thead>
            <tr className="text-left">
              <th className="p-2 text-slate-300">{language === "fr" ? "Type d'entité" : "Entity Type"}</th>
              <th className="p-2 text-slate-300">{language === "fr" ? "Nombre" : "Count"}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className="bg-white/5 rounded">
                <td className="p-2 text-slate-200">{row.label}</td>
                <td className="p-2">
                  <Badge
                    variant="secondary"
                    className={`rounded-full px-2 py-1 text-white ${row.value > 0 ? "bg-pink-500" : "bg-gray-600"}`}
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
