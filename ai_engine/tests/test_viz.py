from ai_engine.schemas import AngleResult, Angle, VizResult
import ai_engine.chains.viz as vz

def _angle():
    return AngleResult(language="en",
                       angles=[Angle(title="Global CO2 emissions 1960-2024",
                                     rationale="…")])

class Fake:
    def invoke(self, _):
        return VizResult(language="en",
                         suggestions=[{
                            "title": "CO2 emissions worldwide (1960-2024)",
                            "chart_type": "line",
                            "x": "Year",
                            "y": "CO2 (Mt)",
                            "note": "Units: million tonnes"
                         }])

def test_viz_suggestion(monkeypatch):
    monkeypatch.setattr(vz, "run", lambda angle_res: Fake().invoke(None))
    res = vz.run(_angle())
    s = res.suggestions[0]
    assert s.chart_type in {"line","bar","pie","area","choropleth","table"}
    assert s.title
    assert s.x and s.y
