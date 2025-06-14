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
  source_url?: string | null;
  formats?: string[] | null;
  organization?: string | null;
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

  return (
    <Card className="shadow-md rounded-2xl">
      <CardContent className="p-6 space-y-4">
        {/* Title */}
        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
          <Globe className="size-5" />
          {t(language, "Suggested Datasets", "Jeux de données suggérés")}
        </h3>

        {/* Accordion list */}
        <Accordion type="multiple" className="w-full space-y-2">
          {datasets.map((ds, idx) => (
            <AccordionItem key={idx} value={String(idx)} className="border rounded-lg">
              <AccordionTrigger className="px-4 py-2 font-medium text-left">
                {ds.title || t(language, "Untitled dataset", "Jeu sans titre")}
              </AccordionTrigger>

              <AccordionContent className="px-4 pb-4 space-y-2 text-sm">
                <div className="flex flex-col gap-1">
                  {ds.found_by && (
                    <InfoLine label={t(language, "Found by", "Trouvé par")} value={ds.found_by} />
                  )}
                  {ds.source_name && (
                    <InfoLine label={t(language, "Source", "Source")} value={ds.source_name} />
                  )}
                  {ds.source_url && (
                    <InfoLine
                      label="URL"
                      value={
                        <a
                          href={ds.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 underline break-all"
                        >
                          {ds.source_url}
                        </a>
                      }
                    />
                  )}
                  {Array.isArray(ds.formats) && ds.formats.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      <span className="font-medium mr-1">{t(language, "Formats:", "Formats :")}</span>
                      {ds.formats.map((f) => (
                        <Badge key={f}>{f}</Badge>
                      ))}
                    </div>
                  )}
                  {ds.organization && (
                    <InfoLine label={t(language, "Organization", "Organisation")} value={ds.organization} />
                  )}
                  {ds.license && <InfoLine label="License" value={ds.license} />}
                  {ds.last_modified && (
                    <InfoLine label={t(language, "Last modified", "Modifié le")} value={ds.last_modified} />
                  )}
                  {typeof ds.richness === "number" && (
                    <InfoLine label={t(language, "Richness", "Richesse")} value={ds.richness.toFixed(0)} />
                  )}
                  {ds.description && (
                    <div>
                      <span className="font-medium mr-1">{t(language, "Description:", "Description :")}</span>
                      <span>{ds.description}</span>
                    </div>
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
      <span className="font-medium">{label}:</span>
      <span className="break-all">{value}</span>
    </div>
  );
}
