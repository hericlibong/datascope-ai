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

    function countWords(str: string) {
      return str.trim().split(/\s+/).filter(Boolean).length;
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

      if (create.status === 401) {
        setErrorMessage(
          language === "fr"
            ? "Votre session a expiré, merci de vous reconnecter."
            : "Your session has expired, please log in again."
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
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (res.status === 401) {
        setErrorMessage(
          language === "fr"
            ? "Votre session a expiré, merci de vous reconnecter."
            : "Your session has expired, please log in again."
        );
        setLoading(false);
        return;
      }

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
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto w-full max-w-4xl px-4 py-10 space-y-8">
        {/* EN-TÊTE */}
        <header>
          <div className="text-xs uppercase tracking-widest text-white/60">
            {language === "fr" ? "Analyse" : "Analysis"}
          </div>
          <h1 className="text-2xl font-semibold">
            {language === "fr" ? "Lancer une nouvelle analyse" : "Start a new analysis"}
          </h1>
          <p className="mt-2 text-sm text-white/80">
            {language === "fr"
              ? "Collez votre texte ou chargez un fichier. Résultats présentés dans une mise en page claire."
              : "Paste your text or upload a file. Results are presented in a clean layout."}
          </p>
        </header>

        {/* FORMULAIRE */}
        <form onSubmit={handleSubmit} className="space-y-5 w-full">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
            <div className="space-y-4">
              <div className="w-full">
                <Label htmlFor="text" className="flex items-center gap-2 font-medium mb-2">
                  <span>📝</span>
                  {language === "fr" ? "Texte à analyser" : "Text to analyze"}
                </Label>
                <Textarea
                  id="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={
                    language === "fr"
                      ? "Collez ou saisissez ici votre article ou texte à analyser…"
                      : "Paste or type here your article or text to analyze…"
                  }
                  className="w-full min-h-[160px] rounded-xl bg-white/5 text-white placeholder:text-white/40 border border-white/10 focus:ring-2 focus:ring-white/30 focus:border-white/20"
                />
              </div>

              <div>
                <Label htmlFor="file" className="font-medium">
                  {language === "fr" ? "Ou chargez un fichier" : "Or upload a file"}
                </Label>
                <Input
                  id="file"
                  type="file"
                  accept=".txt,.md"
                  onChange={(e) => {
                    if (e.target.files?.[0]) setFile(e.target.files[0]);
                  }}
                  className="mt-1 border-white/10 bg-white/5 text-white placeholder:text-white/40"
                />
              </div>

              {errorMessage && (
                <div className="rounded-xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                  <div>{errorMessage}</div>
                  {(errorMessage.includes("expiré") || errorMessage.includes("expired")) && (
                    <a
                      href="/login"
                      className="mt-2 inline-block rounded-lg bg-white/10 px-3 py-1 text-white underline-offset-2 hover:underline"
                    >
                      {language === "fr" ? "Se reconnecter" : "Sign in"}
                    </a>
                  )}
                </div>
              )}

              <div className="pt-2">
                <Button type="submit" disabled={loading}>
                  {loading
                    ? language === "fr"
                      ? "Analyse en cours…"
                      : "Analyzing…"
                    : language === "fr"
                    ? "Analyser"
                    : "Analyze"}
                </Button>
              </div>
            </div>
          </div>
        </form>

        {/* TEXTE ANALYSÉ (si présent) */}
        {result?.article?.content && (
          <section className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <span className="text-white/70">📝</span>
              {language === "fr" ? "Texte analysé" : "Analyzed text"}
            </h3>
            <div className="prose prose-invert max-w-none whitespace-pre-line text-white/90">
              {result.article.content}
            </div>
          </section>
        )}

        {/* RÉSULTATS — mise en page claire */}
        {result && (
          <section className="space-y-8">
            {/* Bandeau Overview (Score + label) */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <div className="text-xs uppercase tracking-widest text-white/60">
                    {language === "fr" ? "Aperçu" : "Overview"}
                  </div>
                  <h2 className="text-xl font-semibold">
                    {language === "fr" ? "Résultats de l’analyse" : "Analysis results"}
                  </h2>
                  <p className="mt-2 text-sm text-white/80">
                    {language === "fr"
                      ? "Résumé des principaux enseignements : angles, entités, jeux de données et feedback."
                      : "Summary of key insights: angles, entities, datasets and feedback."}
                  </p>
                </div>
                <div className="md:justify-self-end">
                  <DataficationScoreCard
                    score={result.score}
                    profileLabel={result.profile_label ?? ""}
                    language={language}
                  />
                </div>
              </div>
            </div>

            {/* Entités */}
            <section>
              <header className="mb-3">
                <div className="text-xs uppercase tracking-widest text-white/60">
                  {language === "fr" ? "Analyse" : "Analysis"}
                </div>
                <h3 className="text-xl font-semibold">
                  {language === "fr" ? "Entités & Thèmes" : "Entities & Themes"}
                </h3>
              </header>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <EntitiesSummaryCard entities={result.entities ?? []} language={language} />
              </div>
            </section>

            {/* Angles (grille 2 colonnes) */}
            <section>
              <header className="mb-3">
                <div className="text-xs uppercase tracking-widest text-white/60">Édito</div>
                <h3 className="text-xl font-semibold">
                  {language === "fr" ? "Angles éditoriaux" : "Editorial angles"}
                </h3>
              </header>
              <div className="grid gap-4 sm:grid-cols-2">
                {(() => {
                  const angles: AngleResources[] | undefined =
                    result.angle_resources ?? result.angles_resources;
                  return angles?.map((angle) => (
                    <AngleCard key={angle.index} angle={angle} language={language} />
                  ));
                })()}
              </div>
            </section>

            {/* Feedback */}
            <section>
              <header className="mb-3">
                <div className="text-xs uppercase tracking-widest text-white/60">Qualité</div>
                <h3 className="text-xl font-semibold">Feedback</h3>
              </header>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <FeedbackForm analysisId={result.id} language={language} />
              </div>
            </section>
          </section>
        )}
      </div>
    </div>
  );
}
