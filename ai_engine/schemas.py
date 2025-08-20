# ai_engine/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class DatasetSuggestion(BaseModel):
    title: str
    description: str | None = None
    source_name: str                  # "data.gouv.fr", "eurostat", etc.
    source : str = Field(alias="source_name")
    source_url: str                  # lien vers le dataset
    link: str = Field(alias="source_url") 
    formats: list[str] = []
    organization: str | None = None
    license: str | None = None
    last_modified: str | None = None    # ← nouveau
    richness: int = 0
    found_by: str | None = None        # "LLM" or "CONNECTOR"
    angle_idx: int | None = None       # ← nouveau 

class NumberEntity(BaseModel):
    raw: str = Field(..., description="Nombre tel qu'il apparaît dans le texte")
    value: Optional[float] = Field(None, description="Valeur numérique normalisée si possible")
    unit: Optional[str] = Field(None, description="Unité ou symbole (%) / (€) / (kg)")

class ExtractionResult(BaseModel):
    language: str = Field(..., description="fr ou en")
    persons: List[str]
    organizations: List[str]
    locations: List[str]
    themes: List[str]             # thèmes/sujets principaux de l'article
    dates: List[str]              # idéalement YYYY-MM-DD ou ISO partial
    numbers: List[NumberEntity]

# --- déjà présent au-dessus ---
class Angle(BaseModel):
    title: str = Field(..., description="Titre court (≤80 car.)")
    rationale: str = Field(..., description="1-2 phrases expliquant l’angle")

class AngleResult(BaseModel):
    language: str
    angles: List[Angle]

class AnalysisPackage(BaseModel):
    extraction: ExtractionResult
    angles: AngleResult

class KeywordSet(BaseModel):
    angle_title: str
    keywords: List[str]  # exactement 5

class KeywordsResult(BaseModel):
    language: str
    sets: List[KeywordSet]  # 1 par angle d’entrée

class VizSuggestion(BaseModel):
    title: str
    chart_type: str  # line, bar, pie, choropleth, table
    x: str
    y: str
    note: Optional[str] = None

class VizResult(BaseModel):
    language: str
    suggestions: List[VizSuggestion]

class LLMSourceSuggestion(BaseModel):
    title: str
    description: str
    link: str
    source: str   # portail ou organisme
    angle_idx: int 

class LLMSourceSuggestionList(BaseModel):
    datasets: list[LLMSourceSuggestion]

class AngleResources(BaseModel):
    index: int
    title: str
    description: str
    keywords: List[str]
    datasets: List[DatasetSuggestion]
    sources: List[LLMSourceSuggestion]
    visualizations: List[VizSuggestion]






