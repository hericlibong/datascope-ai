from __future__ import annotations
from typing import Any, Callable, Optional
from ai_engine.url_utils import get_url

ConverterToDataset = Callable[[Any], Any]
ConverterToSource  = Callable[[Any], Any]


def rebalance_minima(
    datasets: list,
    sources: list,
    min_ds: int,
    min_src: int,
    is_dataset_like_url: Callable[[Optional[str]], bool],
    to_dataset: ConverterToDataset,
    to_source: ConverterToSource,
    logger=None,
) -> None:
    """
    Minimal balancing with **type-safe** moves between lists.
    - When moving from sources -> datasets: convert item using `to_dataset`
    - When moving from datasets -> sources: convert item using `to_source`
    Mutates lists in place. Keeps behavior intentionally simple.
    """
    moved_ds, moved_src = 0, 0

    def pop_index(predicate, items: list) -> int:
        for i, it in enumerate(items):
            u = get_url(it)
            if predicate(u):
                return i
        return -1

    # 1) Fill datasets from sources (prefer dataset-like in sources)
    while len(datasets) < min_ds and sources:
        i = pop_index(lambda u: is_dataset_like_url(u or ""), sources)
        if i < 0:
            break
        src_obj = sources.pop(i)
        datasets.append(to_dataset(src_obj))
        moved_ds += 1

    # 2) Fill sources from datasets (prefer source-like in datasets)
    while len(sources) < min_src and datasets:
        i = pop_index(lambda u: not is_dataset_like_url(u or ""), datasets)
        if i < 0:
            break
        ds_obj = datasets.pop(i)
        sources.append(to_source(ds_obj))
        moved_src += 1

    # 3) Fallbacks if still short and the other side has surplus
    while len(datasets) < min_ds and len(sources) > min_src:
        src_obj = sources.pop(0)
        datasets.append(to_dataset(src_obj))
        moved_ds += 1
    while len(sources) < min_src and len(datasets) > min_ds:
        ds_obj = datasets.pop(0)
        sources.append(to_source(ds_obj))
        moved_src += 1

    if (moved_ds or moved_src) and logger:
        logger.debug(
            f"min_guard_applied: datasets+{moved_ds}, sources+{moved_src}, "
            f"final_sizes={{'datasets': {len(datasets)}, 'sources': {len(sources)}}}"
        )