import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Globe } from "lucide-react";

// -------------------------------
// Types
// -------------------------------
export interface DatasetSuggestion {
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
}

interface Props {
  datasets: DatasetSuggestion[] | undefined;
  language: "en" | "fr";
}

// -------------------------------
// Helpers
// -------------------------------
const t = (lang: "en" | "fr", en: string, fr: string) => (lang === "fr" ? fr : en);

// -------------------------------
// Main component (named export + default)
// -------------------------------
export function DatasetSuggestionsCard({ datasets, language }: Props) {
  if (!Array.isArray(datasets) || datasets.length === 0) return null;

  const MAX_LEN = 600;
  const truncate = (txt: string) =>
    txt.length > MAX_LEN ? txt.slice(0, MAX_LEN).replace(/\s+\S*$/, "") + "…" : txt;

  return (
    <Card className="shadow-md rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm">
      <CardContent className="p-6 space-y-4">
        {/* Title */}
        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2 text-white">
          <Globe className="size-5" />
          {t(language, "Suggested Datasets", "Jeux de données suggérés")}
        </h3>

        {/* Accordion list */}
        <Accordion type="multiple" className="w-full space-y-2">
          {datasets.map((ds, idx) => (
            <AccordionItem key={idx} value={String(idx)} className="border border-white/10 rounded-lg bg-white/5">
              <AccordionTrigger className="px-4 py-2 font-medium text-left text-white hover:no-underline">
                {ds.title || t(language, "Untitled dataset", "Jeu sans titre")}
              </AccordionTrigger>

              <AccordionContent className="px-4 pb-4 space-y-2 text-sm">
                <div className="flex flex-col gap-1">
                  {/* FOUND BY */}
                  {ds.found_by && (
                    <InfoLine label={t(language, "Found by", "Trouvé par")} value={ds.found_by} />
                  )}

                  {/* SOURCE NAME */}
                  {ds.source_name && (
                    <InfoLine label={t(language, "Source", "Source")} value={ds.source_name} />
                  )}

                  {/* URL */}
                  {(ds.source_url ?? ds.link) && (
                    <InfoLine
                      label="URL"
                      value={
                        <a
                          href={ds.source_url ?? ds.link ?? "#"}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-400 hover:text-indigo-300 hover:underline break-all"
                        >
                          {ds.source_url ?? ds.link}
                        </a>
                      }
                    />
                  )}

                  {/* FORMATS */}
                  {Array.isArray(ds.formats) && ds.formats.length > 0 && (
                    <div className="flex flex-wrap gap-1 items-center">
                      <span className="font-medium mr-1 text-slate-300">{t(language, "Formats:", "Formats :")}</span>
                      {ds.formats.map((f) => (
                        <Badge key={f} className="bg-white/10 text-slate-200 border-white/20">{f}</Badge>
                      ))}
                    </div>
                  )}

                  {/* ORGANISATION */}
                  {(ds.organisation ?? ds.organization) && (
                    <InfoLine
                      label={t(language, "Organization", "Organisation")}
                      value={ds.organisation ?? ds.organization}
                    />
                  )}

                  {/* LICENCE */}
                  {(ds.licence ?? ds.license) && (
                    <InfoLine label="License" value={ds.licence ?? ds.license} />
                  )}

                  {/* LAST MODIFIED */}
                  {ds.last_modified && (
                    <InfoLine
                      label={t(language, "Last modified", "Modifié le")}
                      value={ds.last_modified}
                    />
                  )}

                  {/* RICHNESS */}
                  {typeof ds.richness === "number" && (
                    <InfoLine
                      label={t(language, "Richness", "Richesse")}
                      value={ds.richness.toFixed(0)}
                    />
                  )}

                  {/* DESCRIPTION */}
                  {ds.description && (
                    <p className="text-sm whitespace-pre-line mt-1 text-slate-300">
                      {truncate(ds.description)}
                    </p>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}

export default DatasetSuggestionsCard;

// -------------------------------
// Sub‑component for label/value
// -------------------------------
interface InfoProps {
  label: string;
  value: React.ReactNode;
}
function InfoLine({ label, value }: InfoProps) {
  return (
    <div className="flex gap-1">
      <span className="font-medium text-slate-300">{label}:</span>
      <span className="break-all text-slate-200">{value}</span>
    </div>
  );
}
