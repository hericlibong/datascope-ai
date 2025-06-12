// frontend/src/components/results/EditorialAnglesCard.tsx
import { Card, CardContent } from "@/components/ui/card"

type Props = {
  angles: {
    title: string
    description: string
  }[]
  language: "en" | "fr"
}

export function EditorialAnglesCard({ angles, language }: Props) {
  const title = language === "fr" ? "Angles éditoriaux suggérés" : "Suggested Editorial Angles"
  const emptyText = language === "fr"
    ? "Aucun angle éditorial n’a été généré."
    : "No editorial angles were generated."

  return (
    <Card>
      <CardContent className="p-4 space-y-4">
        <h2 className="text-xl font-semibold">{title}</h2>

        {angles.length === 0 ? (
          <p className="text-sm text-muted-foreground">{emptyText}</p>
        ) : (
          <ul className="space-y-3">
            {angles.map((angle, i) => (
              <li key={i} className="border p-3 rounded shadow-sm bg-gray-50">
                <p className="font-semibold">{angle.title}</p>
                <p className="text-sm text-gray-600 mt-1">{angle.description}</p>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
