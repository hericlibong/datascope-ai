import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { DataficationScoreCard } from "@/components/results/DataficationScoreCard";
import { EntitiesSummaryCard } from "@/components/results/EntitiesSummaryCard";
import AngleCard from "@/components/results/AngleCard";
import { FeedbackForm } from "@/components/results/FeedbackForm";
import type { AngleResources } from "@/types/analysis";
import { getAccessToken } from "@/api/auth";
import { useLanguage } from "@/contexts/LanguageContext";

const API_URL =
  import.meta.env.VITE_API_URL !== undefined
    ? String(import.meta.env.VITE_API_URL)
    : "http://localhost:8000";

export default function AnalyzePage() {
  const { language } = useLanguage();

  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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
      const accessToken = getAccessToken();
      if (!accessToken) {
        setErrorMessage(
          language === "fr"
            ? "Votre session a expiré, merci de vous reconnecter."
            : "Your session has expired, please log in again."
        );
        setLoading(false);
        return;
      }

      const create = await fetch(`${API_URL}/api/analysis/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        body: formData,
      });

      if (create.status === 401) {
        setErrorMessage(
          language === "fr"
            ? "Session expirée, veuillez vous reconnecter."
            : "Session expired, please log in again."
        );
        setLoading(false);
        return;
      }

      if (!create.ok) {
        const detail = await create.json().catch(() => ({}));
        setErrorMessage(detail?.error ?? `API error (${create.status})`);
        setLoading(false);
        return;
      }

      const { analysis_id } = await create.json();

      const res = await fetch(`${API_URL}/api/analysis/${analysis_id}/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (!res.ok) {
        setErrorMessage(
          language === "fr"
            ? "Impossible de récupérer les résultats."
            : "Unable to retrieve results."
        );
        setLoading(false);
        return;
      }

      const full = await res.json();
      setResult(full);
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err?.message ?? "Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      {/* *************** FORMULAIRE *************** */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* plus de switch local ici ! */}
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

      {result && (
        <div className="space-y-6">
          <DataficationScoreCard
            score={result.score}
            profileLabel={result.profile_label ?? ""}
            language={language}
          />
          <EntitiesSummaryCard
            entities={result.entities ?? []}
            language={language}
          />
          {(() => {
            const angles: AngleResources[] | undefined =
              result.angle_resources ?? result.angles_resources;
            return angles?.map((angle) => (
              <AngleCard key={angle.index} angle={angle} language={language} />
            ));
          })()}
          <FeedbackForm analysisId={result.id} language={language} />
        </div>
      )}
    </div>
  );
}
