from typing import Any, Iterable, List, Mapping

from pydantic import NonNegativeInt

from models.merge import MergeIndex, MergeMode, MergeStrategy
from models.partition import JSONish


def _merge_value(old: Any, new: Any, mode: MergeMode = MergeMode.UPDATE) -> Any:
    if new is None:
        return old

    if mode == MergeMode.UPDATE:
        return new
    elif mode == MergeMode.ADDITIVE:
        return old + new
    elif mode == MergeMode.SUBTRACT:
        return old - new


# TODO: Merging for iterables and with indexes, also strings
# Might need option for multiple indexes...?
def _merge_iterable(
    old: Iterable, new: Iterable, index: NonNegativeInt, mode: MergeMode = MergeMode.UPDATE
) -> List[Any]:
    if new is None:
        return old

    if mode == MergeMode.ADDITIVE:
        return old[:index] + new + old[index:]
    elif mode == MergeMode.SUBTRACT:
        return [item for item in old if item not in new]
    elif mode == MergeMode.UPDATE:
        return new


def _merge_mapping(
    old: JSONish, new: JSONish, index: MergeIndex = None, merge: MergeStrategy = None, mode=MergeMode.UPDATE
) -> JSONish:
    if not new:
        return old
    if not index:
        index = {}
    if not merge:
        merge = {}

    for k, v in old.items():
        if isinstance(v, Mapping):
            new[k] = _merge_mapping(v, new.get(k, {}), index.get(k, {}), merge.get(k, {}), merge.get(k, mode))
        elif isinstance(v, Iterable):
            new[k] = _merge_iterable(v, new.get(k, []), index.get(k, len(v)), merge.get(k, mode))
        else:
            new[k] = _merge_value(new.get(k, None), v, merge.get(k, mode))
    return new
