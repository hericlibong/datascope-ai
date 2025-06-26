// src/components/results/AngleCard.tsx
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge }   from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Globe }   from "lucide-react";
import type { AngleResources } from "@/types/analysis";

interface Props {
  angle: AngleResources;
  language: "en" | "fr";
}

// petit helper de traduction
const t = (lang: "en" | "fr", en: string, fr: string) => (lang === "fr" ? fr : en);

export default function AngleCard({ angle, language }: Props) {
  console.log("[AngleCard] props.angle =", angle);   // ← log important

  // Sécurisation de tous les tableaux
  const datasets = Array.isArray(angle.datasets) ? angle.datasets : [];
  const sources = Array.isArray(angle.sources) ? angle.sources : [];
  const visualizations = Array.isArray(angle.visualizations) ? angle.visualizations : [];

  return (
    <Card className="shadow rounded-2xl mb-6">
      <CardContent className="p-5 space-y-4">
        {/* --- Titre / description de l’angle --- */}
        <h3 className="text-lg font-semibold">{angle.title}</h3>
        <p className="text-sm text-gray-700 whitespace-pre-wrap">
          {angle.description}
        </p>

        {/* ========= DATASETS (connecteur + LLM) ========= */}
        {datasets.length > 0 && (
          <>
            <h4 className="font-medium mt-2 mb-1 flex items-center gap-1">
              <Globe className="size-4" />
              {t(language, "Datasets", "Jeux de données")}
            </h4>
            <Accordion type="multiple" className="w-full">
              {datasets.map((ds, i) => {
                const href = (ds as any).link ?? ds.source_url ?? "#";
                return (
                  <AccordionItem key={i} value={String(i)} className="border rounded my-1">
                    <AccordionTrigger className="px-3 py-2 font-medium text-left">
                      {ds.title || t(language, "Untitled dataset", "Jeu sans titre")}
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4 space-y-2 text-sm">
                      <p className="whitespace-pre-wrap">{ds.description || "—"}</p>
                      <div className="flex flex-col gap-1">
                        <Info label={t(language, "Found by", "Trouvé par")} value={ds.found_by} />
                        <Info label={t(language, "Source",   "Source")}     value={ds.source_name} />
                        {/* lien cliquable */}
                        <div className="flex gap-1">
                          <span className="font-medium">{t(language, "Link", "Lien")}:</span>
                          <a href={href} target="_blank" rel="noopener noreferrer"
                             className="text-blue-600 hover:underline break-all">
                            {href}
                          </a>
                        </div>
                        {/* formats */}
                        {ds.formats?.length > 0 && (
                          <div className="flex flex-wrap gap-1 items-center">
                            <span className="font-medium mr-1">Formats:</span>
                            {ds.formats.map((f:string)=> <Badge key={f}>{f}</Badge>)}
                          </div>
                        )}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          </>
        )}

        {/* ========= SOURCES LLM ========= */}
        {sources.length > 0 && (
          <>
            <h4 className="font-medium mt-4 mb-1">
              {t(language, "Additional open-data portals", "Autres portails open-data")}
            </h4>
            <ul className="list-disc list-inside space-y-1">
              {sources.map((s, idx)=>(
                <li key={idx}>
                  <a href={s.link} target="_blank" rel="noopener noreferrer"
                     className="text-blue-600 hover:underline">
                    {s.title}
                  </a>
                  {s.description && <> — <span className="text-xs">{s.description}</span></>}
                </li>
              ))}
            </ul>
          </>
        )}

        {/* ========= VISUALISATIONS ========= */}
        {visualizations.length > 0 && (
          <>
            <h4 className="font-medium mt-4 mb-1">
              {t(language, "Possible visualizations", "Visualisations possibles")}
            </h4>
            <ul className="list-square list-inside space-y-1">
              {visualizations.map((v, idx)=>(
                <li key={idx}>
                  <strong>{v.chart_type}</strong> – {v.title}
                  {v.note && <> ({v.note})</>}
                </li>
              ))}
            </ul>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function Info({ label, value }: {label:string; value:any}) {
  if (!value) return null;
  return (
    <div className="flex gap-1">
      <span className="font-medium">{label}:</span>
      <span className="break-all">{value}</span>
    </div>
  );
}
