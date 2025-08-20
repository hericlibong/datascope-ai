import { Fragment } from "react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import BadgePill from "@/components/results/BadgePill"; // existe déjà (créé plus tôt)
import type { AngleResources } from "@/types/analysis";

function SubCard({
  title,
  children,
  accent = "indigo",
  hint,
}: {
  title: string;
  children: React.ReactNode;
  hint?: string;
  accent?: "indigo" | "sky" | "emerald" | "amber";
}) {
  const border =
    accent === "emerald" ? "border-l-emerald-400"
    : accent === "amber" ? "border-l-amber-400"
    : accent === "sky" ? "border-l-sky-400"
    : "border-l-indigo-400";

  const chip =
    accent === "emerald" ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
    : accent === "amber" ? "border-amber-400/30 bg-amber-500/10 text-amber-200"
    : accent === "sky" ? "border-sky-400/30 bg-sky-500/10 text-sky-200"
    : "border-indigo-400/30 bg-indigo-500/10 text-indigo-200";

  return (
    <div className={`rounded-xl border border-white/10 bg-white/[0.06] p-4 ${border} border-l-4`}>
      <div className="mb-2 flex items-center justify-between gap-3">
        <div>
          <div className="text-[11px] uppercase tracking-widest text-white/60">Section</div>
          <h4 className="text-base md:text-lg font-semibold text-white">{title}</h4>
        </div>
        {hint ? <BadgePill className={`${chip}`}>{hint}</BadgePill> : null}
      </div>
      <div className="text-sm text-white/90">{children}</div>
    </div>
  );
}

function LinkLine({ href, label, description }: { href?: string; label: React.ReactNode; description?: string }) {
  const content = (
    <div className="flex flex-col">
      <span className="font-medium underline decoration-white/20 underline-offset-4 hover:decoration-white/40">
        {label}
      </span>
      {description ? <span className="text-xs text-white/70">{description}</span> : null}
    </div>
  );
  return (
    <li className="rounded-lg border border-white/10 bg-white/[0.04] p-3 hover:bg-white/[0.06] transition">
      {href ? (
        <a href={href} target="_blank" rel="noreferrer" className="block">{content}</a>
      ) : content}
    </li>
  );
}

export default function AngleCard({
  angle,
  language,
}: {
  angle: AngleResources;
  language: "fr" | "en";
}) {
  const t = (fr: string, en: string) => (language === "fr" ? fr : en);

  // Normalisation souple des champs pour coller à l’existant
  const title = (angle as any)?.title ?? (angle as any)?.name ?? t("Angle sans titre", "Untitled angle");
  const description = (angle as any)?.description ?? (angle as any)?.summary ?? "";
  const datasets: Array<any> = (angle as any)?.datasets ?? (angle as any)?.dataset_list ?? [];
  const sources: Array<any> =
    (angle as any)?.open_data_sources ?? (angle as any)?.other_portals ?? (angle as any)?.sources ?? [];

  // Type local pour une visualisation normalisée
  type VizNormalized = {
    title: string;
    chart_type?: string;
    note?: string;
    url?: string;
  };

  // SOURCE tolérante : la donnée arrive parfois sous `visualizations` (format objet),
  // parfois sous `viz_suggestions` (string ou objet).
  const rawViz: any[] = Array.isArray((angle as any)?.visualizations)
    ? (angle as any).visualizations
    : Array.isArray((angle as any)?.viz_suggestions)
    ? (angle as any).viz_suggestions
    : [];

  // Normalisation : on garde exactement les clés qui t'intéressent (chart_type, title, note)
  const vizNorm: VizNormalized[] = rawViz.map((v: any, i: number) => {
    if (typeof v === "string") {
      return { title: v };
    }
    return {
      title:
        v?.title ??
        v?.name ??
        (language === "fr" ? `Viz ${i + 1}` : `Viz ${i + 1}`),
      chart_type:
        v?.chart_type ?? v?.type ?? v?.viz_type ?? v?.chart ?? v?.kind ?? undefined,
      note:
        v?.note ?? v?.description ?? v?.desc ?? v?.details ?? undefined,
      url: v?.url ?? v?.link ?? v?.href ?? undefined,
    };
  });

  return (
    <article className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
      {/* A) Titre + intro */}
      <div className="mb-5">
        <div className="text-[11px] uppercase tracking-widest text-white/60">{t("Édito", "Edito")}</div>
        <h3 className="text-lg md:text-xl font-bold">{title}</h3>
        {description ? <p className="mt-2 text-sm text-white/80 leading-relaxed">{description}</p> : null}
      </div>

      <div className="grid gap-4">
        {/* B) Jeux de données — conserve les collapses */}
        <SubCard
          title={t("Jeux de données", "Datasets")}
          hint={datasets?.length ? `${datasets.length}` : undefined}
          accent="sky"
        >
          {datasets?.length ? (
            <Accordion type="single" collapsible className="w-full">
              {datasets.map((ds: any, i: number) => {
                const dsTitle = ds?.title ?? ds?.name ?? t(`Jeu de données ${i + 1}`, `Dataset ${i + 1}`);
                const dsDesc = ds?.description ?? ds?.desc ?? "";
                const dsUrl = ds?.url ?? ds?.link ?? ds?.href;
                const provider = ds?.provider ?? ds?.source ?? ds?.org;

                return (
                  <AccordionItem value={`ds-${i}`} key={`ds-${i}`} className="border-white/10">
                    <AccordionTrigger className="px-3 py-2 text-left hover:bg-white/[0.05]">
                      <div className="flex flex-col gap-0.5">
                        <span className="font-semibold text-sky-300">{dsTitle}</span>
                        {provider ? (
                          <span className="text-[11px] text-white/60">
                            {t("Source", "Source")}: {provider}
                          </span>
                        ) : null}
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-3 pb-3 space-y-3">
                      {(() => {
                        // ---------- Extraction tolérante ----------
                        const fullDesc =
                          ds?.long_description ??
                          ds?.description ??
                          ds?.notes ??
                          ds?.abstract ??
                          "";

                        const provider = ds?.provider ?? ds?.source ?? ds?.org ?? ds?.organization ?? ds?.owner;
                        const foundBy = ds?.found_by ?? ds?.connector ?? ds?.origin;

                        const dsUrl =
                          ds?.url ?? ds?.link ?? ds?.href ?? ds?.page ?? (Array.isArray(ds?.resources) ? ds.resources.find((r: any) => r?.url)?.url : undefined);

                        const license = ds?.license ?? ds?.licence ?? ds?.licencia ?? ds?.licence_name;
                        const updated = ds?.last_updated ?? ds?.updated ?? ds?.modified ?? ds?.metadata_modified ?? ds?.date_modified;

                        // formats: string | string[] | resources[].format/mime/type
                        const formatsRaw: any[] = [];
                        if (ds?.formats) formatsRaw.push(...(Array.isArray(ds.formats) ? ds.formats : [ds.formats]));
                        if (ds?.format) formatsRaw.push(ds.format);
                        if (Array.isArray(ds?.resources)) {
                          ds.resources.forEach((r: any) => {
                            if (r?.format) formatsRaw.push(r.format);
                            if (r?.mime) formatsRaw.push(r.mime);
                            if (r?.type) formatsRaw.push(r.type);
                          });
                        }
                        const formats = [...new Set(formatsRaw.filter(Boolean).map((f) => String(f).toLowerCase()))];

                        let host: string | null = null;
                        try {
                          if (dsUrl) host = new URL(dsUrl).hostname;
                        } catch (_) {
                          host = null;
                        }

                        return (
                          <>
                            {/* Description longue – jamais tronquée */}
                            {fullDesc && (
                              <div className="prose prose-invert max-w-none text-white/90 whitespace-pre-line leading-relaxed">
                                {fullDesc}
                              </div>
                            )}

                            {/* Métadonnées rapides */}
                            {(foundBy || provider || license || updated) && (
                              <div className="grid gap-2 text-sm">
                                {foundBy && (
                                  <div>
                                    <span className="text-white/60">{language === "fr" ? "Trouvé par" : "Found by"}: </span>
                                    <span className="font-medium">{foundBy}</span>
                                  </div>
                                )}
                                {provider && (
                                  <div>
                                    <span className="text-white/60">{language === "fr" ? "Source" : "Source"}: </span>
                                    <span className="font-medium">{provider}</span>
                                  </div>
                                )}
                                {license && (
                                  <div>
                                    <span className="text-white/60">{language === "fr" ? "Licence" : "License"}: </span>
                                    <span className="font-medium">{license}</span>
                                  </div>
                                )}
                                {updated && (
                                  <div>
                                    <span className="text-white/60">{language === "fr" ? "Dernière mise à jour" : "Last updated"}: </span>
                                    <span className="font-medium">{updated}</span>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Lien */}
                            {dsUrl && (
                              <div className="text-sm">
                                <span className="text-white/60 mr-1">{language === "fr" ? "Lien" : "Link"}:</span>
                                <a
                                  href={dsUrl}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="inline-flex items-center rounded-lg border border-sky-400/30 bg-sky-500/10 px-3 py-1.5 text-xs text-sky-200 hover:bg-sky-500/15"
                                >
                                  {host ?? dsUrl}
                                </a>
                              </div>
                            )}

                            {/* Formats */}
                            {formats.length > 0 && (
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="text-sm text-white/60">{language === "fr" ? "Formats" : "Formats"}:</span>
                                {formats.map((fmt) => (
                                  <span
                                    key={fmt}
                                    className="inline-flex items-center rounded-full border border-white/10 bg-white/10 px-2 py-0.5 text-[11px] font-semibold text-white/80"
                                  >
                                    {fmt}
                                  </span>
                                ))}
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          ) : (
            <div className="text-sm text-white/60">{t("Aucun jeu de données proposé.", "No datasets suggested.")}</div>
          )}
        </SubCard>

        {/* C) Autres portails open‑data */}
        <SubCard
          title={t("Autres portails open‑data", "Other open data portals")}
          hint={sources?.length ? `${sources.length}` : undefined}
          accent="emerald"
        >
          {sources?.length ? (
            <ul className="grid gap-2">
              {sources.map((s: any, i: number) => (
              <LinkLine
                key={`src-${i}`}
                href={s?.url ?? s?.link ?? s?.href}
                label={
                <span className="text-emerald-300">{s?.title ?? s?.name ?? t(`Ressource ${i + 1}`, `Resource ${i + 1}`)}</span>
                }
                description={s?.description ?? s?.desc}
              />
              ))}
            </ul>
          ) : (
            <div className="text-sm text-white/60">{t("Aucun portail listé.", "No portals listed.")}</div>
          )}
        </SubCard>

        {/* D) Visualisations possibles */}
        <SubCard title={language === "fr" ? "Visualisations possibles" : "Possible visualizations"} accent="amber">
          {vizNorm.length ? (
            <ul className="space-y-2">
              {vizNorm.map((v, i) => (
                <li
                  key={`viz-${i}`}
                  className="rounded-lg border border-white/10 bg-white/[0.04] p-3 leading-relaxed"
                >
                  {/* Ligne titre + type */}
                  <div className="flex items-start justify-between gap-3">
                    <span className="font-medium text-white/90">
                      {v.chart_type ? <strong className="mr-2 text-amber-300">{v.chart_type}</strong> : null}
                        <span className="text-amber-300">{v.title}</span>
                    </span>
                  </div>

                  {/* Description/note — jamais tronquée */}
                  {v.note ? (
                    <p className="mt-1 text-sm text-white/70 whitespace-pre-line">
                      {v.note}
                    </p>
                  ) : null}

                  {/* Lien optionnel */}
                  {v.url ? (
                    <a
                      href={v.url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-flex items-center rounded-lg border border-amber-400/30 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-200 hover:bg-amber-500/15"
                    >
                      {language === "fr" ? "Voir un exemple" : "View example"}
                    </a>
                  ) : null}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-sm text-white/60">
              {language === "fr" ? "Aucune suggestion de visualisation." : "No visualization suggestion."}
            </div>
          )}
        </SubCard>


      </div>
    </article>
  );
}
