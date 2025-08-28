import pytest

from ai_engine.ranking import datasets_path_soft_boost, final_weight


class Dummy:
    def __init__(self, url: str):
        self.url = url


def _pick_url_for_weight(obj: Dummy) -> str:
    return obj.url


def _trust_weight_fn(u: str | None) -> float:
    # neutral (no trusted boost)
    return 1.0


def _homepage_weight_fn(u: str | None) -> float:
    # neutral (no homepage penalty)
    return 1.0


def _datasets_boost_fn(u: str | None, boost: float) -> float:
    return datasets_path_soft_boost(u, boost)


def test_datasets_path_soft_boost_basic():
    assert datasets_path_soft_boost("https://example.org/datasets/air", 0.05) == pytest.approx(1.05)
    assert datasets_path_soft_boost("https://example.org/about", 0.05) == pytest.approx(1.0)


def test_final_weight_prefers_datasets_path_when_boosted():
    a = Dummy("https://example.org/datasets/air-quality")
    b = Dummy("https://example.org/about")
    theme_w = {id(a): 1.0, id(b): 1.0}

    wa = final_weight(
        a,
        theme_w=theme_w,
        pick_url_for_weight=_pick_url_for_weight,
        trust_weight_fn=_trust_weight_fn,
        homepage_weight_fn=_homepage_weight_fn,
        datasets_path_boost_fn=lambda u: _datasets_boost_fn(u, 0.05),
    )
    wb = final_weight(
        b,
        theme_w=theme_w,
        pick_url_for_weight=_pick_url_for_weight,
        trust_weight_fn=_trust_weight_fn,
        homepage_weight_fn=_homepage_weight_fn,
        datasets_path_boost_fn=lambda u: _datasets_boost_fn(u, 0.05),
    )
    assert wa > wb

    # With zero boost, both should be equal (given all other factors are neutral)
    wa0 = final_weight(
        a,
        theme_w=theme_w,
        pick_url_for_weight=_pick_url_for_weight,
        trust_weight_fn=_trust_weight_fn,
        homepage_weight_fn=_homepage_weight_fn,
        datasets_path_boost_fn=lambda u: _datasets_boost_fn(u, 0.0),
    )
    wb0 = final_weight(
        b,
        theme_w=theme_w,
        pick_url_for_weight=_pick_url_for_weight,
        trust_weight_fn=_trust_weight_fn,
        homepage_weight_fn=_homepage_weight_fn,
        datasets_path_boost_fn=lambda u: _datasets_boost_fn(u, 0.0),
    )
    assert wa0 == pytest.approx(wb0)