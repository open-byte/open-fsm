from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any

from typing_extensions import Self

from open_fsm.exceptions import TransitionNotAllowed
from open_fsm.transitions import Transition

from .typing import DictStrAny, StateValue


class StateEnum(str, Enum):
    """
    A base class for state enumerations.
    This class can be used to define a set of valid states for a state machine.
    STATES:
        Any: Represents any state. This can be used as a wildcard to match any state.
        PLUS: Represents a special state that can be used to indicate a transition to any state except itself.
        Example usage:
        class MyStates(StateEnum):
            INITIAL = "initial"
            FINISHED = "finished"
        In this example, MyStates is a subclass of StateEnum that defines two valid states:
        INITIAL and FINISHED. You can use these states in your state machine to represent the current
        state of the system. The ANY and PLUS states can be used as wildcards in transition definitions.

    """

    ANY = '*'
    PLUS = '+'


INTERNAL_OPEN_FSM_STATE_FIELD = '_open_fsm_state_field'


@dataclass
class MethodMeta:
    transitions: dict[StateValue, Transition]
    state_field: StateField | None = None

    def get_transition(self, source: StateValue) -> Transition | None:
        transition = self.transitions.get(source, None)
        if transition is None:
            transition = self.transitions.get(StateEnum.ANY.value, None)
        if transition is None:
            transition = self.transitions.get(StateEnum.PLUS.value, None)
        return transition

    def has_transition(self, source: StateValue) -> bool:
        if source in self.transitions:
            return True
        if StateEnum.ANY.value in self.transitions:
            return True
        if StateEnum.PLUS.value in self.transitions and self.transitions[StateEnum.PLUS.value].source != source:
            return True
        return False

    def conditions_met(self, instance: object, state: StateValue) -> bool:
        """
        Check if all conditions have been met
        """
        transition = self.get_transition(state)

        if transition is None:
            return False

        elif transition.conditions is None:
            return True
        else:
            return all(condition(instance) for condition in transition.conditions)

    def next_state(self, current_state: StateValue) -> StateValue:
        transition = self.get_transition(current_state)

        if transition is None:
            raise TransitionNotAllowed(f'No transition from {current_state}')

        return transition.target

    def exception_state(self, current_state: StateValue) -> StateValue:
        transition = self.get_transition(current_state)

        if transition is None:
            raise TransitionNotAllowed(f'No transition from {current_state}')

        return transition.on_error

    def get_transition_from_source(self, source: StateValue) -> Transition | None:
        transition = self.transitions.get(source)
        if transition and transition.source == source:
            return transition
        return None

    def add_transition(self, transition: Transition) -> None:

        if transition.source in self.transitions:
            raise ValueError(f"A transition from source '{transition.source}' already exists.")

        self.transitions[transition.source] = transition


class StateField:
    def __init__(self, *, states: Any, default: StateValue = None) -> None:
        self.states = states
        self._internal_value = default
        self._name: str | None = None
        self._on_success_callbacks: list[Callable[..., Any]] | None = None

    # def __set_name__(self, instance_type: type[object], name: str) -> None:
    #     print(f'Setting name for StateField: {name}')
    #     self._name = name

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

    def _change_state(self, instance: object, method: Callable[..., Any], *args: Any, **kwargs: Any) -> None:

        method_meta: MethodMeta | None = getattr(method, INTERNAL_OPEN_FSM_STATE_FIELD, None)
        curren_state = self._internal_value
        if method_meta is None:
            raise ValueError(f"No transition metadata found for method '{method.__name__}'.")  # ty: ignore[unresolved-attribute]

        if not method_meta.has_transition(curren_state):
            raise TransitionNotAllowed(
                f"Cannot transition from state '{curren_state}' using method '{method.__name__}'."  # ty: ignore[unresolved-attribute]
            )

        if not method_meta.conditions_met(instance, curren_state):
            raise TransitionNotAllowed(
                f"Conditions not met for transitioning from state '{curren_state}' using method '{method.__name__}'."  # ty: ignore[unresolved-attribute]
            )

        next_state = method_meta.next_state(curren_state)

        try:
            result = method(instance, *args, **kwargs)
            ## Try to get_states

        except Exception as e:
            exception_state = method_meta.exception_state(curren_state)
            if exception_state is not None:
                self._internal_value = exception_state
            raise e

        else:
            self._internal_value = next_state
            if self._on_success_callbacks is not None:
                for callback in self._on_success_callbacks:
                    callback(instance, *args, **kwargs)

        return result

    def transition(
        self,
        source: StateValue | Iterable[StateValue],
        target: StateValue,
        on_error: StateValue | Callable[..., None] = None,
        conditions: Iterable[Callable[..., bool]] | Callable[..., bool] | None = None,
        label: str | None = None,
        properties: DictStrAny | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:

            method_meta = getattr(func, INTERNAL_OPEN_FSM_STATE_FIELD, None)

            if method_meta is None:
                method_meta = MethodMeta(
                    transitions={},
                    state_field=self,
                )
                setattr(func, INTERNAL_OPEN_FSM_STATE_FIELD, method_meta)

                @wraps(func)
                def inner(instance: Self, *args: Any, **kwargs: Any) -> Any:
                    return self._change_state(instance, func, *args, **kwargs)

                result = inner
            else:
                result = func

            sources = source if isinstance(source, (list, tuple, set)) else (source,)

            normalized_conditions: tuple[Callable[..., bool], ...] | None = None

            if conditions is not None:
                if isinstance(conditions, Callable):
                    normalized_conditions = (conditions,)
                elif isinstance(conditions, Iterable):
                    normalized_conditions = tuple(conditions)
                else:
                    raise ValueError('Conditions must be a callable or an iterable of callables.')

            for _source in sources:
                method_meta.add_transition(
                    Transition(
                        method=func,
                        source=_source,
                        target=target,
                        on_error=on_error,
                        conditions=normalized_conditions,
                        label=label,
                        properties=properties,
                    )
                )

            return result

        return wrapper

    def on_success(self) -> Callable[..., Any]:
        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            if self._on_success_callbacks is None:
                self._on_success_callbacks = []
            self._on_success_callbacks.append(func)
            return func

        return wrapper
