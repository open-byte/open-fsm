from collections.abc import Callable, Iterable
from typing import Any

from .typing import DictStrAny, StateValue


class StateField:
    def __init__(self, *, states: Any, default: StateValue = None) -> None:
        self.states = states
        self._internal_value = default

    def __get__(self, instance: object, instance_type: type[object]) -> StateValue:
        if instance is None:
            return self
        return self._internal_value

    def __set__(self, instance: object, value: StateValue) -> None:
        # TODO:
        # Add validation logic here if needed
        # If Enum
        # if List, tuple, set, etc. check if value is in self.states
        self._internal_value = value

    def transition(
        self,
        source: StateValue,
        target: Iterable[StateValue] | StateValue,
        on_error: StateValue | Callable[..., None] = None,
        conditions: Iterable[Callable[..., bool]] | Callable[..., bool] | None = None,
        label: str | None = None,
        properties: DictStrAny | None = None,
    ) -> Any:
        # TODO: Missing validation logic for source and target states

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            def inner(*args: Any, **kwargs: Any) -> Any:
                print(f'Transitioning from {source} to {target}')

            return inner

        return wrapper
