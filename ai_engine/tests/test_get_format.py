# ai_engine/tests/test_get_format.py
from ai_engine.connectors.data_gouv import get_format

def test_get_format_handles_none():
    res = {"format": None, "mimetype": None, "url": None}
    assert get_format(res) is None

def test_get_format_from_extension():
    res = {"format": None, "url": "https://example.com/data.geojson"}
    assert get_format(res) == "geojson"
