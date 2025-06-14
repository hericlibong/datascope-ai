import { useState, useId } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { DataficationScoreCard } from "@/components/results/DataficationScoreCard";
import { EntitiesSummaryCard } from "@/components/results/EntitiesSummaryCard";
import { EditorialAnglesCard } from "@/components/results/EditorialAnglesCard";
import { DatasetSuggestionsCard } from "@/components/results/DatasetSuggestionsCard";

// Base URL configurable via .env (VITE_API_URL) avec fallback localhost
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function AnalyzePage() {
  /* ---------------------- état formulaire ---------------------- */
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<"en" | "fr">("en");

  /* ------------------- état interface & résultat --------------- */
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const langSwitchId = useId();

  /* ---------------------- gestion soumission ------------------- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    setResult(null);

    if (!text && !file) {
      setLoading(false);
      setErrorMessage(
        language === "fr"
          ? "Veuillez entrer un texte ou charger un fichier."
          : "Please enter text or upload a file."
      );
      return;
    }

    const formData = new FormData();
    formData.append("language", language);
    if (text) formData.append("text", text);
    if (file) formData.append("file", file);

    try {
      /* ------------------ 1/ création de l'analyse ------------------ */
      const token = localStorage.getItem("access_token");
      const createRes = await fetch(`${API_URL}/api/analysis/`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!createRes.ok) {
        const detail = await createRes.json().catch(() => ({}));
        setErrorMessage(detail?.error ?? `API error (${createRes.status})`);
        return;
      }

      const { analysis_id } = await createRes.json();

      /* ---------------- 2/ récupération du résultat complet --------- */
      const resultRes = await fetch(`${API_URL}/api/analysis/${analysis_id}/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!resultRes.ok) {
        setErrorMessage(
          language === "fr"
            ? "Impossible de récupérer les résultats de l’analyse."
            : "Unable to retrieve analysis results."
        );
        return;
      }

      const fullResult = await resultRes.json();
      setResult(fullResult);
    } catch (err) {
      /* Erreur réseau réelle (CORS, offline, etc.) */
      console.error(err);
      setErrorMessage(
        language === "fr"
          ? "Erreur réseau : impossible de contacter l’API."
          : "Network error: could not reach the API."
      );
    } finally {
      setLoading(false);
    }
  };

  /* ----------------------------- rendu ----------------------------- */
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
          <span role="img" aria-label="anglais">
            🇬🇧
          </span>
          <Switch
            id={langSwitchId}
            checked={language === "fr"}
            onCheckedChange={(v) => setLanguage(v ? "fr" : "en")}
          />
          <span role="img" aria-label="français">
            🇫🇷
          </span>
          <span className="text-xs text-gray-500 ml-2">
            {language === "fr" ? "Français" : "English"}
          </span>
        </div>

        {/* Champ texte */}
        <div>
          <Label htmlFor="text">
            {language === "fr" ? "Texte" : "Text"}
          </Label>
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
              if (e.target.files) setFile(e.target.files[0]);
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

      {/* === Résultats === */}
      {result?.score !== undefined && (
        <div className="mt-8 space-y-6">
          <h2 className="text-xl font-semibold">
            {language === "fr" ? "Résultats" : "Results"}
          </h2>

          {/* Score de datafication */}
          <DataficationScoreCard
            score={result.score}
            profileLabel={result.profile_label}
            language={language}
          />

          {/* Entités */}
          {Array.isArray(result.entities) && result.entities.length > 0 && (
            <EntitiesSummaryCard entities={result.entities} language={language} />
          )}

          {/* Angles éditoriaux */}
          {Array.isArray(result.angles) && result.angles.length > 0 && (
            <EditorialAnglesCard angles={result.angles} language={language} />
          )}

          {/* Datasets */}
        { /* Array.isArray(result.datasets) && result.datasets.length > 0 && ( 
            <DatasetSuggestionsCard datasets={result.datasets} language={language} />
          )*/}

          {result?.datasets && result.datasets.length > 0 && (
            <DatasetSuggestionsCard datasets={result.datasets} language={language} />
          )}


          {/* Debug brut */}
          <div className="mt-8 bg-gray-100 border border-gray-300 p-4 rounded text-sm text-gray-700">
            <h3 className="text-md font-semibold mb-2">
              {language === "fr" ? "Résultat complet brut (debug)" : "Raw Result (debug)"}
            </h3>
            <pre className="whitespace-pre-wrap overflow-x-auto text-xs">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
