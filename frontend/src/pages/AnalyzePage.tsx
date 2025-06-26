/* frontend/src/pages/AnalyzePage.tsx */
import { useState, useId } from "react";
import { Textarea }  from "@/components/ui/textarea";
import { Input }     from "@/components/ui/input";
import { Label }     from "@/components/ui/label";
import { Switch }    from "@/components/ui/switch";
import { Button }    from "@/components/ui/button";

import { DataficationScoreCard } from "@/components/results/DataficationScoreCard";
import AngleCard                 from "@/components/results/AngleCard";

import type { AngleResources }   from "@/types/analysis";

/* URL API (.env ➜ VITE_API_URL) */
const API_URL =
  import.meta.env.VITE_API_URL !== undefined
    ? String(import.meta.env.VITE_API_URL)
    : "http://localhost:8000";

export default function AnalyzePage() {
  /* ---------- état formulaire ---------- */
  const [text,     setText]     = useState("");
  const [file,     setFile]     = useState<File | null>(null);
  const [language, setLanguage] = useState<"en" | "fr">("en");

  /* ---------- état résultats ----------- */
  const [loading,      setLoading]      = useState(false);
  const [result,       setResult]       = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const langSwitchId = useId();

  /* ---------------- submit ------------- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    setResult(null);

    /* validation minime */
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
      /* 1. création de l’analyse */
      const token   = localStorage.getItem("access_token");
      const headers = token ? { Authorization: `Bearer ${token}` } : undefined;

      const create = await fetch(`${API_URL}/api/analysis/`, {
        method : "POST",
        headers,
        body   : formData,
      });

      if (!create.ok) {
        const detail = await create.json().catch(() => ({}));
        setErrorMessage(detail?.error ?? `API error (${create.status})`);
        return;
      }
      const { analysis_id } = await create.json();

      /* 2. récupération complète */
      const res = await fetch(`${API_URL}/api/analysis/${analysis_id}/`, {
        headers,
      });
      if (!res.ok) {
        setErrorMessage(
          language === "fr"
            ? "Impossible de récupérer les résultats."
            : "Unable to retrieve results."
        );
        return;
      }

      const full = await res.json();
      console.log("[DEBUG] payload reçu :", full);      // ← pour débogage
      setResult(full);
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err?.message ?? "Network error");
    } finally {
      setLoading(false);
    }
  };

  /* ---------------- rendu -------------- */
  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      {/* *************** FORMULAIRE *************** */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* langue */}
        <div className="flex items-center gap-4">
          <Label htmlFor={langSwitchId}>{language === "fr" ? "Langue" : "Language"}</Label>
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

        {/* texte */}
        <div>
          <Label htmlFor="text">{language === "fr" ? "Texte" : "Text"}</Label>
          <Textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={
              language === "fr"
                ? "Collez ou saisissez votre texte…"
                : "Paste or type your text…"
            }
            className="min-h-[120px]"
          />
        </div>

        {/* fichier */}
        <div>
          <Label htmlFor="file">
            {language === "fr" ? "ou chargez un fichier" : "or upload a file"}
          </Label>
          <Input
            id="file"
            type="file"
            accept=".txt,.md"
            onChange={(e) => {
              if (e.target.files?.[0]) setFile(e.target.files[0]);
            }}
          />
        </div>

        {/* erreur */}
        {errorMessage && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded">
            {errorMessage}
          </div>
        )}

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

      {/* *************** RÉSULTATS *************** */}
      {result && (
        <div className="space-y-6">
          {/* score global */}
          <DataficationScoreCard
            score={result.score}
            profileLabel={result.profile_label ?? ""}
            language={language}
          />

          {/* cartes angle */}
          {(() => {
            /* compatibilité double clé */
            const angles: AngleResources[] | undefined =
              result.angle_resources ?? result.angles_resources;

            console.log("[DEBUG] angle_resources =", angles); // ← doit afficher un tableau
            console.log("DEBUG angle_resources:", result.angle_resources);

            return angles?.map((angle) => (
              <AngleCard key={angle.index} angle={angle} language={language} />
            ));
          })()}
        </div>
      )}
    </div>
  );
}
