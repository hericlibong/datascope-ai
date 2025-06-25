/* ----------------------------------------------------------------------
 * pages/AnalyzePage.tsx
 * -------------------------------------------------------------------- */
import { useState, useId } from "react";

/* UI atoms ---------------------------------------------------------------- */
import { Textarea } from "@/components/ui/textarea";
import { Input }    from "@/components/ui/input";
import { Label }    from "@/components/ui/label";
import { Switch }   from "@/components/ui/switch";
import { Button }   from "@/components/ui/button";

/* Résultats ---------------------------------------------------------------- */
import { DataficationScoreCard } from "@/components/results/DataficationScoreCard";
import AngleCard                 from "@/components/results/AngleCard";

/* Types -------------------------------------------------------------------- */
import type { AngleResources }   from "@/types/analysis";

/* Base URL API (dotenv → VITE_API_URL) ------------------------------------ */
const API_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/* ======================================================================== */
export default function AnalyzePage() {
  /* -------- états du formulaire ---------------------------------------- */
  const [text,     setText]     = useState("");
  const [file,     setFile]     = useState<File | null>(null);
  const [language, setLanguage] = useState<"en" | "fr">("en");

  /* -------- états d’UI / résultat -------------------------------------- */
  const [loading, setLoading]          = useState(false);
  const [result,  setResult]           = useState<
    | { score: number; angle_resources: AngleResources[] }
    | null
  >(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const langSwitchId = useId();

  /* -------------------------------------------------------------------- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    setResult(null);

    /* validation rapide */
    if (!text && !file) {
      setLoading(false);
      setErrorMessage(
        language === "fr"
          ? "Veuillez entrer un texte ou charger un fichier."
          : "Please enter text or upload a file."
      );
      return;
    }

    const fd = new FormData();
    fd.append("language", language);
    if (text) fd.append("text", text);
    if (file) fd.append("file", file);

    try {
      /* ---------- 1/ création analyse ------------------------------ */
      const token = localStorage.getItem("access_token");
      const headers: HeadersInit =
        token != null ? { Authorization: `Bearer ${token}` } : {};

      const createRes = await fetch(`${API_URL}/api/analysis/`, {
        method: "POST",
        headers,           // peut être {}
        body: fd,
      });

      if (!createRes.ok) {
        const detail = await createRes.json().catch(() => ({}));
        setErrorMessage(detail?.error ?? `API error (${createRes.status})`);
        return;
      }
      const { analysis_id } = await createRes.json();

      /* ---------- 2/ résultat complet ----------------------------- */
      const res = await fetch(`${API_URL}/api/analysis/${analysis_id}/`, {
        headers,
      });

      if (!res.ok) {
        setErrorMessage(
          language === "fr"
            ? "Impossible de récupérer les résultats."
            : "Unable to retrieve analysis results."
        );
        return;
      }
      const full = await res.json();
      setResult(full);
    } catch (err: any) {
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

  /* ==================================================================== */
  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      {/* ------------------- Titre ------------------------------------- */}
      <h1 className="text-3xl font-bold">
        {language === "fr" ? "Analyse d’un article" : "Article Analysis"}
      </h1>

      {/* ------------------- Formulaire -------------------------------- */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* ---- langue ---- */}
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

        {/* ---- texte ---- */}
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
                ? "Collez ou saisissez votre texte ici…"
                : "Paste or type your text here…"
            }
            className="min-h-[120px]"
          />
        </div>

        {/* ---- fichier ---- */}
        <div>
          <Label htmlFor="file">
            {language === "fr" ? "ou chargez un fichier" : "or upload a file"}
          </Label>
          <Input
            id="file"
            type="file"
            accept=".txt,.md"
            onChange={(e) => e.target.files && setFile(e.target.files[0])}
          />
        </div>

        {/* ---- erreur ---- */}
        {errorMessage && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded">
            {errorMessage}
          </div>
        )}

        {/* ---- bouton ---- */}
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

      {/* ------------------- Résultats --------------------------------- */}
      {result && (
        <div className="space-y-6">
          {/* score global */}
          <DataficationScoreCard
            score={result.score}
            profileLabel=""
            language={language}
          />

          {/* une carte par angle */}
          {/* compatibilité : angles_resources (back) ou angle_resources (front) */}
        {(result.angle_resources ?? result.angle_resources)?.map(
          (angle: AngleResources) => (
            <AngleCard key={angle.index} angle={angle} language={language} />
        ))}

          {/* bloc debug optionnel */}
          <details className="bg-gray-100 border border-gray-300 p-4 rounded text-xs">
            <summary className="cursor-pointer font-medium">
              JSON / debug
            </summary>
            <pre className="whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
