# ai_engine/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field

class NumberEntity(BaseModel):
    raw: str = Field(..., description="Nombre tel qu'il apparaît dans le texte")
    value: Optional[float] = Field(None, description="Valeur numérique normalisée si possible")
    unit: Optional[str] = Field(None, description="Unité ou symbole (%) / (€) / (kg)")

class ExtractionResult(BaseModel):
    language: str = Field(..., description="fr ou en")
    persons: List[str]
    organizations: List[str]
    locations: List[str]
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

