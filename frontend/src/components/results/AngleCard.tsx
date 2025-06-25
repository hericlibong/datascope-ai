/* -------------------------------------------------------------------------- */
/*  AngleCard.tsx – 1 carte = 1 angle                                         */
/* -------------------------------------------------------------------------- */

import React from "react";

/* shadcn/ui */
import { Card, CardContent }            from "@/components/ui/card";
import { Accordion,
         AccordionItem,
         AccordionTrigger,
         AccordionContent }             from "@/components/ui/accordion";
import { Badge }                        from "@/components/ui/badge";

/* icônes lucide-react */
import { Lightbulb, Globe, BarChart }   from "lucide-react";

/* types partagés */
import type {
  AngleResources,
  DatasetSuggestion,
  LLMSourceSuggestion,
  VizSuggestion,
} from "@/types/analysis";

/* -------------------------------------------------------------------------- */
/*  Helpers locaux                                                            */
/* -------------------------------------------------------------------------- */

/** trad rapide EN/FR (à affiner plus tard) */
const t = (lang: "en" | "fr", en: string, fr: string) =>
  lang === "fr" ? fr : en;

/** affiche une liste de badges formats, keywords, etc. */
function Badges({ items }: { items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1">
      {items.map((txt) => (
        <Badge key={txt}>{txt}</Badge>
      ))}
    </div>
  );
}

/** ligne clé / valeur */
function InfoLine({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-1 text-sm">
      <span className="font-medium">{label}:</span>
      <span className="break-all">{children}</span>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Sous-cartes : Datasets, Sources LLM, Visus                                */
/* -------------------------------------------------------------------------- */

function DatasetList({ list, lang }: { list: DatasetSuggestion[]; lang: "en"|"fr" }) {
  if (!Array.isArray(list) || list.length === 0) return null;

  return (
    <section className="space-y-2">
      <h4 className="flex items-center gap-1 font-semibold">
        <Globe className="size-4" />
        {t(lang, "Datasets (connectors)", "Jeux de données (connecteurs)")}
      </h4>

      <Accordion type="multiple" className="w-full space-y-1">
        {list.map((ds, i) => (
          <AccordionItem key={i} value={String(i)} className="border rounded">
            <AccordionTrigger className="px-3 py-1 text-left">{ds.title}</AccordionTrigger>
            <AccordionContent className="px-4 pb-3 space-y-1">
              {ds.description && <p className="text-sm whitespace-pre-line">{ds.description}</p>}
              <InfoLine label="URL">
                <a href={ds.source_url} target="_blank" className="text-blue-600 hover:underline">
                  {ds.source_url}
                </a>
              </InfoLine>
              <InfoLine label={t(lang,"Source","Source")}>{ds.source_name}</InfoLine>
              {ds.organization && <InfoLine label={t(lang,"Org.","Org.")}>{ds.organization}</InfoLine>}
              {ds.formats?.length && <Badges items={ds.formats} />}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  );
}

function SourceList({ list, lang }: { list: LLMSourceSuggestion[]; lang:"en"|"fr" }) {
  if (!Array.isArray(list) || list.length === 0) return null;

  return (
    <section className="space-y-2">
      <h4 className="flex items-center gap-1 font-semibold">
        <Lightbulb className="size-4" />
        {t(lang, "Open-data portals (LLM)", "Portails open-data (LLM)")}
      </h4>

      {list.map((src, i) => (
        <div key={i} className="border rounded p-3 space-y-1">
          <a href={src.link} target="_blank" className="font-medium text-blue-700 hover:underline">
            {src.title}
          </a>
          <p className="text-sm">{src.description}</p>
          <InfoLine label={t(lang,"Provider","Fournisseur")}>{src.source}</InfoLine>
        </div>
      ))}
    </section>
  );
}

function VizList({ list, lang }: { list: VizSuggestion[]; lang:"en"|"fr" }) {
  if (!Array.isArray(list) || list.length === 0) return null;

  return (
    <section className="space-y-2">
      <h4 className="flex items-center gap-1 font-semibold">
        <BarChart className="size-4" />
        {t(lang, "Visual ideas", "Idées de visu")}
      </h4>

      {list.map((v, i) => (
        <div key={i} className="border rounded p-3 space-y-1 text-sm">
          <p className="font-medium">{v.title}</p>
          <InfoLine label="Type">{v.chart_type}</InfoLine>
          <InfoLine label="X">{v.x}</InfoLine>
          <InfoLine label="Y">{v.y}</InfoLine>
          {v.note && <InfoLine label={t(lang,"Note","Note")}>{v.note}</InfoLine>}
        </div>
      ))}
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/*  Composant principal                                                       */
/* -------------------------------------------------------------------------- */

interface Props {
  angle: AngleResources;          // données d’un angle
  language?: "en" | "fr";         // UI lang (défaut = angleResources)
}

const AngleCard: React.FC<Props> = ({ angle, language }) => {
  const lang = language ?? ("en" as "en" | "fr");

  return (
    <Card className="shadow-lg rounded-2xl">
      <CardContent className="p-6 space-y-5">
        {/* Titre + description ------------------------------------------------ */}
        <div className="space-y-1">
          <h3 className="text-xl font-bold">{angle.title}</h3>
          <p className="text-sm text-gray-700 whitespace-pre-line">{angle.description}</p>

          <Badges items={angle.keywords} />
        </div>

        {/* Sections ---------------------------------------------------------- */}
        <DatasetList list={angle.datasets} lang={lang} />
        <SourceList  list={angle.sources}  lang={lang} />
        <VizList     list={angle.visualizations} lang={lang} />
      </CardContent>
    </Card>
  );
};

export default AngleCard;
