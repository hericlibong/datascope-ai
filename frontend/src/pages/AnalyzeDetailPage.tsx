import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { authFetch } from "@/api/auth";
import { useLanguage } from "@/contexts/LanguageContext";
import { ResultLayout } from "@/components/results/ResultLayout";
import { OverviewSection } from "@/components/results/OverviewSection";
import { EditorialAnglesCard } from "@/components/results/EditorialAnglesCard";
import { EntitiesSummaryCard } from "@/components/results/EntitiesSummaryCard";
import { DatasetSuggestionsCard } from "@/components/results/DatasetSuggestionsCard";
import { FeedbackForm } from "@/components/results/FeedbackForm";
import { ResultCard } from "@/components/results/ResultCard";
import { FileText, Users, Database, MessageSquare } from "lucide-react";

// Types for the analysis data
interface AnalysisData {
  id: number;
  content?: string;
  source?: string;
  url?: string;
  created_at?: string;
  score?: number;
  entities?: Array<{
    id: number;
    type: "PER" | "ORG" | "LOC" | "DATE" | "NUM" | "MISC";
    value: string;
    context?: string | null;
  }>;
  editorial_angles?: Array<{
    title: string;
    description: string;
  }>;
  dataset_suggestions?: Array<{
    id?: number;
    title: string;
    description?: string | null;
    source_name?: string | null;
    link?: string | null;
    source_url?: string | null;
    formats?: string[] | null;
    organisation?: string | null;
    organization?: string | null;
    licence?: string | null;
    license?: string | null;
    last_modified?: string | null;
    richness?: number | null;
    found_by?: string | null;
  }>;
}

export default function AnalyzeDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  useEffect(() => {
    if (!id) return;
    authFetch(`http://localhost:8000/api/analysis/${id}/`)
      .then((res) =>
        res.ok
          ? res.json()
          : res.json().then((err: any) => Promise.reject(err.detail || (language === "fr" ? "Erreur" : "Error")))
      )
      .then(setData)
      .catch((err) => setError(typeof err === "string" ? err : (language === "fr" ? "Erreur" : "Error")))
      .finally(() => setLoading(false));
  }, [id, language]);

  const t = (en: string, fr: string) => language === "fr" ? fr : en;

  if (loading) {
    return (
      <ResultLayout language={language}>
        <div className="space-y-8">
          <OverviewSection language={language} isLoading={true} />
          <ResultCard title={t("Editorial Angles", "Angles éditoriaux")} language={language} isLoading={true} />
          <ResultCard title={t("Entities & Themes", "Entités & thèmes")} language={language} isLoading={true} />
          <ResultCard title={t("Dataset Suggestions", "Jeux de données suggérés")} language={language} isLoading={true} />
          <ResultCard title={t("Feedback", "Feedback")} language={language} isLoading={true} />
        </div>
      </ResultLayout>
    );
  }

  if (error) {
    return (
      <ResultLayout language={language}>
        <div className="text-center mt-10">
          <ResultCard error={error} language={language} />
        </div>
      </ResultLayout>
    );
  }

  if (!data) return null;

  return (
    <ResultLayout language={language}>
      <div className="space-y-8">
        {/* Overview Section */}
        <OverviewSection 
          score={data.score} 
          language={language}
          source={data.source || data.url}
          dateAnalyzed={data.created_at}
        />

        {/* Editorial Angles Section */}
        <section id="angles">
          <div className="mb-4">
            <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">
              {t("EDITORIAL ANGLES", "ANGLES ÉDITORIAUX")}
            </p>
          </div>
          {data.editorial_angles && data.editorial_angles.length > 0 ? (
            <EditorialAnglesCard angles={data.editorial_angles} language={language} />
          ) : (
            <ResultCard 
              title={t("Editorial Angles", "Angles éditoriaux")}
              language={language}
              isEmpty={true}
              icon={<FileText className="w-5 h-5" />}
            />
          )}
        </section>

        {/* Entities Section */}
        <section id="entities">
          <div className="mb-4">
            <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">
              {t("ENTITIES & THEMES", "ENTITÉS & THÈMES")}
            </p>
          </div>
          {data.entities && data.entities.length > 0 ? (
            <EntitiesSummaryCard entities={data.entities} language={language} />
          ) : (
            <ResultCard 
              title={t("Entities & Themes", "Entités & thèmes")}
              language={language}
              isEmpty={true}
              icon={<Users className="w-5 h-5" />}
            />
          )}
        </section>

        {/* Datasets Section */}
        <section id="datasets">
          <div className="mb-4">
            <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">
              {t("DATASET SUGGESTIONS", "JEUX DE DONNÉES SUGGÉRÉS")}
            </p>
          </div>
          {data.dataset_suggestions && data.dataset_suggestions.length > 0 ? (
            <DatasetSuggestionsCard datasets={data.dataset_suggestions} language={language} />
          ) : (
            <ResultCard 
              title={t("Dataset Suggestions", "Jeux de données suggérés")}
              language={language}
              isEmpty={true}
              icon={<Database className="w-5 h-5" />}
            />
          )}
        </section>

        {/* Feedback Section */}
        <section id="feedback">
          <div className="mb-4">
            <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">
              {t("FEEDBACK", "FEEDBACK")}
            </p>
          </div>
          <ResultCard 
            className="rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm"
            icon={<MessageSquare className="w-5 h-5" />}
          >
            <FeedbackForm analysisId={parseInt(id!)} language={language} />
          </ResultCard>
        </section>
      </div>
    </ResultLayout>
  );
}