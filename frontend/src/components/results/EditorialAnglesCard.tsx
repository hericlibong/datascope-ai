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
    <Card className="rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm">
      <CardContent className="p-6 space-y-4">
        <h2 className="text-xl font-semibold text-white">{title}</h2>

        {angles.length === 0 ? (
          <p className="text-sm text-slate-400">{emptyText}</p>
        ) : (
          <ul className="space-y-3">
            {angles.map((angle, i) => (
              <li key={i} className="border border-white/10 p-4 rounded-lg bg-white/5">
                <p className="font-semibold text-white">{angle.title}</p>
                <p className="text-sm text-slate-300 mt-1">{angle.description}</p>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
