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
import { detectLang } from "@/utils/langDetect";

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
  
    let contentToAnalyze = text || "";
  
    if (file && !text) {
      try {
        contentToAnalyze = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (event) => resolve(event.target?.result as string);
          reader.onerror = (err) => reject(err);
          reader.readAsText(file);
        });
      } catch (err) {
        setErrorMessage(
          language === "fr"
            ? "Erreur de lecture du fichier. Veuillez réessayer."
            : "Error reading the file. Please try again."
        );
        setLoading(false);
        return;
      }
    }

    // Compte le nombre de mots du texte
    function countWords(str: string) {
      return (str.trim().split(/\s+/).filter(Boolean).length);
    }

    const wordCount = countWords(contentToAnalyze);

    if (wordCount < 220) {
      setErrorMessage(
        language === "fr"
          ? `Le texte est trop court (${wordCount} mots). Merci de fournir un texte d'au moins 220 mots.`
          : `Text is too short (${wordCount} words). Please provide at least 220 words.`
      );
      setLoading(false);
      return;
    }
  
    const detectedLang = detectLang(contentToAnalyze);
  
    // Gestion plus stricte et fiable des erreurs
    if (detectedLang !== language) {
      if (detectedLang === "latin") {
        setErrorMessage(
          language === "fr"
            ? "Le texte semble être du Lorem Ipsum (latin). Veuillez fournir un texte valide en français."
            : "The text appears to be Lorem Ipsum (Latin). Please provide a valid English text."
        );
      } else if (detectedLang === "other") {
        setErrorMessage(
          language === "fr"
            ? "Impossible de détecter clairement la langue du texte. Veuillez fournir un texte lisible en français."
            : "Unable to clearly detect the language. Please provide a readable English text."
        );
      } else {
        setErrorMessage(
          language === "fr"
            ? "Le texte n'est pas en français. Merci de saisir un texte en français."
            : "The text is not in English. Please enter a text in English."
        );
      }
      setLoading(false);
      return;
    }
  
    const formData = new FormData();
    formData.append("language", language);
    formData.append("text", contentToAnalyze);
  
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
        headers: { Authorization: `Bearer ${accessToken}` },
        body: formData,
      });
  
      if (!create.ok) {
        const detail = await create.json().catch(() => ({}));
        setErrorMessage(detail?.error ?? `API error (${create.status})`);
        setLoading(false);
        return;
      }
  
      const { analysis_id } = await create.json();
  
      const res = await fetch(`${API_URL}/api/analysis/${analysis_id}/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
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
