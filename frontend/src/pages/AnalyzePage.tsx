import { useState, useId } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { DataficationScoreCard } from "@/components/results/DataficationScoreCard"
import { EntitiesSummaryCard } from "@/components/results/EntitiesSummaryCard"
import { EditorialAnglesCard } from "@/components/results/EditorialAnglesCard"
import { DatasetSuggestionsCard } from "@/components/results/DatasetSuggestionsCard"


export default function AnalyzePage() {
  // État des champs du formulaire
  const [text, setText] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [language, setLanguage] = useState<"en" | "fr">("en")

  // État de l’interface utilisateur
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const langSwitchId = useId()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setErrorMessage(null)
    setResult(null)
  
    if (!text && !file) {
      setLoading(false)
      setErrorMessage(
        language === "fr"
          ? "Veuillez entrer un texte ou charger un fichier."
          : "Please enter text or upload a file."
      )
      return
    }
  
    const formData = new FormData()
    formData.append("language", language)
    if (text) formData.append("text", text)
    if (file) formData.append("file", file)
  
    try {
      const token = localStorage.getItem("access_token")
  
      // 🔁 Étape 1 : on envoie le texte ou fichier
      const response = await fetch("http://localhost:8000/api/analysis/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token || ""}`,
        },
        body: formData,
      })
  
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}))
        setErrorMessage(detail?.error ?? `Erreur API : ${response.status}`)
        return
      }
  
      const data = await response.json() // { message, article_id, analysis_id }
  
      // 🔁 Étape 2 : on récupère les résultats complets de l’analyse
      const resultResponse = await fetch(`http://localhost:8000/api/analysis/${data.analysis_id}/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token || ""}`,
        },
      })
  
      if (!resultResponse.ok) {
        setErrorMessage(
          language === "fr"
            ? "Impossible de récupérer les résultats de l’analyse."
            : "Unable to retrieve analysis results."
        )
        return
      }
  
      const fullResult = await resultResponse.json()
      setResult(fullResult)
      console.log("Résultat complet :", fullResult)
    } catch (err) {
      setErrorMessage(
        language === "fr"
          ? "Erreur réseau : impossible de contacter l’API."
          : "Network error: could not reach the API."
      )
    } finally {
      setLoading(false)
    }
  }
  
  

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">
        {language === "fr" ? "Analyse d’un article" : "Article Analysis"}
      </h1>

      {/* === Formulaire d’analyse === */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Choix de langue */}
        <div className="flex items-center gap-4">
          <Label htmlFor={langSwitchId}>
            {language === "fr" ? "Langue" : "Language"}
          </Label>
          <span role="img" aria-label="anglais">🇬🇧</span>
          <Switch
            id={langSwitchId}
            checked={language === "fr"}
            onCheckedChange={(v) => setLanguage(v ? "fr" : "en")}
          />
          <span role="img" aria-label="français">🇫🇷</span>
          <span className="text-xs text-gray-500 ml-2">
            {language === "fr" ? "Français" : "English"}
          </span>
        </div>

        {/* Champ texte */}
        <div>
          <Label htmlFor="text">{language === "fr" ? "Texte" : "Text"}</Label>
          <Textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={
              language === "fr"
                ? "Collez ou saisissez votre texte ici..."
                : "Paste or type your text here..."
            }
            className="min-h-[120px]"
          />
        </div>

        {/* Champ fichier */}
        <div>
          <Label htmlFor="file">
            {language === "fr" ? "ou chargez un fichier" : "or upload a file"}
          </Label>
          <Input
            id="file"
            type="file"
            accept=".txt,.md"
            onChange={(e) => {
              if (e.target.files) setFile(e.target.files[0])
            }}
          />
        </div>

        {/* Message d’erreur */}
        {errorMessage && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded">
            {errorMessage}
          </div>
        )}

        {/* Bouton d’analyse */}
        <Button type="submit" disabled={loading}>
          {loading
            ? language === "fr"
              ? "Analyse en cours…"
              : "Analyzing…"
            : language === "fr"
              ? "Analyser"
              : "Analyze"}
        </Button>
      </form>

      {/* === Affichage des résultats === */}
      {result?.score !== undefined &&(
        <div className="mt-8 space-y-6">
          <h2 className="text-xl font-semibold">
            {language === "fr" ? "Résultats" : "Results"}
          </h2>

          {/* → Affiche le score de datafication */}
          <DataficationScoreCard
            score={result.score}
            profileLabel={result.profile_label}
            language={language}
          />

          {/* → Affiche les entités extraites */}
          {result?.entities && (
  <EntitiesSummaryCard
    entities={result.entities}
    language={language}
  />
    )}
  {/* → Affiche les angles éditoriaux */}
  {result?.angles && result.angles.length > 0 && (
  <EditorialAnglesCard angles={result.angles} language={language} />
 
  
  )}
 
 <DatasetSuggestionsCard datasets={result.connectors_results} language={result.language} />
 


  


          {/* Autres composants à venir ici */}
          {result?.entities && Array.isArray(result.entities) && result.entities.length > 0 && (
  <div className="mt-6">
    <h3 className="text-lg font-semibold mb-2">
      {language === "fr" ? "Entités extraites" : "Extracted Entities"}
    </h3>
    <div className="bg-gray-50 border p-4 rounded text-sm whitespace-pre-wrap">
      <pre>{JSON.stringify(result.entities, null, 2)}</pre>
    </div>
  </div>
  
)}
{/* Debug temporaire : affichage brut du résultat */}
{result && (
  <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded text-sm text-gray-700">
    <h3 className="text-md font-semibold mb-2">
      {language === "fr" ? "Résultat complet brut (debug)" : "Raw Result (debug)"}
    </h3>
    <pre className="whitespace-pre-wrap overflow-x-auto text-xs">
      {JSON.stringify(result, null, 2)}
    </pre>
  </div>
)}


        </div>
      )}
      
    </div>
  )
}


  
