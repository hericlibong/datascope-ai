import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ChevronDown, ChevronRight } from "lucide-react"

type Dataset = {
  title: string
  description?: string
  source_name: string
  source_url: string
  formats: string[]
  organization?: string
  license?: string
  last_modified?: string
  richness: number
}

type Props = {
  datasets: Dataset[]
  language: "en" | "fr"
}

export function DatasetSuggestionsCard({ datasets, language }: Props) {
  const [open, setOpen] = useState(true)

  const toggleOpen = () => setOpen(!open)

  const label = language === "fr" ? "Suggestions de jeux de données" : "Suggested Datasets"
  const sourceLabel = language === "fr" ? "Source" : "Source"
  const formatLabel = language === "fr" ? "Formats" : "Formats"
  const richnessLabel = language === "fr" ? "Richesse" : "Richness"
  const linkLabel = language === "fr" ? "Voir" : "View"

  if (!datasets || datasets.length === 0) return null

  return (
    <Card>
      <CardContent className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <Button
            variant="ghost"
            className="text-xl font-semibold flex items-center px-0 hover:bg-transparent"
            onClick={toggleOpen}
        >
            {open ? <ChevronDown className="mr-2" /> : <ChevronRight className="mr-2" />}
            {label}
        </Button>
        </div>


        {open && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-separate border-spacing-y-1">
              <thead>
                <tr className="text-left">
                  <th className="p-2">{language === "fr" ? "Titre" : "Title"}</th>
                  <th className="p-2">{sourceLabel}</th>
                  <th className="p-2">{formatLabel}</th>
                  <th className="p-2">{richnessLabel}</th>
                  <th className="p-2">{language === "fr" ? "Lien" : "Link"}</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((ds, idx) => (
                  <tr key={idx} className="bg-muted rounded">
                    <td className="p-2">{ds.title}</td>
                    <td className="p-2">{ds.source_name}</td>
                    <td className="p-2">
                      {ds.formats.map((fmt, i) => (
                        <Badge key={i} variant="outline" className="mr-1 mb-1">
                          {fmt.toUpperCase()}
                        </Badge>
                      ))}
                    </td>
                    <td className="p-2">
                      <Badge variant="secondary" className="rounded-full px-2 py-1 bg-blue-600 text-white">
                        {ds.richness}/100
                      </Badge>
                    </td>
                    <td className="p-2">
                      <a
                        href={ds.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline"
                      >
                        {linkLabel}
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
