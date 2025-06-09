// frontend/src/pages/AnalyzePage.tsx

import { useState } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function AnalyzePage() {
  const [text, setText] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append("language", "en") // on pourra changer dynamiquement plus tard
      if (text) formData.append("text", text)
      if (file) formData.append("file", file)

      const token = localStorage.getItem("access_token") // ou autre méthode selon ton système d’authentification

      const response = await fetch("http://localhost:8000/api/analysis/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token || ""}`,
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Erreur API : ${response.status}`)
      }

      const data = await response.json()
      setResult(JSON.stringify(data, null, 2))
    } catch (err: any) {
      setError(err.message || "Erreur inconnue")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Analyse d’un article</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="text">Texte à analyser</Label>
          <Textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Copiez-collez ici votre texte..."
            className="min-h-[120px]"
          />
        </div>

        <div>
          <Label htmlFor="file">ou chargez un fichier</Label>
          <Input
            id="file"
            type="file"
            accept=".txt,.md"
            onChange={(e) => {
              if (e.target.files) {
                setFile(e.target.files[0])
              }
            }}
          />
        </div>

        <Button type="submit" disabled={loading}>
          {loading ? "Analyse en cours..." : "Analyser"}
        </Button>
      </form>

      {result && (
        <div className="mt-6 p-4 border rounded bg-green-50 text-sm whitespace-pre-wrap">
          <strong>Résultat :</strong>
          <pre>{result}</pre>
        </div>
      )}

      {error && (
        <div className="mt-6 p-4 border rounded bg-red-100 text-red-800 text-sm">
          Erreur : {error}
        </div>
      )}
    </div>
  )
}
