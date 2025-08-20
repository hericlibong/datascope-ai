import { useMemo, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";

import { DataficationScoreCard } from "@/components/results/DataficationScoreCard";
import { EntitiesSummaryCard } from "@/components/results/EntitiesSummaryCard";
import AngleCard from "@/components/results/AngleCard";
import { FeedbackForm } from "@/components/results/FeedbackForm";
import AngleKeyCard from "@/components/results/AngleKeyCard";
import type { AngleResources } from "@/types/analysis";

import { getAccessToken } from "@/api/auth";
import { useLanguage } from "@/contexts/LanguageContext";
import { detectLang } from "@/utils/langDetect";

import { getScoreTheme } from "@/lib/scoreTheme";
import BadgePill from "@/components/results/BadgePill";
import KpiStat from "@/components/results/KpiStat";
import ResultGauge from "@/components/results/ResultGauge";

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
  const [showArticle, setShowArticle] = useState(false);

  const showForm = !result;

  const countWords = (str: string) => str.trim().split(/\s+/).filter(Boolean).length;

  const wordCount = useMemo(
    () => (result?.article?.content ? countWords(result.article.content) : 0),
    [result?.article?.content]
  );

  const angles: AngleResources[] | undefined = result?.angle_resources ?? result?.angles_resources;
  const anglesCount = angles?.length ?? 0;
  const entitiesCount = Array.isArray(result?.entities) ? result.entities.length : 0;
  const score = Number.isFinite(result?.score) ? result.score : 0;
  const theme = getScoreTheme(score);

  const topAnglesLabels: string[] = useMemo(() => {
    if (!angles?.length) return [];
    return angles.slice(0, 3).map((a, i) =>
      (a as any)?.title ?? (a as any)?.name ?? (language === "fr" ? `Angle ${i + 1}` : `Angle ${i + 1}`)
    );
  }, [angles, language]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);
    setResult(null);

    if (!text && !file) {
      setLoading(false);
      setErrorMessage(
        language === "fr" ? "Veuillez entrer un texte ou charger un fichier." : "Please enter text or upload a file."
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
      } catch {
        setErrorMessage(
          language === "fr" ? "Erreur de lecture du fichier. Veuillez réessayer." : "Error reading the file. Please try again."
        );
        setLoading(false);
        return;
      }
    }

    const wc = countWords(contentToAnalyze);
    if (wc < 220) {
      setErrorMessage(
        language === "fr"
          ? `Le texte est trop court (${wc} mots). Merci de fournir un texte d'au moins 220 mots.`
          : `Text is too short (${wc} words). Please provide at least 220 words.`
      );
      setLoading(false);
      return;
    }

    const detectedLang = detectLang(contentToAnalyze);
    if (detectedLang !== language) {
      const msg =
        detectedLang === "latin"
          ? language === "fr"
            ? "Le texte semble être du Lorem Ipsum (latin)."
            : "The text appears to be Lorem Ipsum (Latin)."
          : detectedLang === "other"
          ? language === "fr"
            ? "Impossible de détecter clairement la langue du texte."
            : "Unable to clearly detect the language."
          : language === "fr"
          ? "Le texte n'est pas en français."
          : "The text is not in English.";
      setErrorMessage(msg);
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
          language === "fr" ? "Votre session a expiré, merci de vous reconnecter." : "Your session has expired, please log in again."
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
          language === "fr" ? "Votre session a expiré, merci de vous reconnecter." : "Your session has expired, please log in again."
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
          language === "fr" ? "Votre session a expiré, merci de vous reconnecter." : "Your session has expired, please log in again."
        );
        setLoading(false);
        return;
      }

      if (!res.ok) {
        setErrorMessage(language === "fr" ? "Impossible de récupérer les résultats." : "Unable to retrieve results.");
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
      <div className="mx-auto w-full max-w-7xl px-4 py-10 space-y-10">
        {/* HEADER */}
        {showForm && (
          <header>
            <div className="text-xs uppercase tracking-widest text-white/60">
              {language === "fr" ? "Analyse" : "Analysis"}
            </div>
            <h1 className="text-2xl font-semibold">
              {language === "fr" ? "Lancer une nouvelle analyse" : "Start a new analysis"}
            </h1>
            <p className="mt-2 text-sm text-white/80">
              {language === "fr"
                ? "Collez votre texte ou chargez un fichier. Les résultats s’affichent dans une mise en page claire."
                : "Paste your text or upload a file. Results are shown in a clean layout."}
            </p>
          </header>
        )}

        {/* FORMULAIRE — caché quand result est présent */}
        {showForm && (
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
        )}

        {/* RÉSULTATS */}
        {result && (
          <section className="space-y-10">
            {/* OVERVIEW riche */}
            <div className="rounded-3xl border border-white/10 bg-white/5 p-7 backdrop-blur-sm">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                  <div className="text-[11px] uppercase tracking-widest text-white/60">
                    {language === "fr" ? "Aperçu" : "Overview"}
                  </div>
                  <h2 className="mt-1 text-2xl md:text-3xl font-extrabold">
                    {language === "fr" ? "Résultats de l’analyse" : "Analysis results"}
                  </h2>
                </div>
                <BadgePill className={theme.chip}>
                  <span className={`h-2 w-2 rounded-full bg-gradient-to-r ${theme.grad}`} />
                  <span className="font-medium">{theme.label}</span>
                </BadgePill>
              </div>

              <div className="mt-6 grid gap-6 lg:grid-cols-[1fr,220px]">
                <div className="grid gap-4 sm:grid-cols-2">
                  <KpiStat
                    label={language === "fr" ? "Score global" : "Overall score"}
                    value={<span>{score}%</span>}
                    hint={result?.profile_label ?? undefined}
                  />
                  <KpiStat
                    label={language === "fr" ? "Angles détectés" : "Angles detected"}
                    value={anglesCount}
                    hint={language === "fr" ? "Toujours 5 max" : "Up to 5"}
                    accent="sky"
                  />
                  <KpiStat
                    label={language === "fr" ? "Entités extraites" : "Entities extracted"}
                    value={entitiesCount}
                    hint={language === "fr" ? "Total brutes" : "Raw total"}
                    accent="pink"
                  />
                  <KpiStat
                    label={language === "fr" ? "Mots du texte" : "Word count"}
                    value={wordCount}
                    accent="emerald"
                  />
                </div>

                <div className="flex items-center justify-center">
                  {Number.isFinite(result?.score) ? (
                    <ResultGauge score={score} />
                  ) : (
                    <DataficationScoreCard
                      score={result?.score}
                      profileLabel={result?.profile_label ?? ""}
                      language={language}
                    />
                  )}
                </div>
              </div>

              {topAnglesLabels.length > 0 && (
                <div className="mt-6">
                  <div className="text-[11px] uppercase tracking-widest text-white/60 mb-2">
                    {language === "fr" ? "Angles clés" : "Key angles"}
                  </div>

                  <div
                    className="
        grid gap-3
        sm:grid-cols-2
        lg:grid-cols-3
      "
                    role="list"
                  >
                    {topAnglesLabels.map((t, i) => (
                      <AngleKeyCard key={i} index={i + 1} title={t} />
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-5">
                <Button variant="secondary" onClick={() => setResult(null)}>
                  {language === "fr" ? "Modifier la requête" : "Edit query"}
                </Button>
              </div>
            </div>

            {/* TEXTE ANALYSÉ */}
            {result?.article?.content && (
              <Collapsible
                open={showArticle}
                onOpenChange={setShowArticle}
                className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                {/* Header clickable – style harmonisé avec les vignettes */}
                <CollapsibleTrigger asChild>
                  <div
                    role="button"
                    className="
          w-full cursor-pointer select-none
          px-6 py-4
          flex items-center justify-between gap-3
          hover:bg-white/[0.06] transition
        "
                    aria-expanded={showArticle}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-white/70"></span>
                      <div>
                        <div className="text-[11px] uppercase tracking-widest text-white/60">
                          {language === "fr" ? "Analyse" : "Analysis"}
                        </div>
                        <h3 className="text-lg font-semibold text-white/95">
                          {language === "fr" ? "Texte analysé" : "Analyzed text"}
                        </h3>
                      </div>

                      {/* Badge compteur de mots */}
                      <span className="ml-3 rounded-full border border-white/10 bg-white/10 px-2 py-0.5 text-[11px] text-white/70">
                        {((result?.article?.content || "").trim().split(/\s+/).filter(Boolean).length) || 0} {" "}
                        {language === "fr" ? "mots" : "words"}
                      </span>
                    </div>

                    <ChevronDown
                      className={`h-5 w-5 text-white/70 transition-transform ${showArticle ? "rotate-180" : ""}`}
                      aria-hidden="true"
                    />
                  </div>
                </CollapsibleTrigger>

                {/* Contenu repliable avec séparateur discret */}
                <CollapsibleContent className="px-6 pb-6 pt-0">
                  <div className="mt-2 border-t border-white/10 pt-4 prose prose-invert max-w-none whitespace-pre-line text-white/90">
                    {result.article.content}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            )}

            {/* ENTITÉS */}
            <section>
            <EntitiesSummaryCard entities={result?.entities ?? []} language={language} />
          </section>


            {/* ANGLES — grille 2 colonnes */}
            <section>
              <header className="mb-3">
                <div className="text-[11px] uppercase tracking-widest text-white/60">Édito</div>
                <h3 className="text-xl font-semibold">
                  {language === "fr" ? "Angles éditoriaux" : "Editorial angles"}
                </h3>
              </header>
              <div className="grid gap-4 sm:grid-cols-2">
                {(angles ?? []).map((angle) => (
                  <AngleCard key={angle.index} angle={angle} language={language} />
                ))}
              </div>
            </section>

            {/* FEEDBACK */}
            <section className="pb-8">
              <header className="mb-3">
                <div className="text-[11px] uppercase tracking-widest text-white/60">Qualité</div>
                <h3 className="text-xl font-semibold">Feedback</h3>
              </header>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <FeedbackForm analysisId={result?.id} language={language} />
              </div>
            </section>
          </section>
        )}
      </div>
    </div>
  );
}
