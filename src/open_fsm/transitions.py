from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from .typing import DictStrAny, StateValue


@dataclass
class Transition:
    method: Callable[..., Any]
    source: StateValue
    target: StateValue
    on_error: StateValue | Callable[..., None] = None
    conditions: Iterable[Callable[..., bool]] | None = None
    label: str | None = None
    properties: DictStrAny | None = None
