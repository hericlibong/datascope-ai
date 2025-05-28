from ai_engine.schemas import ExtractionResult, AngleResult, Angle
from ai_engine.formatter import package

def test_package_outputs_both_json_and_md():
    extraction = ExtractionResult(
        language="fr",
        persons=["Emmanuel Macron"],
        organizations=["INSEE"],
        locations=["Paris"],
        dates=["2024-01-01"],
        numbers=[]
    )

    angle_result = AngleResult(
        language="fr",
        angles=[
            Angle(title="L’empreinte carbone oubliée", rationale="Une analyse des transports urbains trop peu documentée.")
        ]
    )

    packaged, md = package(extraction, angle_result)

    assert packaged.extraction.language == "fr"
    assert packaged.angles.angles[0].title.startswith("L’empreinte")
    assert "## Suggestions d’angles" in md
    assert "L’empreinte carbone oubliée" in md
