from ai_engine.schemas import ExtractionResult, AngleResult, AnalysisPackage

def format_markdown(extraction: ExtractionResult, angles: AngleResult) -> str:
    """Retourne un texte markdown lisible regroupant les entités et les angles."""
    lines = [f"# Résultat d’analyse", "", "## Entités extraites"]
    lines.append(f"- **Langue** : {extraction.language}")

    if extraction.persons:
        lines.append(f"- **Personnes** : {', '.join(extraction.persons)}")
    if extraction.organizations:
        lines.append(f"- **Organisations** : {', '.join(extraction.organizations)}")
    if extraction.locations:
        lines.append(f"- **Lieux** : {', '.join(extraction.locations)}")
    if extraction.dates:
        lines.append(f"- **Dates** : {', '.join(extraction.dates)}")
    if extraction.numbers:
        nums = [
            f"{n.raw} ({n.value} {n.unit})" if n.value else n.raw
            for n in extraction.numbers
        ]
        lines.append(f"- **Valeurs numériques** : {', '.join(nums)}")

    lines.append("\n## Suggestions d’angles\n")
    for idx, angle in enumerate(angles.angles, 1):
        lines.append(f"### {idx}. {angle.title}\n{angle.rationale}\n")

    return "\n".join(lines)


def package(extraction: ExtractionResult, angles: AngleResult) -> tuple[AnalysisPackage, str]:
    """Retourne (objet JSON consolidé, markdown formaté)."""
    return AnalysisPackage(extraction=extraction, angles=angles), format_markdown(extraction, angles)
