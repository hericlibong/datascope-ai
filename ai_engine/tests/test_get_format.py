from ai_engine.connectors.format_utils import get_format

# Définition d’un ensemble de formats valides pour les tests
VALID_FORMATS = {"csv", "json", "xml", "geojson"}

def test_get_format_handles_none():
    res = {"format": None, "mimetype": None, "url": None}
    assert get_format(res, VALID_FORMATS) is None

def test_get_format_from_extension():
    res = {"format": None, "url": "https://example.com/data.geojson"}
    assert get_format(res, VALID_FORMATS) == "geojson"
