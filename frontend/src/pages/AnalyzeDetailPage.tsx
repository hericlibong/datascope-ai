import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { authFetch } from "@/api/auth";
import { useLanguage } from "@/contexts/LanguageContext";

import ResultLayout from "@/components/results/ResultLayout";
import ResultOverview from "@/components/results/ResultOverView";

import { DataficationScoreCard } from "@/components/results/DataficationScoreCard";
import { EntitiesSummaryCard } from "@/components/results/EntitiesSummaryCard";
import AngleCard from "@/components/results/AngleCard";
import { FeedbackForm } from "@/components/results/FeedbackForm";
import DatasetSuggestionsCard from "@/components/results/DatasetSuggestionsCard";

import type { AngleResources } from "@/types/analysis";

export default function AnalyzeDetailPage() {
  const { id } = useParams();
  const { language } = useLanguage();

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 🔎 Chargement des résultats d’analyse
  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);

    authFetch(`http://localhost:8000/api/analysis/${id}/`)
      .then((res) =>
        res.ok
          ? res.json()
          : res
              .json()
              .then((err: any) =>
                Promise.reject(
                  err?.detail || (language === "fr" ? "Erreur de récupération des résultats" : "Failed to fetch results")
                )
              )
      )
      .then(setData)
      .catch((err) => setError(typeof err === "string" ? err : language === "fr" ? "Erreur" : "Error"))
      .finally(() => setLoading(false));
  }, [id, language]);

  // ⛑️ États de confort
  if (loading)
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <div className="mx-auto max-w-3xl px-4 py-16 text-center">
          {language === "fr" ? "Chargement…" : "Loading…"}
        </div>
      </div>
    );

  if (error)
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <div className="mx-auto max-w-3xl px-4 py-16 text-center text-red-300">{error}</div>
      </div>
    );

  if (!data)
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <div className="mx-auto max-w-3xl px-4 py-16 text-center">
          {language === "fr" ? "Aucune donnée" : "No data"}
        </div>
      </div>
    );

  // 📌 Données utiles
  const angles: AngleResources[] | undefined = data.angle_resources ?? data.angles_resources;
  const score: number = Number.isFinite(data?.score) ? data.score : 0;

  // 🧭 Sections pour la SideNav (modèle validé)
  const sections = [
    { id: "overview", label: language === "fr" ? "Vue d'ensemble" : "Overview" },
    { id: "article", label: language === "fr" ? "Résumé article" : "Article summary" },
    { id: "entities", label: language === "fr" ? "Entités" : "Entities" },
    { id: "angles", label: language === "fr" ? "Angles (5)" : "Angles (5)" },
    { id: "datasets", label: language === "fr" ? "Datasets" : "Datasets" },
    { id: "feedback", label: "Feedback" },
  ];

  // ✨ Points clés rapides pour l’Overview (2–3 bullets)
  const summaryPoints: string[] = [
    (language === "fr" ? "Score global : " : "Overall score: ") + `${score}%`,
    (language === "fr" ? "Angles détectés : " : "Angles detected: ") + `${angles?.length ?? 0}`,
    (language === "fr" ? "Entités extraites : " : "Entities extracted: ") + `${data?.entities?.length ?? 0}`,
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto w-full max-w-7xl">
        <ResultLayout sections={sections}>
          {/* OVERVIEW — titre, date, gauge, CTA export */}
          <section id="overview" className="scroll-mt-24 space-y-6">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
              {/* Bandeau compact avec score à droite */}
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <div className="text-xs uppercase tracking-widest text-white/60">
                    {language === "fr" ? "Analyse" : "Analysis"}
                  </div>
                  <h1 className="text-2xl font-semibold">
                    {(language === "fr" ? "Résultats de l’analyse" : "Analysis results") + (id ? ` #${id}` : "")}
                  </h1>
                  {data?.article?.title ? (
                    <p className="text-sm text-white/80">{data.article.title}</p>
                  ) : null}
                  {data?.created_at ? (
                    <p className="text-xs text-white/60">{new Date(data.created_at).toLocaleString()}</p>
                  ) : null}
                </div>

                {/* Tu peux garder le ResultOverview si tu préfères le bloc “Résumé + Export” */}
                <div className="md:justify-self-end">
                  <DataficationScoreCard
                    score={score}
                    profileLabel={data?.profile_label ?? ""}
                    language={language}
                  />
                </div>
              </div>

              {/* Résumé en bullets (optionnel si tu utilises ResultOverview) */}
              <div className="mt-6">
                <ResultOverview
                  title={language === "fr" ? "Aperçu" : "Overview"}
                  score={score}
                  summary={summaryPoints}
                />
              </div>
            </div>
          </section>

          {/* ARTICLE — résumé de l’article analysé (pas de formulaire ici) */}
          <section id="article" className="scroll-mt-24">
            <header className="mb-3">
              <div className="text-xs uppercase tracking-widest text-white/60">
                {language === "fr" ? "Texte analysé" : "Analyzed text"}
              </div>
              <h2 className="text-xl font-semibold">{language === "fr" ? "Résumé de l’article" : "Article summary"}</h2>
            </header>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
              <div className="prose prose-invert max-w-none whitespace-pre-line text-white/90">
                {data?.article?.content || (language === "fr" ? "Aucun résumé disponible." : "No summary available.")}
              </div>
            </div>
          </section>

          {/* ENTITÉS */}
          <section id="entities" className="scroll-mt-24">
            <header className="mb-3">
              <div className="text-xs uppercase tracking-widest text-white/60">
                {language === "fr" ? "Analyse" : "Analysis"}
              </div>
              <h2 className="text-xl font-semibold">
                {language === "fr" ? "Entités & Thèmes" : "Entities & Themes"}
              </h2>
            </header>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <EntitiesSummaryCard entities={data?.entities ?? []} language={language} />
            </div>
          </section>

          {/* ANGLES — grille 2 colonnes (5 angles) */}
          {!!angles?.length && (
            <section id="angles" className="scroll-mt-24">
              <header className="mb-3">
                <div className="text-xs uppercase tracking-widest text-white/60">Édito</div>
                <h2 className="text-xl font-semibold">
                  {language === "fr" ? "Angles éditoriaux" : "Editorial angles"}
                </h2>
              </header>

              <div className="grid gap-4 sm:grid-cols-2">
                {angles.map((angle) => (
                  <AngleCard key={angle.index} angle={angle} language={language} />
                ))}
              </div>
            </section>
          )}

          {/* DATASETS — suggestions liées */}
          <section id="datasets" className="scroll-mt-24">
            <header className="mb-3">
              <div className="text-xs uppercase tracking-widest text-white/60">
                {language === "fr" ? "Données" : "Data"}
              </div>
              <h2 className="text-xl font-semibold">
                {language === "fr" ? "Jeux de données suggérés" : "Suggested datasets"}
              </h2>
            </header>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              {/* On tente plusieurs clés possibles côté API */}
              <DatasetSuggestionsCard
                datasets={
                  data?.dataset_suggestions ??
                  data?.datasets ??
                  data?.datasets_suggestions ??
                  []
                }
                language={language}
              />
            </div>
          </section>

          {/* FEEDBACK */}
          <section id="feedback" className="scroll-mt-24 pb-8">
            <header className="mb-3">
              <div className="text-xs uppercase tracking-widest text-white/60">Qualité</div>
              <h2 className="text-xl font-semibold">Feedback</h2>
            </header>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <FeedbackForm analysisId={data?.id} language={language} />
            </div>
          </section>
        </ResultLayout>
      </div>
    </div>
  );
}
