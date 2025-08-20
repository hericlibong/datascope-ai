// REPLACE the entire file `src/components/results/EntitiesSummaryCard.tsx` with:

import { useMemo, useState } from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";

type Entity =
  | { type?: string; label?: string; category?: string }
  | Record<string, any>;

export function EntitiesSummaryCard({
  entities,
  language,
  defaultOpen = true,
}: {
  entities: Entity[] | Record<string, number>;
  language: "fr" | "en";
  defaultOpen?: boolean;
}) {
  // --- Helpers --------------------------------------------------------------
  const t = (fr: string, en: string) => (language === "fr" ? fr : en);

  function normalizeType(e: Entity): string {
    const raw =
      (e as any)?.type ||
      (e as any)?.label ||
      (e as any)?.category ||
      (typeof e === "string" ? e : "");

    const s = String(raw).toLowerCase();

    if (/(person|pers|human|people|per|pers\.)/.test(s)) return "persons";
    if (/(org|organisation|organization|company|inst|agency)/.test(s)) return "orgs";
    if (/(loc|place|city|country|geo)/.test(s)) return "locations";
    if (/(date|time)/.test(s)) return "dates";
    if (/(number|unit|measure|num|qty)/.test(s)) return "numbers";
    return "others";
  }

  // Accept either an array of items or a summary object { persons: n, ... }
  const summary = useMemo(() => {
    const base = { persons: 0, orgs: 0, locations: 0, numbers: 0, dates: 0, others: 0 };

    if (Array.isArray(entities)) {
      for (const e of entities) {
        const k = normalizeType(e) as keyof typeof base;
        base[k] += 1;
      }
      return base;
    }

    // object-like
    const obj = entities as Record<string, number>;
    return {
      persons: obj.persons ?? obj.people ?? obj.PER ?? obj.PERSON ?? obj.Persons ?? 0,
      orgs: obj.orgs ?? obj.organizations ?? obj.ORG ?? obj.Organizations ?? 0,
      locations: obj.locations ?? obj.LOC ?? obj.location ?? 0,
      numbers: obj.numbers ?? obj.units ?? obj.quantities ?? 0,
      dates: obj.dates ?? obj.time ?? 0,
      others: obj.others ?? obj.misc ?? 0,
    };
  }, [entities]);

  const total =
    summary.persons +
    summary.orgs +
    summary.locations +
    summary.numbers +
    summary.dates +
    summary.others;

  const rows: Array<{ label: string; key: keyof typeof summary }> = [
    { label: t("Personnes", "Persons"), key: "persons" },
    { label: t("Organisations", "Organizations"), key: "orgs" },
    { label: t("Lieux", "Locations"), key: "locations" },
    { label: t("Nombres + Unités", "Numbers + Units"), key: "numbers" },
    { label: t("Dates", "Dates"), key: "dates" },
    { label: t("Autres", "Others"), key: "others" },
  ];

  const [open, setOpen] = useState<boolean>(defaultOpen);

  // --- UI -------------------------------------------------------------------
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm">
      <Collapsible open={open} onOpenChange={setOpen}>
        {/* Header (comme la carte précédente) */}
        <CollapsibleTrigger asChild>
          <div
            role="button"
            aria-expanded={open}
            className="
              w-full cursor-pointer select-none px-6 py-4
              flex items-center justify-between gap-3
              hover:bg-white/[0.06] transition
            "
          >
            <div className="flex items-center gap-2">
              <span className="text-white/70"></span>
              <div>
                <div className="text-[11px] uppercase tracking-widest text-white/60">
                  {t("Analyse", "Analysis")}
                </div>
                <h3 className="text-xl font-semibold text-white/95">
                  {t("Entités & Thèmes", "Entities & Themes")}
                </h3>
              </div>

              {/* Badge total */}
              <span className="ml-3 rounded-full border border-white/10 bg-white/10 px-2 py-0.5 text-[11px] text-white/70">
                {total} {t("au total", "total")}
              </span>
            </div>

            <ChevronDown
              className={`h-5 w-5 text-white/70 transition-transform ${
                open ? "rotate-180" : ""
              }`}
              aria-hidden="true"
            />
          </div>
        </CollapsibleTrigger>

        {/* Contenu */}
        <CollapsibleContent className="px-6 pb-6 pt-0">
          <div className="mt-2 border-t border-white/10 rounded-xl overflow-hidden">
            {/* Table style dark harmonisé */}
            <div className="grid grid-cols-[1fr,120px] text-sm">
              {/* Header row */}
              <div className="col-span-2 bg-white/[0.03] px-4 py-3 flex items-center font-medium">
                <div className="flex-1 text-white/80">{t("Type d’entité", "Entity type")}</div>
                <div className="w-[120px] text-right text-white/80">{t("Nombre", "Count")}</div>
              </div>

              {/* Data rows */}
              {rows.map((r, i) => {
                const val = summary[r.key] ?? 0;
                return (
                  <div
                    key={r.key as string}
                    className={`
                      col-span-2 px-4 py-3 flex items-center
                      ${i % 2 === 0 ? "bg-white/[0.02]" : "bg-white/[0.04]"}
                      border-t border-white/5
                    `}
                  >
                    <div className="flex-1">{r.label}</div>
                    <div className="w-[120px] text-right">
                      <span
                        className="
                          inline-flex min-w-[28px] items-center justify-center
                          rounded-full bg-pink-500/20 text-pink-200
                          border border-pink-400/30 px-2 py-0.5 text-xs font-semibold
                        "
                      >
                        {val}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}

export default EntitiesSummaryCard;
